"""

Description: Web scraping & Connections
Authors: GAMM
Version: 1
Year: 2023-09-02

"""

# .1 Standard Libraries
import os
import re
import time
import pickle
import logging
import requests
import traceback
from threading import Lock

# .2 Local
import utils

# .3 HTML PARSER
from bs4 import BeautifulSoup as bs

# .4 BROWSER
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# from webdriver.chrome.service import Service

# .5 SPOTIFY API TOOL
import spotipy

# .6 LOCK
lock = Lock()


class connection:
    def __init__(self):
        pass

    # SPOTIFY API

    @utils.timeout(20.0)
    def subconnect(self, index, pick):
        """CONNECTION FUNCTION w/ TIMEOUT"""
        self.user = os.getenv("ssr")
        callback = "http://localhost:8888/callback"
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
                username=self.user,
            ),
            requests_timeout=5,
            retries=10,
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
            with open("./pickle/spotipywebapi.pickle", "rb") as handle:
                pick = pickle.load(handle)
            logging.warning(index[pick])
            self.subconnect(index, pick)
            time.sleep(1.0)
            lock.release()
        except Exception:
            self.conexcp()

    def conexcp(self):
        """CLEAR CACHE IF CONNECTION ERROR/TIMEOUT & TRY AGAIN"""
        time.sleep(3.0)
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
            logging.warning(". Unsuccessful .")
            dr = os.listdir()
            if ".cache-31yeoenly5iu5pvoatmuvt7i7ksy" in dr:
                os.remove(".cache-31yeoenly5iu5pvoatmuvt7i7ksy")

            if "spotipywebapi.pickle" not in os.listdir("./pickle"):
                with open("./pickle/spotipywebapi.pickle", "wb") as handle:
                    pickle.dump(0, handle, protocol=pickle.HIGHEST_PROTOCOL)

            with open("./pickle/spotipywebapi.pickle", "rb") as handle:
                pick = pickle.load(handle)
            pick += 1
            if pick == (len(index) - 1):
                pick = 0

            logging.info(index[pick])

            with open("./pickle/spotipywebapi.pickle", "wb") as handle:
                pickle.dump(pick, handle, protocol=pickle.HIGHEST_PROTOCOL)

            self.subconnect(index, pick)
            time.sleep(1.0)
            lock.release()

        except Exception:
            self.conexcp()


class webscraper:
    def __init__(self):
        pass

    def browse(self, url, amount=100):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.headless = True
        driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=options,
        )

        driver.get(url)
        time.sleep(1.0)

        elem = driver.find_element(By.TAG_NAME, "body")
        no_of_pagedowns = amount
        while no_of_pagedowns:
            print(f"{no_of_pagedowns:03}", end="\r")
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
            no_of_pagedowns -= 1
        time.sleep(0.5)
        soup = bs(driver.page_source, "html.parser")
        driver.quit()
        return soup

    def scrape(self, show, short=False, amount=100):
        url = f"https://www.nts.live/shows/{show}"
        if short:
            soup = bs(self.req(url).content, "html.parser")
        else:
            soup = self.browse(url, amount)

        logging.info("Scraping Soup")
        grid = soup.select(".nts-grid-v2")
        # EPISODES ID
        if not grid:
            raise RuntimeError(
                f"{show} doesn't exist in NTS archive, check show name for upper/lower case"
            )
        else:
            try:
                for i in grid[0]:
                    a = i.select("a")
                    if a:
                        href = a[0]["href"]
                        episode = href.split("/episodes/")[1]
                        if episode not in self.episodelist.keys():
                            print(f". . . . . . .{episode[-10:]}.", end="\r")
                            self.episodelist[episode] = dict()
                        else:
                            print(f". . . . . . .{episode[-5:]}", end="\r")
                    else:
                        logging.info("href failed")
            except:
                soup = self.browse(url, 1)
                grid = soup.select(".nts-grid-v2")
                for i in grid[0]:
                    a = i.select("a")
                    if a:
                        href = a[0]["href"]
                        episode = href.split("/episodes/")[1]
                        if episode not in self.episodelist.keys():
                            print(f". . . . . . .{episode[-10:]}.", end="\r")
                            self.episodelist[episode] = dict()
                        else:
                            print(f". . . . . . .{episode[-5:]}", end="\r")
                    else:
                        logging.info("href failed (again)")

            # EPISODES META

            episodemeta = soup.select(".nts-grid-v2-item__content")
            for i in episodemeta:
                sub = i.select(".nts-grid-v2-item__header")[0]
                ep = sub["href"].split("/")[-1]
                date = sub.select("span")[0].text
                eptitle = sub.select(".nts-grid-v2-item__header__title")[0].text
                self.meta[ep] = {"title": eptitle, "date": date}

            # ARTIST IMAGES

            try:
                imlist = [
                    i.split(".")[0] for i in os.listdir("./spotify/")
                ]  # IF IN SPOTIFY THEN IMAGE EXISTS
                if show not in imlist:
                    try:
                        back = soup.select(".background-image")
                    except:
                        back = soup.select(".profile-image")
                    if back:
                        img = re.findall("\((.*?)\)", back[0].get("style"))[0]
                        img_data = requests.get(img).content
                        extension = img.split(".")[-1]
                        with open(f"./jpeg/{show}.{extension}", "wb") as handler:
                            handler.write(img_data)
                    else:
                        logging.info(". . . . . . . . .Image not found.")

            except Exception:
                logging.warning(f"Image Request Failed : {traceback.format_exc()}")

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

    @utils.timeout(50.0)
    def req(self, url):
        try:
            res = requests.get(url)
            return res
        except ConnectionError:
            logging.info("Connection Error")
            time.sleep(1.0)
            self.req(url)

    @utils.monitor
    def ntstracklist(self, show, episodes=[]):
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

        utils.rnw_json(f"./tracklist/{show}", self.episodelist)
        utils.rnw_json(f"./meta/{show}", self.meta)

    def retryepisodes(self, show):
        save = False
        for i in self.episodelist:
            if not self.episodelist[i]:
                if i in self.uploaded:
                    save = True
                    del self.uploaded[i]
        if save:
            utils.rnw_json(f"./uploaded/{show}", self.uploaded)
