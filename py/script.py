# BASIC LIBRARIES
import os
import re
import time
import queue
import string
import urllib
import pprint
import random
import logging
import traceback
import datetime as dt
from threading import Thread, Lock

# .2 Local
import web
import utils
import rating

# SPOTIFY API TOOL
import spotipy

# IMAGE PROCESSING TOOLS
import cv2
import base64
from PIL import Image

# ENVIRONMENT VARIABLES
from dotenv import load_dotenv

load_dotenv()
connection = web.connection()


class nts:
    def __init__(self):
        self.showlist = [i.split(".")[0] for i in os.listdir("./tracklist/")]
        self.pid = utils.rnw_json("pid")

    # RUN SCRIPT

    @utils.monitor
    def review(self, show):
        tday = dt.date.today()
        day = [tday]
        for i in range(1, 15):
            day += [tday - dt.timedelta(i)]
        try:
            rday = dt.datetime.fromtimestamp(
                os.path.getmtime(f"./spotify/{show}.json")
            ).date()
        except:
            return True
        if rday in day:
            return True
        else:
            return False

    def _reset(self, show):
        logging.info(".RESET.")
        utils.rnw_json(f"./spotify_search_results/{show}", dict())
        utils.rnw_json(f"./spotify/{show}", dict())

    # SPOTIFY SEARCH

    @utils.monitor
    def pid(self, show):
        """GET/CREATE SHOW PLAYLIST ID"""
        try:
            shelf = self.pid[show]
            return shelf
        except KeyError:  # new show
            #
            try:
                im = [i for i in os.listdir("./jpeg/") if i.split(".")[0] == show][0]
                basewidth = 600
                img = Image.open(f"./jpeg/{im}")
                wpercent = basewidth / float(img.size[0])
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), Image.ANTIALIAS)
                img.save(f"./jpeg/{im}")
                img = cv2.imread(f"./jpeg/{im}")
                jpg_img = cv2.imencode(".jpg", img)
                b64_string = base64.b64encode(jpg_img[1]).decode("utf-8")
            except Exception as error:
                logging.info(f"image failure for show : {show} : Error : {error}")
            ref = connection.sp.user_playlist_create(
                connection.user,
                f"{show}-nts",
                public=True,
                description=f"(https://www.nts.live/shows/{show})",
            )
            self.pid[show] = ref["id"]
            utils.rnw_json("pid", self.pid)
            try:  # FIXME
                connection.sp.playlist_upload_cover_image(ref["id"], b64_string)
            except:
                print("ERROR COVER")
                logging.warning(traceback.format_exc())
            #
            return ref["id"]

    @utils.monitor
    def searchloop(self, show, jsonlist, kind="search", episodelist=[]):
        """jsonlist = [TRACKLIST, DO-ON, ADDITIONALS]"""
        for jsondir in jsonlist:
            locals()[jsondir] = utils.rnw_json(f"./{jsondir}/{show}")

        total = list(eval(jsonlist[0]).keys())
        if not episodelist:
            episodelist = eval(jsonlist[0])

        multiple = dict()

        for episode in episodelist:
            multiple[episode] = dict()
            _ = f"{show[:7]}{episode[:7]}. . . . . . . . . .{total.index(episode)}:{len(total)}."
            logging.info(_)
            print(_, end="\r")
            if episode not in eval(jsonlist[1]):
                eval(jsonlist[1])[episode] = dict()
                utils.rnw_json(f"./{jsonlist[1]}/{show}", eval(jsonlist[1]))
            ok = eval(jsonlist[0])[episode].keys()
            nk = eval(jsonlist[1])[episode].keys()
            vl = [i for i in eval(jsonlist[1])[episode].values()]
            if list(set(ok) - set(nk)) or (not all(vl)):
                for trdx in eval(jsonlist[0])[episode]:
                    second = False
                    try:
                        if not eval(jsonlist[1])[episode][trdx]:
                            second = True
                    except KeyError:
                        second = True
                    if second:
                        _ = f"{show[:7]}{episode[:7]}. . . . .{list(ok).index(trdx)}:{len(list(ok))}."
                        print(_, end="\r")
                        if kind == "search":
                            # 0 : TRACKLIST ; 1 : SEARCH
                            multiple[episode][trdx] = 0
                        elif kind == "rate":
                            # 0 : TRACKLIST ; 1 : RATE ; 2 : SEARCH
                            multiple[episode][trdx] = 0

        if any([True for i in multiple if multiple[i]]):
            if kind == "search":
                req = self.mt_spotifysearch(eval(jsonlist[0]), multiple)
            elif kind == "rate":
                req = self.mt_streamrate(eval(jsonlist[0]), eval(jsonlist[2]), multiple)
            for episode in multiple:
                for td in multiple[episode]:
                    eval(jsonlist[1])[episode][td] = req[episode][td]
            utils.rnw_json(f"./{jsonlist[1]}/{show}", eval(jsonlist[1]))

    # SPOTIFY/YOUTUBE PLAYLIST FUNCTIONS

    @staticmethod
    def scene(sequence):
        """GET UNIQUE ITEMS IN LIST & IN ORDER"""
        seen = set()
        return [x for x in sequence if not (x in seen or seen.add(x))]

    @utils.monitor
    @utils.timeout(300.0)
    def spotifyplaylist(self, show, threshold=[6, 10], reset=False):
        connection.connect()

        """ APPEND-FROM/CREATE SPOTIFY PLAYLIST """
        pid = self.pid[show]
        meta = utils.rnw_json(f"./meta/{show}")
        sortmeta = sorted(
            [".".join(value["date"].split(".")[::-1]), key]
            for (key, value) in meta.items()
            if isinstance(value, dict)
        )

        """ LOAD DATA """
        uploaded = utils.rnw_json(f"./uploaded/{show}")
        showlist = utils.rnw_json(f"./tracklist/{show}")
        rate = utils.rnw_json(f"./spotify/{show}")

        """ IF NEW SHOW, OR IF EPISODE IS OLDER THAN CURRENTLY UPLOADED """
        if not uploaded:
            logging.info(".reset.")
            reset = True
        elif sortmeta:
            valid = [i for i in showlist if showlist[i]]
            ha_up = [i for i in sortmeta if i[1] in valid]
            to_up = [i for i in ha_up if i[1] not in list(uploaded)]
            if to_up and (to_up[-1][0] < ha_up[-1][0]):
                reset = True

        """ EMPTY PARAMETERS TO FILL """
        tid = []
        trackdict = dict()
        pup = []
        mis = 0
        almost = 0
        empty = 0
        f = True
        ff = 0
        upend = False

        """ GET SHOW EPISODES LATEST & OLDEST DATES """
        while f:
            fp = sortmeta[ff][0].split(".")
            firstep = f"{fp[2]}.{fp[1]}.{fp[0]}"
            if firstep != "00.00.00":
                f = False
            else:
                ff += 1
        lp = sortmeta[-1][0].split(".")
        lastep = f"{lp[2]}.{lp[1]}.{lp[0]}"

        """ LOOP : GET (NEW) TRACKS TO UPLOAD (ACCORDING TO THRESHOLD) """
        idx = -1
        for mt in sortmeta[::-1]:
            idx += 1
            ep = mt[1]
            trackdict[idx] = []
            if ep not in uploaded:
                uploaded[ep] = 1
                up = True
            else:
                up = False
            if showlist[ep]:
                for tr in rate[ep]:
                    #
                    if rate[ep][tr]["ratio"] != -1:
                        bad = [
                            "unknown",
                            "unknown artist",
                            "n/a",
                            "artist unknown",
                            "unreleased",
                        ]
                        ua = (
                            " ".join(
                                re.sub(
                                    r"([A-Z])", r" \1", showlist[ep][tr]["artist"]
                                ).split()
                            )
                            .lower()
                            .strip()
                        )
                        ut = (
                            " ".join(
                                re.sub(
                                    r"([A-Z])", r" \1", showlist[ep][tr]["title"]
                                ).split()
                            )
                            .lower()
                            .strip()
                        )
                        if (ua in bad) or (ut in bad) or ("".join(set(ua)) == "?"):
                            rate[ep][tr]["ratio"] = -1
                            rate[ep][tr]["uri"] = ""
                        else:
                            ua = (
                                " ".join(
                                    re.sub(
                                        r"([A-Z])", r" \1", rate[ep][tr]["artist"]
                                    ).split()
                                )
                                .lower()
                                .strip()
                            )
                            ut = (
                                " ".join(
                                    re.sub(
                                        r"([A-Z])", r" \1", rate[ep][tr]["title"]
                                    ).split()
                                )
                                .lower()
                                .strip()
                            )
                            if (
                                ("unknown artist" in ua)
                                or ("unknown track" in ua)
                                or ("unknown track" in ut)
                                or (ua in bad)
                                or (ut in bad)
                                or ("".join(set(ua)) == "?")
                            ):
                                rate[ep][tr]["ratio"] = -1
                                rate[ep][tr]["uri"] = ""
                    #
                    if threshold[0] <= rate[ep][tr]["ratio"] <= threshold[1]:
                        tid += [rate[ep][tr]["trackid"]]
                        if up:
                            upend = True
                            trackdict[idx] += [rate[ep][tr]["trackid"]]
                    pup += [rate[ep][tr]["trackid"]]
                    if not rate[ep][tr]["trackid"]:
                        mis += 1
                    if rate[ep][tr]["ratio"] in [6]:
                        almost += 1
            else:
                empty += 1

        """ STORE UPDATED RATE INFO (REMOVING UNKNOWN ARTIST) """
        utils.rnw_json(f"./spotify/{show}", rate)

        """ RESET CONDITION """
        if reset:
            logging.warning("RESET")
            current = connection.sp.user_playlist_tracks(connection.user, pid)
            tracks = current["items"]
            while current["next"]:
                current = connection.sp.next(current)
                tracks.extend(current["items"])
            ids = []
            for x in tracks:
                ids.append(x["track"]["id"])
            rem = list(set(ids))
            hund = [rem[i : i + 100] for i in range(0, len(rem), 100)]
            for i in hund:
                print(".resetting.", end="\r")
                connection.sp.user_playlist_remove_all_occurrences_of_tracks(
                    connection.user, pid, i
                )

        """ UPLOAD """
        if upend:
            _ = ".tracks appending."
            logging.info(_)
            print(_, end="\r")
            for episode in list(trackdict.keys())[::-1]:
                if trackdict[episode]:
                    trackstoadd = trackdict[episode]
                    hund = [
                        trackstoadd[i : i + 100]
                        for i in range(0, len(trackstoadd), 100)
                    ]
                    for i in hund:
                        connection.sp.user_playlist_add_tracks(
                            connection.user, pid, i, 0
                        )
            print(".tracks appended.", end="\r")

        """ DESCRIPTION / TITLES """
        title, desk = (
            meta["title"],
            meta["description"],
        )
        desk = (
            desk.replace("\n", " ")
            .replace("\\", "")
            .replace('"', "")
            .replace("'", "")
            .strip()
        )
        syn = (
            f"{mis+len(set(pup))-len(set(tid))} tracks missing".strip()
        )  # {almost} # {duplicates}{empty}

        a = 0
        reduced_title = ""
        while len(reduced_title) < 60:
            a += 1
            _title = ".".join(desk.split(".")[:a])
            if len(reduced_title) == len(_title):
                break
            elif len(_title) > 100:
                reduced_title = ".".join(desk.split(".")[: a - 1])
                break
            else:
                reduced_title = _title

        if not reduced_title:
            a = 0
            while len(reduced_title) < 80:
                a += 1
                _title = " ".join(desk.split(" ")[:a]) + "..."
                if len(reduced_title) == len(_title):
                    break
                elif len(_title) > 100:
                    reduced_title = " ".join(desk.split(" ")[: a - 1]) + "..."
                    break
                else:
                    reduced_title = _title

        """ UPDATE SPOTIFY PLAYLIST DETAILS """
        x_test = connection.sp.user_playlist_change_details(
            connection.user, pid, name=f"{title} - NTS", description=f"{syn}"
        )
        x_real = connection.sp.user_playlist_change_details(
            connection.user,
            pid,
            name=f"{title} - NTS",
            description=f'"{show}" {lastep}→{firstep} {reduced_title} [{syn}]',
        )

        """ UPDATE UPLOADED EPISODES METADATA """
        utils.rnw_json(f"./uploaded/{show}", uploaded)

    def subfollow(self, usr, creds):
        if str(usr) not in creds:
            return None
        user = creds[str(usr)]["user"]
        cid = creds[str(usr)]["cid"]
        secret = creds[str(usr)]["secret"]

        callback = "http://localhost:8888/callback"
        spot = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(
                client_id=cid,
                client_secret=secret,
                redirect_uri=f"{callback}",
                scope="playlist-modify-public user-follow-modify",
                username=user,
            ),
            requests_timeout=5,
            retries=5,
        )
        logging.info("Testing .")
        _ = spot.user(user)
        logging.info("Successful .")

        # if kind == "cre":
        extent = self.showlist[(200 * (usr - 1)) : (200 * (usr))]

        print(f"{usr}: Unfollowing")
        cn = False
        while not cn:
            try:
                plys = []
                for i in range(4):
                    it = spot.user_playlists(user, offset=(i * 50))["items"]
                    plys += [k["id"] for k in it]
                for i in plys:
                    playlist_owner_id = "31yeoenly5iu5pvoatmuvt7i7ksy"
                    spot.user_playlist_unfollow(playlist_owner_id, i)
                cn = True
            except:
                logging.warning(traceback.format_exc())

        _ = f"{usr}: Following: {extent[0][0]} : {extent[-1][0]}"
        print(_)
        logging.info(_)
        cn = False
        while not cn:
            try:
                for i in extent[::-1]:
                    if i in self.pid:
                        logging.info(f"{usr}: {i}")
                        playlist_owner_id = "31yeoenly5iu5pvoatmuvt7i7ksy"
                        playlist_id = self.pid[i]
                        if playlist_id:
                            spot.user_playlist_follow_playlist(
                                playlist_owner_id, playlist_id
                            )
                        else:
                            logging.warning(f"FAILED : {i}")
                    else:
                        logging.warning(f"FAILED : {i}")
                cn = True
            except:
                logging.warning(traceback.format_exc())

        del creds[str(usr)]

    def follow(self, kind="cre"):
        """SECONDARY SPOTIFY USERS WHO MAINTAIN ALPHABETICALLY ORGANIZED PLAYLISTS BELOW SPOTIFY (VISIBLE) PUBLIC PLAYLIST LIMIT (200)"""
        creds = utils.rnw_json(f"{kind}dentials")
        usrcall = round(len(self.showlist) / 200 + 0.4999)
        _ = range(1, usrcall + 1)
        ranger = [i for i in range(usrcall + 1)]
        return self.parallel(self.subfollow, ranger, [creds])

    @staticmethod
    @utils.timeout(10)
    def subsubprivatise(pid, b):
        _ = connection.sp.playlist(pid, fields="followers,public")
        if _["public"] != b:
            connection.sp.playlist_change_details(pid, public=b)
        if not b:
            return _["followers"]["total"]
        else:
            return 0

    def subprivatise(self, pid, b):
        logging.info(f"Privitising: {str(not b):<8} {pid}")
        while True:
            try:
                return self.subsubprivatise(pid, b)
            except:
                logging.warning(traceback.format_exc())
                connection.connect()

    def publicise(self):
        values = list(self.pid.values())
        followers = dict()
        o = 0
        pids = []
        anem, r = self.parallel(self.subprivatise, values, [False])
        for c in range(r):
            followers[values[c]] = eval(f"utils.{anem}_{c}")
        most = {
            k: v for k, v in sorted(followers.items(), key=lambda item: item[1])[::-1]
        }
        for i in most:
            o += 1
            if o > 200:
                break
            else:
                pids += [i]
        return self.parallel(self.subprivatise, pids, [True])

    def subsubcounter(self, show, episodes):
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
        for k in episodes:
            a = (
                episodes[k]["artist"]
                .replace(",", "")
                .replace("'", "")
                .replace('"', "")
                .strip()
            )
            r = (
                episodes[k]["title"]
                .replace(",", "")
                .replace("'", "")
                .replace('"', "")
                .strip()
            )
            if not ((a.lower() in bad) or (r.lower() in bad)):
                info1 = f"{show} -- {a} -- {r}"
                info2 = f"{show} -- {r} -- {a}"
                track = f"{a} -- {r}"
                if any(i not in self.list for i in [info1, info2]):
                    if track not in self.track_d:
                        self.track_d[track] = 1
                    else:
                        self.track_d[track] += 1
                else:
                    pass
                    # track_d[track] += 1
                if f"{r}" in self.artist_d:
                    self.artist_d[f"{r}"] += 1
                elif f"{a}" not in self.artist_d:
                    self.artist_d[f"{a}"] = 1
                else:
                    self.artist_d[f"{a}"] += 1
                self.list += [info1, info2]

    def subcounter(self, show):
        return self.parallel(
            self.subsubcounter, utils.rnw_json(f"./tracklist/{show}"), [show]
        )

    def counter(self):
        self.track_d = dict()
        self.artist_d = dict()
        self.list = list()
        _ = self.parallel(self.subcounter, self.showlist)
        with open("./most_played_tracks.txt", "w", encoding="utf-8") as f:
            f.write(self.cleaners_from_venus(self.track_d, 200))
        with open("./most_played_artists.txt", "w", encoding="utf-8") as f:
            f.write(self.cleaners_from_venus(self.track_d, 100))

    @staticmethod
    def cleaners_from_venus(dic, amount):
        c = dict(
            [i for i in sorted(dic.items(), key=lambda item: item[1])[::-1][:amount]]
        )
        a = pprint.pformat(c, sort_dicts=False).split("\n")
        for i in range(len(a)):
            a[i] = f"{i+1:03}. {a[i].replace('{','').replace('}','')}"
        return "\n".join(a)

    @staticmethod
    def parallel(function, ranger, kwargs=[]):
        r = range(len(ranger))
        anem = "".join(random.choice(string.ascii_letters) for i in range(10))
        f = {f"{anem}_{c}": function for c in r}
        p = {f"{anem}_{c}": [ranger[c], *kwargs] for c in r}
        utils.parallel_process(f, p)
        return anem, len(ranger)

    # SPOTIFY API SEARCH FUNCTIONS

    @utils.timeout(15.0)
    def subrun(self, query):
        """RUN SPOTIFY API"""
        try:
            result = connection.sp.search(q=query, type="track,artist", limit=3)
            if result is None:
                raise RuntimeError
            else:
                return result
        except spotipy.SpotifyException as error:
            if error.http_status == 400:  # HTTP ERROR
                return {"tracks": {"items": ""}}
            elif error.http_status == 429:  # MAX RETRY ERROR
                time.sleep(3.0)
                return self.subrun(query)
            else:
                raise RuntimeWarning(error)

    def _run(self, query):
        """RUN SPOTIFY API WITH TIMEOUT"""
        try:
            return self.subrun(query)
        except RuntimeError:
            raise RuntimeError("Spotify API Broken")
        except Exception as error:
            connection.connect()
            return self.subrun(query)

    # MULTITHREADING FUNCTIONS

    def qmt(self, q, kind, nw=16):
        """GENERAL MULTITHREADING FUNCTION"""
        """ COMBINE DICTIONARIES INTO FLAT DICTIONARY (INDEX-DATA = NEW-KEY) """
        q1 = q[0]
        taskdict = {
            f"q1.{l1:03}.{l2:03}": q1[list(q1.keys())[l1]][
                list(q1[list(q1.keys())[l1]].keys())[l2]
            ]
            for l1 in range(len(q1))
            for l2 in range(len(q1[list(q1.keys())[l1]]))
        }
        if len(q) == 2:
            q2 = q[1]
            taskdict |= {
                f"q2.{l1:03}.{l2:03}": q2[list(q2.keys())[l1]][
                    list(q2[list(q2.keys())[l1]].keys())[l2]
                ]
                for l1 in range(len(q2))
                for l2 in range(len(q2[list(q2.keys())[l1]]))
            }

        """ RUN MULTITHREAD (5 second TIMEOUT) """
        MT = multithread(taskdict, kind)  # load class
        MT.multithreading(nw)  # run threads
        """ RE-RUN MULTITHREAD FOR SKIPPED (20 second TIMEOUT) """
        if MT.double:
            logging.info(".Re-Threading.")
            MT.multithreading(8, MT.double)
        """ RE-RE-RUN WITHOUT MULTITHREADING (AS LAST RESORT) FOR SKIPPED (NO TIMEOUT) """
        if MT.double:
            logging.info(".Re-Re-Threading.")
            MT.nothread(MT.double)
        return MT.taskdict

    def mt_request(self, content):
        """REQUESTS FUNCTION"""
        c = 0
        request = urllib.request.Request(content)
        repeat = True
        while repeat:
            try:
                c += 1
                return urllib.request.urlopen(request).read()
            except:
                logging.debug(f"{c}$")
                time.sleep(1.0)

    def mt_spotifysearch(self, showson, multiple):
        """SPOTIFY SEARCH : DICTIONARY MAKER"""
        q1 = dict()
        q2 = dict()
        for episode in multiple:
            q1[episode] = dict()
            q2[episode] = dict()
            for td in multiple[episode]:
                q1[episode][
                    td
                ] = f'artist:{showson[episode][td]["artist"]} track:{showson[episode][td]["title"]}'
                q2[episode][
                    td
                ] = f'{showson[episode][td]["artist"]} : {showson[episode][td]["title"]}'
        return self.mt_samp(q1, q2)

    def mt_samp(self, q1, q2):
        """SPOTIFY SEARCH : RUN MULTITHREAD AND RECREATE DICTIONARY FROM RESULT"""
        taskdict = self.qmt([q1, q2], "spotify", 32)
        for l1 in range(len(q1)):
            episode = list(q1.keys())[l1]
            for l2 in range(len(q1[list(q1.keys())[l1]])):  # td are tracks
                td = list(q1[list(q1.keys())[l1]].keys())[l2]
                S0 = taskdict[f"q1.{l1:03}.{l2:03}"]
                S1 = taskdict[f"q2.{l1:03}.{l2:03}"]
                q1[episode][td] = {"s0": S0, "s1": S1}
        return q1

    def mt_streamrate(self, showson, srchson, multiple):
        """RATE RESULTS FROM YOUTUBE/SPOTIFY/BANDCAMP : DICTIONARY MAKER"""
        q1 = dict()
        q2 = dict()
        for episode in multiple:
            q1[episode] = dict()
            q2[episode] = dict()
            for td in multiple[episode]:
                qa = showson[episode][td]["artist"]
                qt = showson[episode][td]["title"]
                s0 = srchson[episode][td]["s0"]
                s1 = srchson[episode][td]["s1"]

                if all([qa, qt]):
                    q1[episode][td] = {"s": s0, "qa": qa, "qt": qt}
                    q2[episode][td] = {"s": s1, "qa": qa, "qt": qt}
                else:
                    q1[episode][td] = {"s": "", "qa": "", "qt": ""}
                    q2[episode][td] = {"s": "", "qa": "", "qt": ""}

        return self.mt_rate(q1, q2)

    def mt_rate(self, q1, q2):
        """RATE RESULTS FROM YOUTUBE/SPOTIFY/BANDCAMP : RUN MULTITHREAD AND RECREATE DICTIONARY FROM RESULT"""
        taskdict = self.qmt([q1, q2], "rate", 16)
        for l1 in range(len(q1)):
            episode = list(q1.keys())[l1]
            for l2 in range(len(q1[list(q1.keys())[l1]])):  # td are tracks
                td = list(q1[list(q1.keys())[l1]].keys())[l2]
                #
                a0, t0, r0, u0 = (
                    taskdict[f"q1.{l1:03}.{l2:03}"]["a"],
                    taskdict[f"q1.{l1:03}.{l2:03}"]["t"],
                    taskdict[f"q1.{l1:03}.{l2:03}"]["r"],
                    taskdict[f"q1.{l1:03}.{l2:03}"]["u"],
                )
                a1, t1, r1, u1 = (
                    taskdict[f"q2.{l1:03}.{l2:03}"]["a"],
                    taskdict[f"q2.{l1:03}.{l2:03}"]["t"],
                    taskdict[f"q2.{l1:03}.{l2:03}"]["r"],
                    taskdict[f"q2.{l1:03}.{l2:03}"]["u"],
                )
                #
                if ([a0, t0, r0, u0] != ["", "", 0, ""]) or (
                    [a1, t1, r1, u1] != ["", "", 0, ""]
                ):
                    dx = [r0, r1].index(max([r0, r1]))

                    if round(eval(f"r{dx}"), 1) >= 0.9:
                        lag = 9
                    elif round(eval(f"r{dx}"), 1) == 0.8:
                        lag = 8
                    elif round(eval(f"r{dx}"), 1) == 0.7:
                        lag = 7
                    elif round(eval(f"r{dx}"), 1) == 0.6:
                        lag = 6
                    elif round(eval(f"r{dx}"), 1) == 0.5:
                        lag = 5
                    elif round(eval(f"r{dx}"), 1) == 0.4:
                        lag = 4
                    elif round(eval(f"r{dx}"), 1) == 0.3:
                        lag = 3
                    else:
                        lag = 0

                    if any([a0, a1]):
                        q1[episode][td] = {
                            "artist": eval(f"a{dx}"),
                            "title": eval(f"t{dx}"),
                            "ratio": lag,
                            "trackid": eval(f"u{dx}"),
                        }
                    else:
                        q1[episode][td] = {
                            "artist": eval(f"a{dx}"),
                            "title": eval(f"t{dx}"),
                            "ratio": -1,
                            "trackid": "",
                        }
                else:
                    q1[episode][td] = {
                        "artist": "",
                        "title": "",
                        "ratio": -1,
                        "trackid": "",
                    }
        return q1

    # BACKUP PID IN CASE SCRIPT CRASHES

    def backup(self):
        for i in ["pid"]:
            file = utils.rnw_json(f"./{i}")
            utils.rnw_json(f"./backup/{i}", file)


