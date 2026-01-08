"""

Description: Logic for MAIN
Authors: GAMM
Version: 2
Year: 2025-11-17

"""

from os.path import join
import logging
import traceback

from . import src
from .web import connection as conn, webscraper
from .utils import rnw_json

connection = conn()
webscrape = webscraper()


def scrape(
    amount: int = True,
):
    shelf = dict()
    if isinstance(amount, bool):
        if amount:
            amount = 1
        else:
            amount = 15  # 15
    soup = webscrape.browse(
        "https://www.nts.live/latest",
        amount=amount,
    )

    episodes = soup.select("a.nts-grid-v2-item__header")
    assert episodes, "something weird"
    for i in episodes:
        href = i["href"]
        show = href.split("/")[2]
        epis = href.split("/")[-1]
        if show not in shelf:
            shelf[show] = [epis]

    assert shelf, "fetch failed"

    return shelf


def scripts(
    self,
    show,
    test: bool,
    reset: bool,
):
    # TRACKLIST
    runner(self, show, join(src,"meta",show), 1)
    # SPOTIFY
    runner(self, show, join(src,"spotify_search_results",show), 2)
    runner(self, show, join(src,"spotify",show), 3)
    # ADD
    if test:
        logging.warning(f"Running Test, Skipping Upload: {show}")
    else:
        runner(self, show, join(src,"spotify",show), 4)
        logging.debug("S-Playlist")
        runner(
            self,
            show,
            join(src,"uploaded",show),
            6,
            reset=reset,
        )


def runner(
    self,
    show: str,
    comparison,
    command,
    **kwargs,
):
    rq, do = prerun(comparison)
    if rq:
        logging.debug(f"Runner {show}: {command}")
        if command == 1:
            webscrape.ntstracklist(show, do)
        elif command == 2:
            logging.debug("Spotify")
            self.searchloop(show, ["tracklist", "spotify_search_results"], "search", do)
        elif command == 3:
            logging.debug("Spotify-Rate")
            self.searchloop(
                show, ["tracklist", "spotify", "spotify_search_results"], "rate", do
            )
        elif command == 6:
            logging.debug("Spotify-Playlist")
            self.spotifyplaylist(
                show,
                **kwargs,
            )


def prerun(
    comparison_path: str,
):
    episodes = webscrape.episodelist
    comparison: dict = rnw_json(comparison_path)
    missing_eps = []

    # SECOND TEST (TRACKS)
    if all([isinstance(comparison[i], dict) for i in comparison]) and (comparison):
        ignore_empty = True
        for episode in comparison:
            for track in episodes[episode]:
                if track not in comparison[episode]:
                    missing_eps += [episode]
                else:
                    if not comparison[episode][track]:
                        missing_eps += [episode]
    else:
        ignore_empty = False

    # FIRST TEST (TRACKLIST)
    missing_eps += [
        x
        for x in list(comparison)
        if (x not in set(list(episodes))) and isinstance(comparison[x], dict)
    ]

    if not ignore_empty:
        missing_eps += [
            x
            for x in list(episodes)
            if (x not in set(list(comparison))) or (not episodes[x])
        ]
    else:
        missing_eps += [
            x
            for x in list(episodes)
            if (x not in set(list(comparison))) and (episodes[x])
        ]

    missing_eps = scene(missing_eps)
    if missing_eps:
        _ = f". . . . . . . . . . . . . . . .:{len(missing_eps)}."
        print(_, end="\r")
        boolean = True
    else:
        boolean = False

    return (boolean, missing_eps)


def scene(sequence):
    """GET UNIQUE ITEMS IN LIST & IN ORDER"""
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def runscript(
    self,
    test: bool,
    shows: list,
    short: bool = True,
    retry: bool = False,
    reset: bool = False,
):
    print("backup")
    self.backup()
    shows = sorted(set(shows) - set(["guests"]))

    assert shows, "fetch failed"

    print("connect")
    connection.connect()

    _ = {i: shows[i] for i in range(len(shows))}
    print(len(_))

    for i in range(len(shows)):
        show = shows[i]
        webscrape.episodelist = rnw_json(join(src, "tracklist", show))
        webscrape.meta = rnw_json(join(src, "meta", show))
        webscrape.uploaded = rnw_json(join(src, "uploaded", show))

        if retry:
            webscrape.retryepisodes(show)
        _ = f"{str(show + '. . . . . . . . . . . . . . . . . . . . . . . .')[:50]}{i}/{len(shows)}"
        print(_)

        # SCRAPE / PRELIMINARY
        if short:
            webscrape.scrape(show, True)
        else:
            webscrape.scrape(show)

        # MAIN FUNCTIONS
        f = 0
        while f < 2:
            f += 1
            try:
                scripts(
                    self,
                    show,
                    test,
                    reset,
                )
                break
            except RuntimeError as error:
                raise RuntimeError(error)
            except:
                print("ERROR RUN")
                logging.warning(traceback.format_exc())
