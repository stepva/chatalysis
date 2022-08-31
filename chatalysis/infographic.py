# Standard library imports
import locale
import os
import math

# Third party imports
from jinja2 import Environment, FileSystemLoader

# Application imports
from utility import home
from const import TRANSLATION_TABLE
from const import DAYS


# emojis = {"total": 0, "types": {"type": x}, "sent": {"name": {"total": x, "type": y}}}
# reactions = {"total": 0, "types": {}, "gave": {"name": {"total": x, "type": y}}, "got": {"name": {"total": x, "type": y}}}
locale.setlocale(locale.LC_ALL, "")

translation_table = str.maketrans(TRANSLATION_TABLE)


def mrHtml(version, names, basicStats, fromDay, toDay, times, emojis, reactions, title):
    """Imports stats and other variables into HTML"""
    file_loader = FileSystemLoader(home / ".." / "resources" / "templates")
    env = Environment(loader=file_loader)
    env.filters["space"] = s

    (people, photos, gifs, stickers, videos, audios, files) = basicStats
    (hours, days, weekdays, months, years) = times

    template = env.get_template("index.html.j2")

    days_names = DAYS
    labels, data, background, border = msgGraph(names, people)

    return template.render(
        # utility
        chartjs="../node_modules/chart.js/dist/Chart.js",
        chartjs_labels="../node_modules/chartjs-plugin-labels/src/chartjs-plugin-labels.js",
        participants=len(names),
        version=version,
        fromDay=fromDay,
        toDay=toDay,
        # names
        title=title,
        names=names,
        splits=splitNames(names),
        # pictures
        pictures=getPics(names),
        # stats
        messages=people,
        images=photos,
        gifs=gifs,
        videos=videos,
        stickers=stickers,
        audios=audios,
        files=files,
        # personalstats
        lines=persStatsCount(names)[0],
        left=persStatsCount(names)[1],
        leftEmojis=emojiStatsCount(names),
        # messagesgraph
        labels=labels,
        data=data,
        background=background,
        border=border,
        # timestats
        topDay=topTimes(days),
        topWeekday=[days_names[topTimes(weekdays)[0]], topTimes(weekdays)[1]],
        topMonth=topTimes(months),
        topYear=topTimes(years),
        # daysgraph
        days=list(days.values()),
        daysLab=monthLabel(days),
        stepSizeY=stepSize(days),
        # hourgraph
        hours=list(hours.values()),
        hoursLab=list(hours.keys()),
        stepSizeYh=stepSize(hours),
        # emojis
        emojisCount=emojis,
        diffEmojis=countTypes(names, emojis, "sent"),
        avgEmojis=avgCounts(names, people, emojis, "sent"),
        topEmojis=topEmojis(emojis, names, "sent"),
        emojisL=topsCount(names, emojis, "sent"),
        # reactions
        reacsCount=reactions,
        diffReacsGave=countTypes(names, reactions, "gave"),
        avgReacs=avgCounts(names, people, reactions, "gave"),
        topReacs=topEmojis(reactions, names, "got"),
        reacsL=topsCount(names, reactions, "got"),
    )


def s(n):
    """Splits number by thousands with a space"""
    return "{0:n}".format(n) if n != 1 else n


def changeName(name: str) -> str:
    """Removes non-english characters from a name"""
    return name.translate(translation_table).lower()


def splitNames(names: "list[str]"):
    """Splits names and takes just the first name

    :param names: list of names that should be split
    """
    splits = {}
    for n in names:
        splits[n] = n.split()[0]
    return splits


def getPics(names: "list[str]") -> "dict[str, str]":
    """Collects the available profile pics or uses a placeholder picture instead

    :param names: names of the people whose profile pics should be collected
    :return: dict of people and paths to their profile pics
    """
    pics = {}
    for n in names:
        pics[n] = "../resources/images/placeholder.jpg"
        for p in os.listdir(home / ".." / "resources" / "images"):
            if p.startswith(changeName(n)):
                pics[n] = "../resources/images/p"
    return pics


def stepSize(days) -> float:
    """Calculates the desired step size for the time chart"""
    x = sorted(days.items(), key=lambda item: item[1], reverse=True)[0][1]
    if x < 100:
        y = x if x % 10 == 0 else x + 10 - x % 10
    elif x > 100:
        y = x if x % 100 == 0 else x + 100 - x % 100
    return y / 2


