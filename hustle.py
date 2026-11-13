#!/usr/bin/env python3
"""ZERO DAY HUSTLE - a hacker-underground trading game for the terminal.

Run:  py hustle.py            (optional: --seed N for a repeatable run)
"""
import argparse
import json
import math
import os
import random
import sys
from pathlib import Path

DAYS = 30
START_CASH = 2000
START_DEBT = 5500
DEBT_RATE = 0.08      # the Syndicate's daily interest
WALLET_RATE = 0.03    # cold wallet daily yield
DEBT_LIMIT = 25000
START_DRIVE = 100
HEAT_DECAY = 8
MAX_PROXIES = 8
SCORES = Path(__file__).with_name("scores.json")

# name, low, high, news when scarce, news when flooded
GOODS = [
    ("Zero-Days", 15000, 29000,
     "Bug bounties are paying triple. Nobody is selling Zero-Days!",
     "A broker got doxxed and is fire-selling Zero-Days!"),
    ("Rootkits", 5000, 13000,
     "New kernel protections broke most Rootkits. Working ones cost a fortune!",
     "A rootkit crew leaked their own source. Rootkits are dirt cheap!"),
    ("Botnet Hours", 1500, 4400,
     "A big takedown wiped out half the bots. Botnet Hours are scarce!",
     "Millions of cheap smart cameras just came online. Botnet Hours are flooding in!"),
    ("Leaked Databases", 1000, 3500,
     "Everyone rotated their passwords. Fresh Leaked Databases are gold!",
     "A mega-breach dropped overnight. Leaked Databases everywhere!"),
    ("Phishing Kits", 600, 1300,
     "Tax season! Phishing Kits are selling out!",
     "Mail filters got smarter. Nobody wants Phishing Kits!"),
    ("Rogue APs", 300, 900,
     "A big conference is in town. Rogue APs are in demand!",
     "A hardware shop is clearing out Rogue APs!"),
    ("Cracked Accounts", 200, 700,
     "Streaming prices went up again. Cracked Accounts are hot!",
     "A combo list went public. Cracked Accounts are nearly worthless!"),
    ("USB Droppers", 90, 250,
     "Customs seized a shipment. USB Droppers are hard to find!",
     "Somebody found a pallet of USB Droppers behind a warehouse!"),
    ("Burner SIMs", 30, 120,
     "New ID laws hit the kiosks. Burner SIMs are scarce!",
     "A carrier is dumping Burner SIMs by the box!"),
    ("Warez", 10, 60,
     "The big tracker went down. Warez prices are up!",
     "A release group dumped its whole archive. Warez are basically free!"),
]

LOCATIONS = [
    "The Hackerspace",   # home: Syndicate broker + cold wallet
    "Tor Bazaar",
    "IRC Backchannel",
    "Con Hallway",
    "Campus Lab",
    "Datacenter Dock",
    "Cyber Cafe",
    "Paste Alley",
]
HOME = LOCATIONS[0]

USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
if USE_COLOR and os.name == "nt":
    os.system("")  # switches the Windows console into ANSI mode


def c(code, s):
    return f"\033[{code}m{s}\033[0m" if USE_COLOR else s


def green(s):
    return c("92", s)


def red(s):
    return c("91", s)


def yellow(s):
    return c("93", s)


def cyan(s):
    return c("96", s)


def dim(s):
    return c("2", s)


def money(n):
    return f"-${-n:,}" if n < 0 else f"${n:,}"


def ask(prompt):
    try:
        return input(green(prompt)).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def ask_int(prompt, most):
    """Number from 1..most, or None. 'm' means the maximum."""
    raw = ask(prompt).lower().replace(",", "").replace("$", "")
    if not raw:
        return None
    if raw in ("m", "max", "all"):
        return most if most > 0 else None
    if not raw.isdigit():
        print(red(" That's not a number."))
        return None
    n = int(raw)
    if n <= 0:
        return None
    if n > most:
        print(red(f" Too many. The most you can do is {most:,}."))
        return None
    return n


