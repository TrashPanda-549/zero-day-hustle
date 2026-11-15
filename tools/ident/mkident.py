"""Build the studio-ident markup (coloured ASCII) for Zero Day Hustle.

Reads the plain-ASCII avatar art and the ASCII lettering, emits:
  - a CSS block with one class per ramp level, coloured with neon.py's stops
  - two <pre> variants (72-col art for big screens, 40-col for small)
Runs of the same ramp level share one <span>, so the markup stays small and
the browser has few boxes to paint.
"""
import sys

RAMP = "@%#*+=-:. "
STOPS = [
    (0.00, (0x1a, 0x0b, 0x3d)),
    (0.30, (0x05, 0x39, 0xe8)),
    (0.55, (0x05, 0xd9, 0xe8)),
    (0.80, (0xff, 0x2a, 0x6d)),
    (1.00, (0xfc, 0xee, 0x0a)),
]


def ramp_colour(t):
    for i in range(len(STOPS) - 1):
        a, ca = STOPS[i]
        b, cb = STOPS[i + 1]
        if a <= t <= b:
            f = 0 if b == a else (t - a) / (b - a)
            return tuple(round(ca[j] + (cb[j] - ca[j]) * f) for j in range(3))
    return STOPS[-1][1]


def css():
    out = []
    for i, ch in enumerate(RAMP):
        if ch == " ":
            continue
        r, g, b = ramp_colour(max(0.0, 1.0 - i / 10.0))
        out.append(".k%d{color:#%02x%02x%02x}" % (i, r, g, b))
    return "".join(out)


def colour(lines):
    """Run-length colour one block of ASCII into spans."""
    out = []
    for line in lines:
        buf = []
        run_k, run = None, []
        def flush():
            if run:
                if run_k is None:
                    buf.append("".join(run))
                else:
                    buf.append('<span class=k%d>%s</span>' % (run_k, "".join(run)))
        for c in line.rstrip("\n"):
            k = None if c == " " else RAMP.index(c)
            if k != run_k:
                flush()
                run_k, run = k, []
            run.append(c)
        flush()
        out.append("".join(buf))
    return "\n".join(out)


def read(p):
    with open(p, encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f if l.strip("\n") != "" or True]


def trim(lines):
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def block(art_path, tp, tt, indent):
    art = trim(read(art_path))
    words = [" " * 2 + l for l in trim(read(tp))] + [""] + \
            [" " * indent + l for l in trim(read(tt))]
    lines = art + [""] + words
    cols = max(len(l) for l in lines)
    return lines, cols, len(lines)


if __name__ == "__main__":
    art_dir, let_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]
    pieces = []
    for name, art, ind in (("big", "trashpanda-72.txt", 16), ("sm", "trashpanda-40.txt", 16)):
        lines, cols, rows = block("%s/%s" % (art_dir, art),
                                  "%s/tp.txt" % let_dir, "%s/tt.txt" % let_dir, ind)
        pieces.append((name, cols, rows, colour(lines)))
    with open(out, "w", encoding="utf-8") as f:
        f.write("<!--CSS-->\n" + css() + "\n")
        for name, cols, rows, html in pieces:
            f.write("<!--%s %d %d-->\n" % (name, cols, rows))
            f.write(html + "\n")
    for name, cols, rows, html in pieces:
        print(name, "cols", cols, "rows", rows, "bytes", len(html))
