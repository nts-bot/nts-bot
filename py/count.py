import os
import json
import pprint

os.chdir(os.getenv("directory"))


def _j2d(path):
    with open(f"{path}.json", "r", encoding="utf-8") as f:
        w = json.load(f)
        return dict(w)


def _d2j(path, allot):
    with open(f"{path}.txt", "w", encoding="utf-8") as f:
        f.write(allot)


def counter():
    track_d = dict()
    artist_d = dict()
    l = list()

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
                    info1 = f"{i} -- {a} -- {r}"
                    info2 = f"{i} -- {r} -- {a}"
                    track = f"{a} -- {r}"
                    if any(i not in l for i in [info1, info2]):
                        if track not in track_d:
                            track_d[track] = 1
                        else:
                            track_d[track] += 1
                    else:
                        pass
                        # track_d[track] += 1
                    if f"{r}" in artist_d:
                        artist_d[f"{r}"] += 1
                    elif f"{a}" not in artist_d:
                        artist_d[f"{a}"] = 1
                    else:
                        artist_d[f"{a}"] += 1
                    l += [info1, info2]
    return track_d, artist_d


def clean(dic, amount):
    c = dict([i for i in sorted(dic.items(), key=lambda item: item[1])[::-1][:amount]])
    a = pprint.pformat(c, sort_dicts=False).split("\n")
    for i in range(len(a)):
        a[i] = f"{i+1:03}. {a[i].replace('{','').replace('}','')}"
    return "\n".join(a)


track_d, artist_d = counter()
_d2j("./most_played_tracks", clean(track_d, 200))
_d2j("./most_played_artists", clean(artist_d, 100))