class Game:
    def __init__(self):
        self.day = 1
        self.loc = HOME
        self.cash = START_CASH
        self.debt = START_DEBT
        self.wallet = 0
        self.drive = START_DRIVE
        self.opsec = 100
        self.heat = 0
        self.proxies = 0
        self.inv = {}    # name -> quantity
        self.cost = {}   # name -> average price paid
        self.prices = {}
        self.news = []
        self.over = False
        self.busted = False

    # ---------- helpers ----------
    def used(self):
        return sum(self.inv.values())

    def free(self):
        return self.drive - self.used()

    def add_items(self, name, qty, price):
        held = self.inv.get(name, 0)
        paid = self.cost.get(name, 0) * held + price * qty
        self.inv[name] = held + qty
        self.cost[name] = paid // (held + qty)

    def remove_items(self, name, qty):
        self.inv[name] -= qty
        if self.inv[name] <= 0:
            del self.inv[name]
            self.cost.pop(name, None)

    def add_heat(self, value):
        gain = min(15, value // 10000)
        if gain:
            self.heat = min(100, self.heat + gain)

    def roll_market(self):
        while True:
            self.prices, self.news = {}, []
            for name, low, high, scarce, flood in GOODS:
                if random.random() < 0.18:
                    continue  # nobody is dealing this here today
                price = random.randint(low, high)
                r = random.random()
                if r < 0.06:
                    price *= random.randint(3, 6)
                    self.news.append(scarce)
                elif r < 0.12:
                    price = max(1, price // random.randint(3, 5))
                    self.news.append(flood)
                self.prices[name] = price
            if len(self.prices) >= 4:
                return

    # ---------- screens ----------
    def show(self):
        line = "=" * 64
        print()
        print(green(line))
        final = yellow("   ** FINAL DAY - sell what you hold **") if self.day >= DAYS else ""
        print(f" DAY {self.day}/{DAYS}  @ {cyan(self.loc)}{final}")
        print(f" Cash {green(money(self.cash))}   Wallet {money(self.wallet)}   "
              f"Debt {red(money(self.debt)) if self.debt else money(0)}")
        heat = f"{self.heat}%"
        heat = red(heat) if self.heat >= 60 else yellow(heat) if self.heat >= 30 else heat
        opsec = f"{self.opsec}%"
        opsec = red(opsec) if self.opsec <= 35 else opsec
        print(f" Drive {self.used()}/{self.drive}   OpSec {opsec}   Heat {heat}   "
              f"Proxies {self.proxies}")
        print(green(line))
        for item in self.news:
            print(yellow(" >> " + item))
        print(dim("  #  Item                    Price     Held    Avg paid"))
        for i, good in enumerate(GOODS, 1):
            name = good[0]
            price = self.prices.get(name)
            held = self.inv.get(name, 0)
            ptxt = f"{money(price):>12}" if price else dim(f"{'no market':>12}")
            htxt = f"{held:>8,}" if held else f"{'-':>8}"
            atxt = f"{money(self.cost.get(name, 0)):>12}" if held else ""
            print(f" {i:>2}  {name:<17}{ptxt}{htxt}{atxt}")
        print()
        menu = " [B]uy  [S]ell  [T]unnel out  [L]ay low  [D]ump  [Q]uit"
        if self.loc == HOME:
            menu += "\n [K] Syndicate broker  [W] Cold wallet"
        print(menu)

    def pick_good(self, prompt):
        n = ask_int(prompt, len(GOODS))
        return GOODS[n - 1][0] if n else None

    def buy(self):
        name = self.pick_good(" Buy which #? ")
        if not name:
            return
        price = self.prices.get(name)
        if not price:
            print(red(f" Nobody is dealing {name} here today."))
            return
        if self.free() <= 0:
            print(red(" Your drive is full."))
            return
        most = min(self.cash // price, self.free())
        if most <= 0:
            print(red(f" You can't afford even one at {money(price)}."))
            return
        qty = ask_int(f" How many {name}? (max {most:,}, m = max) ", most)
        if not qty:
            return
        self.cash -= qty * price
        self.add_items(name, qty, price)
        self.add_heat(qty * price)
        print(f" Bought {qty:,} {name} for {money(qty * price)}.")

    def sell(self):
        name = self.pick_good(" Sell which #? ")
        if not name:
            return
        held = self.inv.get(name, 0)
        if not held:
            print(red(f" You aren't holding any {name}."))
            return
        price = self.prices.get(name)
        if not price:
            print(red(f" No buyers for {name} here today."))
            return
        qty = ask_int(f" How many {name}? (max {held:,}, m = max) ", held)
        if not qty:
            return
        profit = (price - self.cost.get(name, 0)) * qty
        self.cash += qty * price
        self.remove_items(name, qty)
        self.add_heat(qty * price)
        tag = green(f"+{money(profit)}") if profit >= 0 else red(money(profit))
        print(f" Sold {qty:,} {name} for {money(qty * price)}  ({tag} vs what you paid).")

    def dump(self):
        name = self.pick_good(" Dump which #? ")
        if not name:
            return
        held = self.inv.get(name, 0)
        if not held:
            print(red(f" You aren't holding any {name}."))
            return
        qty = ask_int(f" Wipe how many {name}? (max {held:,}, m = max) ", held)
        if qty:
            self.remove_items(name, qty)
            print(f" Securely wiped {qty:,} {name}.")

    def confirm_end(self):
        if self.used():
            print(yellow(" You are still holding goods. They count for nothing at the end."))
        if ask(" It's the final day. End the run and cash out? (y/n) ").lower().startswith("y"):
            self.over = True

    def travel(self):
        if self.day >= DAYS:
            self.confirm_end()
            return
        others = [l for l in LOCATIONS if l != self.loc]
        print()
        for i, l in enumerate(others, 1):
            note = dim("  (broker, cold wallet)") if l == HOME else ""
            print(f"  {i}  {l}{note}")
        n = ask_int(" Tunnel to which #? (takes a day) ", len(others))
        if not n:
            return
        self.loc = others[n - 1]
        self.next_day()
        if not self.over:
            self.random_event()

    def lay_low(self):
        if self.day >= DAYS:
            self.confirm_end()
            return
        if not ask(" Go dark for a day? Heat drops, OpSec recovers. (y/n) ").lower().startswith("y"):
            return
        self.next_day()
        self.heat = max(0, self.heat - 30)
        self.opsec = min(100, self.opsec + 10)
        print(dim(" You unplug everything and read paperbacks for a day."))

    def next_day(self):
        self.day += 1
        self.debt = math.ceil(self.debt * (1 + DEBT_RATE))
        self.wallet = int(self.wallet * (1 + WALLET_RATE))
        self.heat = max(0, self.heat - HEAT_DECAY)
        self.roll_market()

    def broker(self):
        print(f"\n The Syndicate's broker looks up. You owe {red(money(self.debt))} "
              f"(+{int(DEBT_RATE * 100)}% a day).")
        cmd = ask(" [P]ay down, [B]orrow, or Enter to leave: ").lower()[:1]
        if cmd == "p":
            most = min(self.cash, self.debt)
            if most <= 0:
                print(red(" Nothing to pay, or nothing to pay with."))
                return
            amt = ask_int(f" Pay how much? (max {money(most)}, m = max) ", most)
            if amt:
                self.cash -= amt
                self.debt -= amt
                print(" Paid." + (green(" You're clear with the Syndicate!") if not self.debt else ""))
        elif cmd == "b":
            most = DEBT_LIMIT - self.debt
            if most <= 0:
                print(red(" \"You're at your limit. Pay something back first.\""))
                return
            amt = ask_int(f" Borrow how much? (max {money(most)}, m = max) ", most)
            if amt:
                self.cash += amt
                self.debt += amt
                print(" \"Don't make us come looking for you.\"")

    def cold_wallet(self):
        print(f"\n Cold wallet balance: {money(self.wallet)} "
              f"(+{int(WALLET_RATE * 100)}% a day, safe from phishing).")
        cmd = ask(" [D]eposit, [W]ithdraw, or Enter to leave: ").lower()[:1]
        if cmd == "d":
            amt = ask_int(f" Deposit how much? (max {money(self.cash)}, m = max) ", self.cash)
            if amt:
                self.cash -= amt
                self.wallet += amt
        elif cmd == "w":
            amt = ask_int(f" Withdraw how much? (max {money(self.wallet)}, m = max) ", self.wallet)
            if amt:
                self.wallet -= amt
                self.cash += amt

    # ---------- events ----------
    def random_event(self):
        if random.random() < min(0.45, 0.07 + self.heat / 300):
            self.trace()
            return
        r = random.random()
        if r < 0.10:
            name, low, high = random.choice(GOODS[3:])[:3]
            qty = min(random.randint(2, 8), self.free())
            if qty > 0:
                self.add_items(name, qty, 0)
                print(cyan(f"\n ** You find an unlocked laptop in a ride share: {qty} {name}! **"))
        elif r < 0.18:
            price = random.randint(400, 1200) * (1 + self.day // 8)
            if self.cash >= price:
                print(cyan(f"\n ** A hardware hacker offers an encrypted drive upgrade "
                           f"(+50 slots) for {money(price)}. **"))
                if ask(" Buy it? (y/n) ").lower().startswith("y"):
                    self.cash -= price
                    self.drive += 50
        elif r < 0.27:
            price = random.randint(700, 1500) * (1 + self.proxies)
            if self.cash >= price and self.proxies < MAX_PROXIES:
                print(cyan(f"\n ** A sysadmin with a grudge will sell you a proxy chain for "
                           f"{money(price)}. **"))
                print(dim("    Proxies help you slip traces and let you counter-hack."))
                if ask(" Buy it? (y/n) ").lower().startswith("y"):
                    self.cash -= price
                    self.proxies += 1
        elif r < 0.33:
            if self.cash > 100:
                loss = self.cash * random.randint(10, 25) // 100
                self.cash -= loss
                print(red(f"\n ** You clicked a link. YOU. Someone drained {money(loss)} "
                          f"from your hot wallet. **"))
        elif r < 0.40:
            if self.opsec < 100:
                price = (100 - self.opsec) * random.randint(20, 45)
                if self.cash >= price:
                    print(cyan(f"\n ** An old-timer offers a full OpSec audit for {money(price)}. **"))
                    if ask(" Pay for it? (y/n) ").lower().startswith("y"):
                        self.cash -= price
                        self.opsec = 100

    def trace(self):
        n = total = random.randint(1, 2 + self.day // 8)
        crew = "alone" if n == 1 else f"with {n - 1} analyst{'s' if n > 2 else ''}"
        print(red(f"\n !! TRACE DETECTED !!  Agent Null is on your connection, {crew}."))
        while True:
            print(f" Tracers: {n}   OpSec: {self.opsec}%   Proxies: {self.proxies}")
            opts = " [R]un  [W]ipe drive (lose all goods, sure escape)"
            if self.proxies:
                opts += "  [C]ounter-hack"
            print(opts)
            cmd = ask(" > ").lower()[:1]
            if cmd == "r":
                chance = max(0.25, min(0.85, 0.55 + 0.05 * self.proxies - 0.07 * (n - 1)))
                if random.random() < chance:
                    self.heat = max(0, self.heat - 10)
                    print(green(" You hop three networks and vanish."))
                    return
                print(" They're still on you.")
            elif cmd == "w":
                self.inv.clear()
                self.cost.clear()
                self.heat //= 2
                print(yellow(" You nuke the drive. Nothing left to find. The trace goes cold."))
                return
            elif cmd == "c" and self.proxies:
                hits = min(n, sum(random.random() < 0.4 for _ in range(self.proxies)))
                n -= hits
                print(f" You fire back through your proxies... {hits} tracer{'s' if hits != 1 else ''} knocked offline.")
                if n <= 0:
                    loot = total * random.randint(400, 1500) * (1 + self.day // 10)
                    self.cash += loot
                    self.heat = max(0, self.heat - 25)
                    print(green(f" Trace dead. You sell their own tooling for {money(loot)}."))
                    return
            else:
                continue
            dmg = sum(random.randint(3, 9) for _ in range(n) if random.random() < 0.35)
            if dmg:
                self.opsec -= dmg
                print(red(f" They unmask part of your trail. OpSec -{dmg}%."))
            else:
                print(dim(" Their probes miss."))
            if self.opsec <= 0:
                self.opsec = 0
                self.busted = self.over = True
                return

    # ---------- flow ----------
    def run(self):
        print(green(r"""
  ____  ____  ____   __     ____   __   _  _
 (__  )(  __)(  _ \ /  \   (    \ / _\ ( \/ )
  / _/  ) _)  )   /(  O )   ) D (/    \ )  /
 (____)(____)(__\_) \__/   (____/\_/\_/(__/
               H  U  S  T  L  E
"""))
        print(f" You have {DAYS} days, {money(START_CASH)} and a {money(START_DEBT)} debt to the Syndicate")
        print(f" that grows {int(DEBT_RATE * 100)}% a day. Buy low, sell high, tunnel between spots.")
        print(" Big deals raise your Heat. Heat brings traces. Zero OpSec means busted.")
        print(" Only cash and your wallet count at the end, so sell before the last day is over.")
        self.roll_market()
        actions = {"b": self.buy, "s": self.sell, "t": self.travel, "l": self.lay_low,
                   "d": self.dump}
        while not self.over:
            self.show()
            cmd = ask(" > ").lower()[:1]
            if cmd in actions:
                actions[cmd]()
            elif cmd == "k" and self.loc == HOME:
                self.broker()
            elif cmd == "w" and self.loc == HOME:
                self.cold_wallet()
            elif cmd == "q":
                if ask(" Abandon this run? (y/n) ").lower().startswith("y"):
                    sys.exit(0)
        self.finish()

    def finish(self):
        print()
        print(green("=" * 64))
        if self.busted:
            print(red(" BUSTED. A van you never noticed was parked outside all week."))
            print(red(f" Your run ends on day {self.day}. No score for the logged-and-tagged."))
            return
        score = self.cash + self.wallet - self.debt
        for limit, rank in ((0, "Owned by the Syndicate"), (50_000, "Script Kiddie"),
                            (250_000, "Gray Hat"), (1_000_000, "Elite Operator"),
                            (10_000_000, "Ghost in the Wire")):
            if score < limit:
                break
        else:
            rank = "Legend of the Underground"
        print(f" RUN COMPLETE.  Cash {money(self.cash)} + wallet {money(self.wallet)} "
              f"- debt {money(self.debt)}")
        print(f" Final score: {green(money(score))}   Rank: {cyan(rank)}")
        record_score(score)


def record_score(score):
    try:
        scores = json.loads(SCORES.read_text())
        assert isinstance(scores, list)
    except Exception:
        scores = []
    if len(scores) < 10 or score > min(s["score"] for s in scores):
        handle = ask(" New high score! Your handle: ")[:16] or "anon"
        scores.append({"handle": handle, "score": score})
        scores = sorted(scores, key=lambda s: s["score"], reverse=True)[:10]
        try:
            SCORES.write_text(json.dumps(scores, indent=1))
        except OSError:
            pass
    print("\n  HALL OF FAME")
    for i, s in enumerate(scores, 1):
        print(f"  {i:>2}. {s['handle']:<16} {money(s['score']):>16}")


def main():
    parser = argparse.ArgumentParser(description="Zero Day Hustle")
    parser.add_argument("--seed", type=int, help="seed the random generator")
    args = parser.parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    while True:
        Game().run()
        if not ask("\n Play again? (y/n) ").lower().startswith("y"):
            break


if __name__ == "__main__":
    main()
