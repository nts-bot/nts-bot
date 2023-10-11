"""

Description: Text Analysis
Authors: GAMM
Version: 1
Year: 2023-09-02

"""


# .0 STANDARD LIBRARIES

import os
import logging

# .1 TRANSLATORS
from deep_translator import GoogleTranslator, DeeplTranslator
from unidecode import unidecode

# .2 PARSING NONLATIN SCRIPT & MACHINE LEARNING LANGUAGE IDENTIFICATION MODEL
import unihandecode
import fasttext

# .3 TEXT COMPARISON TOOL
from difflib import SequenceMatcher

# .4 ENVIRONMENT VARIABLES
from dotenv import load_dotenv

print(os.getcwd())

load_dotenv()
deepl = os.getenv("api")


def load_model():
    if "lid_model" not in globals():
        globals()["lid_model"] = fasttext.load_model("./lid.176.ftz")
    else:
        pass


def tbool(tex):
    trans = False
    convert = unidecode(tex)
    ln = globals()["lid_model"].predict(tex)[0][0].split("__label__")[1]
    if ln in ["ja", "zh", "kr", "vn"]:
        d = unihandecode.Unidecoder(lang=ln)
        convert = d.decode(tex)
        trans = True
    elif ln in ["th", "uk", "ru", "sw", "ar", "et", "id", "yi"]:
        trans = True
    return (kill(convert), trans)


def trnslate(tex):
    """TRANSLATE RESULT IF TEXT IS NOT IN LATIN SCRIPT"""
    try:
        return kill(GoogleTranslator(source="auto", target="en").translate(tex[:500]))
    except Exception as error:
        logging.info(f"{error}\r")
        if "server" in error.lower():
            ln = globals()["lid_model"].predict(tex)[0][0].split("__label__")[1]
            return DeeplTranslator(
                api_key=deepl, source=ln, target="en", use_free_api=True
            ).translate(tex[:500])
        else:
            return tex


def ratio(A, B):
    """GET SIMILARITY RATIO BETWEEN TWO STRINGS"""
    return round(SequenceMatcher(None, A, B).ratio(), 4)


def kill(text):
    """ELIMINATE DUPLICATES & UNNECESSARY CHARACTERS WITHIN STRING"""
    cv = (
        text.replace("°", " ")
        .replace("・", " ")
        .replace("+", " ")
        .replace("}", " ")
        .replace("{", " ")
        .replace("|", " ")
        .replace("/", " ")
        .replace("]", " ")
        .replace("[", " ")
        .replace(")", " ")
        .replace("(", " ")
        .replace("'", " ")
        .replace('"', " ")
        .replace("-", " ")
        .replace("!", " ")
        .replace("=", " ")
        .replace(">", " ")
        .replace("<", " ")
        .replace("@", " ")
        .replace("^", " ")
        .replace("~", " ")
        .replace("*", " ")
        .replace("%", " ")
        .replace("#", " ")
        .replace("$", " ")
        .replace("&", " ")
        .replace("_", " ")
        .replace("?", " ")
        .replace("/", " ")
        .replace(";", " ")
        .replace(":", " ")
        .replace(".", " ")
        .replace(",", " ")
        .replace("  ", " ")
        .split(" ")
    )
    return refine(" ".join(dict.fromkeys(cv)).lower()).strip()


def refine(text):
    """ELIMINATE UNNECCESARY WORDS WITHIN STRING"""
    for i in list(range(1900, 2022)):
        text = text.replace(str(i), "")
    return (
        text.replace("yellow magic orchestra", "ymo")
        .replace("selections", "")
        .replace("with ", "")
        .replace("medley", "")
        .replace("vocal", "")
        .replace("previously unreleased", "")
        .replace("remastering", "")
        .replace("remastered", "")
        .replace("various artists", "")
        .replace("vinyl", "")
        .replace("untitled", "")
        .replace("film", "")
        .replace("movie", "")
        .replace("originally", "")
        .replace("from", "")
        .replace("theme", "")
        .replace("motion picture", "")
        .replace("soundtrack", "")
        .replace("full length", "")
        .replace("original", "")
        .replace(" mix ", " mix mix mix ")
        .replace("remix", "remix remix remix")
        .replace("edit", "edit edit edit")
        .replace("live", "live live live")
        .replace("cover", "cover cover cover")
        .replace("acoustic", "acoustic acoustic")
        .replace("demo", "demo demo demo")
        .replace("version", "")
        .replace("ver", "")
        .replace("feat", "")
        .replace("comp", "")
        .replace("vocal", "")
        .replace("instrumental", "")
        .replace("&", "and")
        .replace("0", "zero")
        .replace("1", "one")
        .replace("2", "two")
        .replace("3", "three")
        .replace("4", "four")
        .replace("5", "five")
        .replace("6", "six")
        .replace("7", "seven")
        .replace("8", "eight")
        .replace("9", "nine")
        .replace("excerpt", "")
        .replace("single", "")
        .replace("album", "")
        .replace("intro", "")
        .replace("anonymous", "")
        .replace("unknown", "")
        .replace("traditional", "")
        .replace("  ", " ")
    )


