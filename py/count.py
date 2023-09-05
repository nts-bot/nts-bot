import os
import json
import pprint


def _j2d(path):
    with open(f"{path}.json", "r", encoding="utf-8") as f:
        w = json.load(f)
        return dict(w)


def _d2j(path, allot):
    with open(f"{path}.txt", "w", encoding="utf-8") as f:
        f.write(allot)


os.chdir(os.getenv("directory"))
d = dict()
bad = [
    "unknown",
    "unknown artist",
    "untitled",
    "????",
    "???",
    "?",
    "??",
    "n/a",
    "artist unknown",
    "unreleased",
]
for i in os.listdir("./tracklist/"):
    t = _j2d(f"./tracklist/{i.split('.json')[0]}")
    for j in t:
        for k in t[j]:
            a = (
                t[j][k]["artist"]
                .replace(",", "")
                .replace("'", "")
                .replace('"', "")
                .strip()
            )
            r = (
                t[j][k]["title"]
                .replace(",", "")
                .replace("'", "")
                .replace('"', "")
                .strip()
            )
            if not ((a.lower() in bad) or (r.lower() in bad)):
                if f"{r} -- {a}" in d:
                    d[f"{r} -- {a}"] += 1
                elif f"{a} -- {r}" not in d:
                    d[f"{a} -- {r}"] = 1
                else:
                    d[f"{a} -- {r}"] += 1

c = dict(
    [i for i in sorted(d.items(), key=lambda item: item[1])[::-1][:300] if i[1] >= 21]
)

a = pprint.pformat(c, sort_dicts=False).split("\n")
for i in range(len(a)):
    a[i] = f"{i+1:03}. {a[i].replace('{','').replace('}','')}"

_d2j("./most_played_tracks", "\n".join(a))

# ARTISTS LISTS

bad = [
    "unknown",
    "unknown artist",
    "untitled",
    "????",
    "???",
    "?",
    "??",
    "n/a",
    "artist unknown",
    "unreleased",
    "intro",
    "guest mix",
]

for i in os.listdir("./tracklist/"):
    t = _j2d(f"./tracklist/{i.split('.json')[0]}")
    for j in t:
        for k in t[j]:
            a = (
                t[j][k]["artist"]
                .replace(",", "")
                .replace("'", "")
                .replace('"', "")
                .strip()
            )
            r = (
                t[j][k]["title"]
                .replace(",", "")
                .replace("'", "")
                .replace('"', "")
                .strip()
            )
            if not ((a.lower() in bad) or (r.lower() in bad)):
                if f"{r}" in d:
                    d[f"{r}"] += 1
                elif f"{a}" not in d:
                    d[f"{a}"] = 1
                else:
                    d[f"{a}"] += 1

c = dict([i for i in sorted(d.items(), key=lambda item: item[1])[::-1][:100]])

a = pprint.pformat(c, sort_dicts=False).split("\n")
for i in range(len(a)):
    a[i] = f"{i+1:03}. {a[i].replace('{','').replace('}','')}"

_d2j("./most_played_artists", "\n".join(a))
