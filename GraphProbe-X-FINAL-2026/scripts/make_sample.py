"""SYNTHETIC toy corpus (fictional names) so `make smoke` can exercise every code path offline. Not the hackathon data."""
import json, random, pathlib
random.seed(7); out = pathlib.Path("data/sample"); out.mkdir(parents=True, exist_ok=True)
FN = "Marta Ivo Lena Doro Sasha Nika Tomas Rina Pavel Alma Joren Kira Milo Vera Anton Zora Luca Nell Bram Ines Orin Sela Teo Yara".split()
LN = "Velkov Hartmann Okonjo Larsen Petrov Duarte Kwan Moreau Sato Novak Reyes Borg Ahmed Lindqvist Costa Ferro Haas Iyer Jansen Kovac Lund Maro Nash Ortiz Pike".split()
CN = "Norland Ostrava Valdria Kessen Tarnia Brevia Solmark Ionia".split()
VN = "Arden Arena|Blue Harbor Hall|Cinder Park|Delta Dome|Ember Field|Frost Stadium|Gale Centre|Haven Track".split("|")
CUPS = ["Lumen Cup", "Aster Games", "Borealis Trophy"]
docs, qs = [], []; n = 0
for cup in CUPS:
    for y in range(1990, 1998):
        w = f"{random.choice(FN)} {random.choice(LN)}"; c = random.choice(CN); v = random.choice(VN); n += 1
        docs.append({"id": f"ev{n}", "title": f"{y} {cup}", "text": f"== Overview ==\nThe {y} {cup} was a multi-sport competition. The {y} {cup} was won by {w}. The {y} {cup} was held at {v}.\n\n== Results ==\nThe {y} {cup} attracted {random.randint(40,90)} competitors from several nations."})
        docs.append({"id": f"ath{n}", "title": w, "text": f"== Biography ==\n{w} is a professional athlete. {w} represents {c}. {w} trained for many years before turning professional."})
        qs.append((cup, y, w, c, v))
for i in range(6):
    docs.append({"id": f"misc{i}", "title": f"Regional Council {i}", "text": f"The Regional Council {i} met in {1990+i}. It discussed roads, schools and budgets."})
random.shuffle(qs); pub, hid = qs[:12], qs[12:18]
def mk(sp, start):
    rows = []
    for i, (cup, y, w, c, v) in enumerate(sp):
        t = i % 3
        if t == 0: rows.append({"id": f"{start}{i}", "question": f"Who won the {y} {cup}?", "answer": w})
        elif t == 1: rows.append({"id": f"{start}{i}", "question": f"Which country did the winner of the {y} {cup} represent?", "answer": c})
        else: rows.append({"id": f"{start}{i}", "question": f"Who won the {y} {cup} and where was it held?", "answer": f"{w}; {v}"})
    return rows
with open(out / "corpus.jsonl", "w") as f:
    for d in docs: f.write(json.dumps(d) + "\n")
with open(out / "eval_public.jsonl", "w") as f:
    for r in mk(pub, "p"): f.write(json.dumps(r) + "\n")
with open(out / "eval_hidden.jsonl", "w") as f:
    for r in mk(hid, "h"): f.write(json.dumps({k: v for k, v in r.items() if k != "answer"}) + "\n")
print("sample written:", len(docs), "docs")