def _ratio(x, y, z=""):
    """RETURN MAX RATIO FROM TEXT COMPARISON"""
    if z:  # Test all
        return [
            max([ratio(x, y), ratio(y, x)]),
            max([ratio(x, z), ratio(z, x)]),
        ]
    else:
        return max([ratio(x, y), ratio(y, x)])


def token(x, y):
    h1 = set(x.replace("s", "").split(" "))
    h2 = set(y.replace("s", "").split(" "))
    X2 = " ".join(h1 - h2).strip()
    Y2 = " ".join(h2 - h1).strip()
    return [X2, Y2]


def subcomp(k1, k2, k3, k4):
    try:
        r = _ratio(k1, k3, k4)
        it = r.index(max(r))  # INDEX (in case AUTHOR switched w/ TITLE)
    except:
        it = 0

    X1 = f"{[k1,k2][it]} {[k2,k1][it]}"
    Y1 = f"{[k3,k4][it]} {[k4,k3][it]}"

    R0 = _ratio(X1, Y1)
    if R0 < 0.85:
        R1 = _ratio(*token(X1, Y1))
        R2, R3 = 0, 0

        if (R1 == 0) and ("" in token(X1, Y1)):
            X2 = f"{[k1,k2][it]}"
            Y2 = f"{[k3,k4][it]}"
            R2 = _ratio(*token(X2, Y2))
            if (R2 == 0) and ("" in token(X2, Y2)):
                X3 = f"{[k2,k1][it]}"
                Y3 = f"{[k4,k3][it]}"
                R3 = _ratio(*token(X3, Y3))
                if (R3 == 0) and ("" in token(X3, Y3)):
                    R = R0
                else:
                    R = R3
            else:
                R = R2
        else:
            R = R1

        if round(R, 1) == 0.6:
            m = [i for i in [R2, R3] if i != 0]
            if m:
                if min(m) < 0.7:
                    R = 0.5
            elif R0 < 0.7:
                R = 0.5
    else:
        R = R0

    return R


def comp(a, b, c, d):  # OA, #OT, #SA, #ST
    """COMPARISON FUNCTION"""

    try:
        k1, t1 = tbool(a)  # O AUTHOR
        k2, t2 = tbool(b)  # O TITLE
        k3, t3 = tbool(c)  # S AUTHOR
        k4, t4 = tbool(d)  # S TITLE

        R = subcomp(k1, k2, k3, k4)

        if (R < 0.6) and any([t1, t2, t3, t4]):
            if t1:  # TRANSLATE
                k1 = trnslate(a)
            if t2:
                k2 = trnslate(b)
            if t3:
                k3 = trnslate(c)
            if t4:
                k4 = trnslate(d)
            R = subcomp(k1, k2, k3, k4)

    except AttributeError:
        R = 0

    return R


def test(search, queryartist, querytitle):
    """TESTING EACH SEARCH RESULT SYSTEMATICALLY, AND RETURNING THE BEST RESULT"""
    load_model()
    if search:
        arts = []
        tits = []
        rats = []
        uris = []
        for t in range(len(search)):
            arts += [search[t]["artist"]]
            tits += [search[t]["title"]]
            uris += [search[t]["uri"]]
            comparison = comp(queryartist, querytitle, arts[t], tits[t])
            rats += [comparison]
        dx = rats.index(max(rats))
        return (arts[dx], tits[dx], rats[dx], uris[dx])
    else:
        return ("", "", 0, "")
