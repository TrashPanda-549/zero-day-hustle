# Zero Day Hustle

A trading game set in the hacker underground. You have 30 days, $2,000 and a debt to the Fixer that grows every day. Buy low, sell high, and stay off the radar.

![App icon](assets/logo.png)

## Play in the browser (and on iPhone)

**https://trashpanda-549.github.io/zero-day-hustle/**

It runs on any phone or computer. On an iPhone or iPad, open the link in Safari, tap Share, then **Add to Home Screen**: it then opens full screen like an app and keeps working offline.

## Download

Grab the latest build from the [Releases page](../../releases):

| Platform | File | Notes |
| --- | --- | --- |
| Windows | `ZeroDayHustle-<version>-windows.exe` | Portable, no install. SmartScreen may warn because the app is unsigned: choose More info, then Run anyway. |
| Android | `ZeroDayHustle-<version>-android.apk` | Android 7 or newer. Allow "install unknown apps" when asked. |
| Mac | `ZeroDayHustle-<version>-mac.dmg` | Unsigned: right-click the app and choose Open the first time. |
| iPhone | `ZeroDayHustle-<version>-ios-unsigned.ipa` | Unsigned, so it only installs through a sideloading tool that signs it with your own Apple ID. For most people the browser version above is the easier way. |

## How to play

- Ten goods, from Warez up to Zero-Days, with prices that change every day. News events make some scarce and others dirt cheap.
- Tunnel between the locations. Travelling does not end the day: you get six trips a day, prices stay put until you sleep, and only sleeping at the Bunker starts a new day. The trip home is always free.
- The Hackerspace is home: pay down or borrow from the Fixer, and park cash in the cold wallet where it earns interest and can't be phished.
- Freelance jobs use up goods you hold on a job. If the job works it pays more than selling them; if it fails the goods are burned and your Heat jumps.
- You earn XP and levels that carry over between runs. At level 10 you can join one of four syndicates, each with a permanent perk.
- Each syndicate has its own line of eight missions, given by a handler: deliveries, raids, shaking the law, trading targets, and a final breach of a rival crew's core. Missions pay far more XP than anything else, plus cash and gear, and progress carries over between runs. After the last one the crew hands out repeatable standing orders that pay more XP the higher your level.
- Now and then a junkie is waiting where you surface, selling gadgets, medkits, ammo, weapons, gear or goods for 25 to 45% of the shop price. Each one carries different things, and they are gone once you walk on.
- Big deals raise your Heat, and Heat decides who hunts you: the police, then the FBI, then the NSA. Police and FBI seize your goods, fine you and cost you days. The NSA ends the run.
- The Bunker is your hideout. Stash goods there to free up your drive, keep spare gear in the locker, and sleep to end the day and heal. Rival crews can't attack you at home, but the police, the FBI and the NSA can raid it whether you are in or out, including while you sleep, and they seize the stash.
- Rival syndicates try to rob you, and once a day you can raid one of their nodes for loot. Every raid makes that crew angrier.
- When cornered you can fire a weapon, throw an EMP, counter-hack through your proxies, burn a Zero-Day, run, wipe your drive or pay them off. Weapons and gear come from the black market at the Tor Bazaar and the Datacenter Dock.
- Weapons come in four kinds. Blunt weapons are quiet and can stun, blades are silent, firearms are loud, and military hardware is very loud. The gun store at the Strip Mall sells the first three but runs a background check on firearms; the arms dealer at the black market sells firearms at a markup and military hardware with no questions asked.
- Firearms and military hardware use ammunition, one round a shot. There are five kinds, from Bargain Bin Bullets (5% worse) to Aimbot Rounds (25% better at hitting). Out of ammo, a gun is just a club.
- Ctrl+Alt+Drip at the Strip Mall sells clothing and body armour, with two items for every gear slot each day.
- You have two bars to protect. Shooting, EMPs and running put your Health at risk; hacking puts your OpSec at risk. Lose either and you go down. An armoured vest cuts Health damage, and a street doc at the black market patches you up.
- Sleeping cools your Heat and restores Health and OpSec. Medkits heal you any time, even mid-fight; you start each run with two, and with a basic item in every gear slot.
- Gear for five slots (head, body, hands, feet, deck) boosts your stats and comes in five rarities: Common, Uncommon, Rare, Epic and Legendary. Rival crews drop it, the black market sells it, and it stays with you between runs.
- Your avatar shows all of it. Pick a skin tone, hair and streak from the Gear screen. It wears your gear (Epic pulses, Legendary shimmers and sparks), carries your weapon and gadgets, and stands in front of wherever you are. It gets bruised and bandaged as Health drops, glitches as OpSec fails, and is lit by police lights, a Fed searchlight or an NSA crosshair as Heat climbs. Your syndicate leaves its mark, and cyberware appears at levels 8, 9, 20, 25 and 30.
- Only cash and your cold wallet count at the end, minus whatever you still owe.

## Terminal version

There is also a text-only version that needs nothing but Python 3. It is the original, simpler game, without freelance jobs, levels or syndicates:

```
python hustle.py
```

## Building from source

The game is a single page, `www/index.html`, which also runs in any browser. The desktop apps wrap it with Electron and the Android app with Capacitor.

```
npm install
npm start            # run the desktop app
npm run dist:win     # build the Windows .exe into dist/
npm run dist:mac     # build the Mac .dmg (on a Mac)
```

For Android, with Java 21 and the Android SDK installed:

```
npx cap add android
npx cap sync android
cd android && ./gradlew assembleDebug
```