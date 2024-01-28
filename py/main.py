"""

Description: Logic for MAIN
Authors: GAMM
Version: 1
Year: 2023-09-02

"""

# .1 Standard Libraries
import logging
import traceback

# .2 Local Libraries
import web
import utils

connection = web.connection()
webscrape = web.webscraper()


def scrape(amount: int = True):
    if isinstance(amount, bool):
        if amount:
            amount = 1
        else:
            amount = 15  # 15
    soup = webscrape.browse("https://www.nts.live/latest", amount=amount)
    episodes = soup.select("a.nts-grid-v2-item__header")
    shelf = dict()
    for i in episodes:
        href = i["href"]
        show = href.split("/")[2]
        epis = href.split("/")[-1]
        if show not in shelf:
            shelf[show] = [epis]
    return shelf


@utils.monitor
def scripts(self, show, test=False):
    # TRACKLIST
    runner(self, show, f"./meta/{show}", 1)
    # SPOTIFY
    runner(self, show, f"./spotify_search_results/{show}", 2)
    runner(self, show, f"./spotify/{show}", 3)
    # ADD
    if test:
        logging.warning(f"Running Test, Skipping Upload: {show}")
    else:
        runner(self, show, f"./spotify/{show}", 4)
        logging.debug("S-Playlist")
        runner(self, show, f"./uploaded/{show}", 6)


@utils.monitor
def runner(self, show, comparison, command):
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
            self.spotifyplaylist(show)


@utils.monitor
def prerun(comparison_path):
    episodes = webscrape.episodelist
    comparison = utils.rnw_json(comparison_path)
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


@utils.monitor
def runscript(self, test, shows, short=True, retry=False):
    # ,bd=False,short=False,retry=True)
    # def runscript(self, shows, ):
    self.backup()

    connection.connect()
    _ = {i: shows[i] for i in range(len(shows))}
    print(len(_))

    for i in range(len(shows)):
        show = shows[i]
        webscrape.episodelist = utils.rnw_json(f"./tracklist/{show}")
        webscrape.meta = utils.rnw_json(f"./meta/{show}")
        webscrape.uploaded = utils.rnw_json(f"./uploaded/{show}")

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
                scripts(self, show, test)
                break
            except RuntimeError as error:
                raise RuntimeError(error)
            except:
                print("ERROR RUN")
                logging.warning(traceback.format_exc())