class multithread:
    def __init__(self, taskdict, kind):
        self.nts = nts()
        if kind == "spotify":
            connection.connect()
        self.taskdict = taskdict
        self.taskcopy = dict(self.taskdict)
        self.kind = kind

    def multithreading(self, no_workers, keys=[]):
        self.thrd = True
        if not keys:
            self.keys = list(self.taskdict.keys())[::-1]
            self.fast = True
        else:
            self.keys = list(keys)
            self.fast = False

        class __worker__(Thread):
            def __init__(selbst, request_queue, t):
                Thread.__init__(selbst)
                selbst.t = t
                selbst.queue = request_queue

            def run(selbst):
                while not selbst.queue.empty():
                    taskid = selbst.queue.get_nowait()
                    if not taskid:
                        break
                    try:
                        if selbst.t.fast and selbst.t.kind != "spotify":
                            selbst.task5(taskid)
                        else:
                            selbst.task20(taskid)
                    except Exception:
                        print("ERROR MT")
                        logging.warning(f"MT : {traceback.format_exc()}")
                        selbst.t.double += [taskid]
                    c = len(selbst.t.keys) - selbst.t.count
                    if (c % 10 == 0) or (c < 50):
                        logging.debug(f"{c}.")
                    selbst.queue.task_done()

            @utils.timeout(5.0)
            def task5(selbst, taskid):
                selbst.t.task(taskid)

            @utils.timeout(20.0)
            def task20(selbst, taskid):
                selbst.t.task(taskid)

        self.count = 0
        self.double = []
        self.c_lock = Lock()

        workq = queue.Queue()
        for k in self.keys:
            workq.put(k)
        for _ in range(no_workers):
            workq.put("")

        workers = []
        for _ in range(no_workers):
            worker = __worker__(workq, self)  # self,
            worker.start()
            workers.append(worker)

        for worker in workers:
            worker.join()

    def counter(self, tid, result):
        if self.thrd:
            self.c_lock.acquire()
        self.taskdict[tid] = result
        if self.thrd:
            self.c_lock.release()
            self.count += 1

    def task(self, taskid):
        if self.kind == "spotify":
            result = self.nts._run(self.taskcopy[taskid])
            if result["tracks"]["items"]:
                takeaway = [
                    {
                        "artist": j["artists"][0]["name"],
                        "title": j["name"],
                        "uri": j["uri"].split(":")[-1],
                    }
                    for j in result["tracks"]["items"][:3]
                    if j is not None
                ]
            # else:
            #     takeaway = ''
            if "takeaway" not in locals():
                takeaway = ""
            self.counter(taskid, takeaway)
        elif self.kind == "rate":
            a0, t0, r0, u0 = rating.test(
                self.taskcopy[taskid]["s"],
                self.taskcopy[taskid]["qa"],
                self.taskcopy[taskid]["qt"],
            )
            self.counter(taskid, {"a": a0, "t": t0, "r": r0, "u": u0})

    def reruncounter(self, tid, result):
        self.taskdict[tid] = result

    def nothread(self, keys):
        self.keys = list(keys)
        self.thrd = False
        c = 0
        for taskid in keys:
            c += 1
            logging.debug(f".{c}:{len(keys)}.")
            self.task(taskid)
