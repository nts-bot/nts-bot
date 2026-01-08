"""

Description: Web scraping & Connections
Authors: GAMM
Version: 2
Year: 2025-11-17

"""

# .1 Standard Libraries
import os
from os.path import join
import time
import pickle
import logging
import requests
from threading import Lock

# .2 Local
from . import src
from .utils import timeout, rnw_json

# .3 HTML PARSER
from bs4 import BeautifulSoup as bs

# .4 BROWSER
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# .5 SPOTIFY API TOOL
import spotipy

# .6 LOCK
lock = Lock()


class connection:
    def __init__(self):
        pass

    # SPOTIFY API

    @timeout(20.0)
    def subconnect(self, index, pick):
        """CONNECTION FUNCTION w/ TIMEOUT"""
        self.user = os.getenv("ssr")
        # NOTE: http://localhost:8888/callback deprecated
        callback = "http://127.0.0.1:8888/callback"
        cid = os.getenv(f"{index[pick]}id")
        secret = os.getenv(f"{index[pick]}st")
        self.sp = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(
                client_id=cid,
                client_secret=secret,
                redirect_uri=f"{callback}",
                scope=[
                    "ugc-image-upload",
                    "playlist-modify-public",
                    "playlist-modify-private",
                    "user-library-modify",
                    "playlist-read-private",
                    "user-read-private",
                    "user-library-read",
                ],
                # username=self.user,
                requests_timeout=5,
            ),
            # retries=10,
        )
        logging.debug(". Testing . ")
        _ = self.sp.user(self.user)
        _ = self.sp.playlist("4yN04eQGIl1Vs1ijVCCyeL")
        logging.debug("Successful")

    def connect(self):
        """CONNECTION HANDLER ; VIA https://developer.spotify.com/dashboard/applications"""
        index = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
        ]
        lock.acquire()
        try:
            with open(join(src,"pickle","spotipywebapi.pickle"), "rb") as handle:
                pick = pickle.load(handle)
            logging.warning(index[pick])
            self.subconnect(index, pick)
            time.sleep(0.5)
            lock.release()
        except Exception:
            self.conexcp()

    def conexcp(self):
        """CLEAR CACHE IF CONNECTION ERROR/TIMEOUT & TRY AGAIN"""
        index = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
        ]
        try:
            time.sleep(1.5)
            logging.warning(". Unsuccessful .")
            dr = os.listdir()

            for i in dr:
                if i == ".cache":
                    print(f"kill {i}")
                    os.remove(i)

            print("re-pickle")
            if "spotipywebapi.pickle" not in os.listdir(join(src,"pickle")):
                with open(join(src,"pickle","spotipywebapi.pickle"), "wb") as handle:
                    pickle.dump(0, handle, protocol=pickle.HIGHEST_PROTOCOL)

            with open(join(src,"pickle","spotipywebapi.pickle"), "rb") as handle:
                pick = pickle.load(handle)
            pick += 1
            if pick == (len(index) - 1):
                pick = 0

            logging.info(index[pick])

            with open(join(src,"pickle","spotipywebapi.pickle"), "wb") as handle:
                pickle.dump(pick, handle, protocol=pickle.HIGHEST_PROTOCOL)

            self.subconnect(index, pick)
            time.sleep(0.5)
            lock.release()

        except Exception as error:
            logging.error(error)
            self.conexcp()
            time.sleep(1.5)