def monthLabel(days):
    """Creates labels for the time chart"""
    l = list(days.keys())
    for i in range(len(l)):
        l[i] = l[i][:7]
    return l


def topEmojisTotal(emojis):
    """Prepares top emojis for the HTML"""
    l = sorted(emojis["types"].items(), key=lambda item: item[1], reverse=True)
    types = []
    counts = []
    for e in l:
        types.append(e[0])
        counts.append(e[1])
    return [types[:10], counts[:10]]


def topEmojisPersonal(emojis, name, sent):
    """Prepares personal top emojis for the HTML"""
    l = sorted(emojis[sent][name].items(), key=lambda item: item[1], reverse=True)
    types = []
    counts = []
    for e in l:
        types.append(e[0])
        counts.append(e[1])
    return [types[1:11], counts[1:11]]


def topEmojis(emojis, names, sent):
    """Packs the overall and top emojis for the HTML"""
    fontSizesT = list(map(str, range(300, 100, -20)))
    fontSizesP = list(map(str, range(180, 80, -10)))
    tops = {
        "total": zip(topEmojisTotal(emojis)[0], topEmojisTotal(emojis)[1], fontSizesT)
    }
    for n in names:
        tops[n] = zip(
            topEmojisPersonal(emojis, n, sent)[0],
            topEmojisPersonal(emojis, n, sent)[1],
            fontSizesP,
        )
    return tops


def topTimes(time):
    """Gets the top time (year, month...) and messages in there"""
    return [
        sorted(time.items(), key=lambda item: item[1], reverse=True)[0][0],
        sorted(time.items(), key=lambda item: item[1], reverse=True)[0][1],
    ]


def countTypes(names, emojis, sent):
    """Gets the count of different emojis or reactions"""
    lens = {"total": len(emojis["types"])}
    for n in names:
        lens[n] = len(emojis[sent][n]) - 1
    return lens


def avgCounts(names, people, emojis, sent):
    """Gets the average of sent emojis or reactions"""
    avgs = {}
    for n in names:
        avgs[n] = (
            round(emojis[sent][n]["total"] / people[n], 2) if people[n] != 0 else 0
        )
    return avgs


def topsCount(names, emojis, sent):
    """Gets the number of top emojis or reactions up to 10"""
    count = {"total": len(topEmojisTotal(emojis)[0])}
    for n in names:
        count[n] = len(topEmojisPersonal(emojis, n, sent)[0])
    return count


def persStatsCount(names):
    """Calculates how many lines of personal stats are needed in the HTML"""
    if len(names) > 2:
        lines = math.floor((len(names) - 2) / 3)
        left = (len(names) - 2) - (lines * 3)
        x = -len(names) if left == 0 else left
        return [lines, x]
    else:
        return [0, 0]


def emojiStatsCount(names):
    """Calculates how many lines of emojis and reactions stats are needed in the HTML"""
    if len(names) % 2 == 0:
        return -len(names)
    else:
        return 1


def msgGraph(names, people):
    """Prepares labels and data for the messages graph"""
    labels = []
    data = []
    background = [
        "hsla(42, 79%, 54%, 0.4)",
        "hsla(45, 98%, 67%, 0.2)",
        "hsla(42, 79%, 54%, 0.6)",
        "hsla(45, 98%, 67%, 0.4)",
        "hsla(42, 79%, 54%, 0.8)",
        "hsla(45, 98%, 67%, 0.6)",
        "hsla(42, 79%, 54%, 1)",
        "hsla(45, 98%, 67%, 0.8)",
        "hsla(69, 100%, 66%, 0.6)",
        "hsla(17, 80%, 66%, 0.5)",
    ]
    border = ["hsla(53, 0%, 0%, 0.5)"] * 10
    if len(names) == 2:
        labels = [names[1], names[0]]
        data = [people[names[1]], people[names[0]]]
        bg = background[0:2]
        bo = border[0:2]
    else:
        for n in sorted(people.items(), key=lambda item: item[1], reverse=True)[1:10]:
            labels.append(n[0])
            data.append(n[1])
            bg = background[0:9]
            bo = border[0:9]
        if len(names) > 9:
            labels.append("Others")
            sofar = sum(data)
            data.append(people["total"] - sofar)
            bg.append(background[9])
            bo.append(border[9])
    return labels, data, background, border