class webscraper:
    def __init__(self):
        pass

    def browse(
        self,
        url,
        amount=100,
    ):
        options = webdriver.EdgeOptions()

        options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920x1080")

        driver = webdriver.Edge(options=options)
        driver.set_page_load_timeout(15)

        print(f"getting url: {url}")
        driver.get(url)
        time.sleep(0.5)
        print("got url")

        elem = driver.find_element(By.TAG_NAME, "body")

        no_of_pagedowns = amount
        while no_of_pagedowns:
            print(f"{no_of_pagedowns:03}", end="\r")
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(1.0)
            no_of_pagedowns -= 1

        soup = bs(driver.page_source, "html.parser")
        driver.quit()

        return soup

    def scrape(
        self,
        show: str,
        short: bool = True,
        amount: int = 100,
    ):
        url = f"https://www.nts.live/shows/{show}"
        if short:
            soup = bs(self.req(url).content, "html.parser")
        else:
            soup = self.browse(url, amount)

        logging.info("Scraping Soup")
        grid = soup.select(".nts-grid-v2")

        def _episode(_grid: list) -> None:
            for i in _grid[0]:
                a = i.select("a")
                if a:
                    href = a[0]["href"].split("/episodes/")
                    if len(href) > 1:
                        episode = href[1]
                        if episode not in self.episodelist.keys():
                            print(f". . . . . . .{episode[-10:]}.", end="\r")
                            self.episodelist[episode] = dict()
                        else:
                            print(f". . . . . . .{episode[-5:]}", end="\r")
                    else:
                        logging.info(f"href failed : {a}")
                else:
                    logging.info(f"href failed : {a}")

        # EPISODES ID
        if not grid:
            raise RuntimeError(
                f"{show} doesn't exist in NTS archive, check show name for upper/lower case"
            )
        else:
            try:
                _episode(grid)
            except:
                soup = self.browse(url, 1)
                _episode(soup.select(".nts-grid-v2"))

            # EPISODES META

            episodemeta = soup.select(".nts-grid-v2-item__content")
            for i in episodemeta:
                sub = i.select(".nts-grid-v2-item__header")[0]
                ep = sub["href"].split("/")[-1]
                date = sub.select("span")[0].text
                eptitle = sub.select(".nts-grid-v2-item__header__title")[0].text
                self.meta[ep] = {"title": eptitle, "date": date}

            # ARTIST IMAGES

            # try:
            imlist = [
                i.split(".")[0] for i in os.listdir(join(src,"jpeg"))
            ]  # IF IN SPOTIFY THEN IMAGE EXISTS
            if show not in imlist:
                # back = soup.select(".background-image")
                back = soup.select(".profile-image")
                if back:
                    # img = re.findall("\((.*?)\)", back[0].get("style"))[0]
                    img = back[0].find("img")["src"].replace("100x100", "1600x1600")
                    logging.info(f"Getting image: {img}")
                    img_data = requests.get(img).content
                    extension = img.split(".")[-1]
                    with open(join(src,"jpeg",f"{show}.{extension}"), "wb") as handler:
                        handler.write(img_data)
                else:
                    logging.info(". . . . . . . . .Image not found.")

            # except Exception:
            #     logging.warning(f"Image Request Failed : {traceback.format_exc()}")

            # ARTIST BIO

            if ("title" not in self.meta) or ("description" not in self.meta):
                bio = soup.select(".bio")
                if bio:
                    title = bio[0].select(".bio__title")[0].select("h1")[0].text
                    desk = bio[0].select(".description")[0].text
                    if not title:
                        logging.info("title-failed")
                        title = show
                    if not desk:
                        logging.info("description-missing")
                        desk = ""
                else:
                    logging.info(". . . . . . . . . .Bio not found")
                    title = show
                    desk = ""
                self.meta["title"] = title
                self.meta["description"] = desk

    @timeout(50.0)
    def req(self, url):
        try:
            res = requests.get(url)
            return res
        except ConnectionError:
            logging.info("Connection Error")
            time.sleep(1.0)
            self.req(url)

    # @monitor
    def ntstracklist(
        self,
        show: str,
        episodes: list = [],
    ):
        if not episodes:
            episodes = self.episodelist

        for episode in episodes:
            try:
                self.meta[episode]
            except:
                logging.info("Meta: New Episode")
                self.meta[episode] = dict()
            try:
                self.episodelist[episode]
            except:
                logging.info("Eplist: New Episode")
                self.episodelist[episode] = dict()
            if (
                (not self.episodelist[episode])
                and (isinstance(self.episodelist[episode], dict))
            ) or (not self.meta[episode]):
                logging.info(episode)
                url = f"https://www.nts.live/shows/{show}/episodes/{episode}"
                soup = bs(self.req(url).content, "html.parser")
                if not self.episodelist[episode]:
                    tracks = soup.select(".track")
                    for j in range(len(tracks)):
                        try:
                            self.episodelist[episode][f"{j:02}"] = {
                                "artist": f"{tracks[j].select('.track__artist')[0].get_text()}",
                                "title": f"{tracks[j].select('.track__title')[0].get_text()}",
                            }
                        except IndexError:
                            logging.info("Index Error")
                            try:
                                self.episodelist[episode][f"{j:02}"] = {
                                    "artist": f"{tracks[j].select('.track__artist')[0].get_text()}",
                                    "title": "",
                                }
                            except IndexError:
                                self.episodelist[episode][f"{j:02}"] = {
                                    "artist": "",
                                    "title": f"{tracks[j].select('.track__title')[0].get_text()}",
                                }
                    if not self.episodelist[episode]:
                        logging.info("fail")
                        self.episodelist[episode] = {}  # NOTE: ""
                    else:
                        logging.info("succ")
                if not self.meta[episode]:
                    logging.info("meta")
                    try:
                        bt = soup.select(".episode__btn")
                        date = bt[0]["data-episode-date"]
                        eptitle = bt[0]["data-episode-name"]
                        self.meta[episode] = {"title": eptitle, "date": date}
                    except:
                        try:
                            logging.info(".trying-once-more-to-find-meta.")
                            soup = self.browse(url, 1)
                            bt = soup.select(".episode__btn")
                            date = bt[0]["data-episode-date"]
                            eptitle = bt[0]["data-episode-name"]
                            self.meta[episode] = {"title": eptitle, "date": date}
                        except:
                            logging.info(
                                f"FAILURE PROCESSING META : {show}:{episode}\n"
                            )
                            self.meta[episode] = {"title": "", "date": "00.00.00"}

        rnw_json(join(src, "tracklist", show), self.episodelist)
        rnw_json(join(src, "meta", show), self.meta)

    def retryepisodes(
        self,
        show: str,
    ):
        save = False
        for i in self.episodelist:
            if not self.episodelist[i]:
                if i in self.uploaded:
                    save = True
                    del self.uploaded[i]
        if save:
            rnw_json(join(src, "uploaded", show), self.uploaded)
