# Standard library imports
import math
import os

# Third party imports
import locale
from jinja2 import Environment, FileSystemLoader


# Application imports
from __init__ import __version__
from utility import home
from const import TRANSLATION_TABLE, DAYS


# emojis = {"total": 0, "types": {"type": x}, "sent": {"name": {"total": x, "type": y}}}
# reactions = {"total": 0, "types": {}, "gave": {"name": {"total": x, "type": y}}, "got": {"name": {"total": x, "type": y}}}


locale.setlocale(locale.LC_ALL, "")

class Analyzer:
    def __init__(self, chat) -> None:
        self.chat = chat

    def mrHtml(self):
        """Imports stats and other variables into HTML"""
        file_loader = FileSystemLoader(home / ".." / "resources" / "templates")
        env = Environment(loader=file_loader)
        env.filters["space"] = self.s

        (people, photos, gifs, stickers, videos, audios, files) = self.chat.basic_stats
        (hours, days, weekdays, months, years) = self.chat.times

        template = env.get_template("index.html.j2")

        days_names = DAYS
        labels, data, background, border = self.msgGraph(people)

        return template.render(
            # utility
            chartjs="../node_modules/chart.js/dist/Chart.js",
            chartjs_labels="../node_modules/chartjs-plugin-labels/src/chartjs-plugin-labels.js",
            participants=len(self.chat.names),
            version=__version__,
            fromDay=self.chat.from_day,
            toDay=self.chat.to_day,
            # names
            title=self.chat.title,
            names=self.chat.names,
            splits=self.splitNames(),
            # pictures
            pictures=self.getPics(),
            # stats
            messages=people,
            images=photos,
            gifs=gifs,
            videos=videos,
            stickers=stickers,
            audios=audios,
            files=files,
            # personalstats
            lines=self.persStatsCount()[0],
            left=self.persStatsCount()[1],
            leftEmojis=self.emojiStatsCount(),
            # messagesgraph
            labels=labels,
            data=data,
            background=background,
            border=border,
            # timestats
            topDay=self.topTimes(days),
            topWeekday=[
                days_names[self.topTimes(weekdays)[0]],
                self.topTimes(weekdays)[1],
            ],
            topMonth=self.topTimes(months),
            topYear=self.topTimes(years),
            # daysgraph
            days=list(days.values()),
            daysLab=self.monthLabel(days),
            stepSizeY=self.stepSize(days),
            # hourgraph
            hours=list(hours.values()),
            hoursLab=list(hours.keys()),
            stepSizeYh=self.stepSize(hours),
            # emojis
            emojisCount=self.chat.emojis,
            diffEmojis=self.countTypes(self.chat.emojis, "sent"),
            avgEmojis=self.avgCounts(self.chat.emojis, "sent"),
            topEmojis=self.topEmojis(self.chat.emojis, "sent"),
            emojisL=self.topsCount(self.chat.emojis, "sent"),
            # reactions
            reacsCount=self.chat.reactions,
            diffReacsGave=self.countTypes(self.chat.reactions, "gave"),
            avgReacs=self.avgCounts(self.chat.reactions, "gave"),
            topReacs=self.topEmojis(self.chat.reactions, "got"),
            reacsL=self.topsCount(self.chat.reactions, "got"),
        )

    def s(self, n):
        """Splits number by thousands with a space"""
        return "{0:n}".format(n) if n != 1 else n

    def msgGraph(self, people):
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
        if len(self.chat.names) == 2:
            labels = [self.chat.names[1], self.chat.names[0]]
            data = [people[self.chat.names[1]], people[self.chat.names[0]]]
            bg = background[0:2]
            bo = border[0:2]
        else:
            for n in sorted(people.items(), key=lambda item: item[1], reverse=True)[
                1:10
            ]:
                labels.append(n[0])
                data.append(n[1])
                bg = background[0:9]
                bo = border[0:9]
            if len(self.chat.names) > 9:
                labels.append("Others")
                sofar = sum(data)
                data.append(people["total"] - sofar)
                bg.append(background[9])
                bo.append(border[9])
        return labels, data, background, border

    def changeName(self, name: str) -> str:
        """Removes non-english characters from a name"""
        return name.translate(TRANSLATION_TABLE).lower()

    def splitNames(self):
        """Splits names and takes just the first name

        :param names: list of names that should be split
        """
        splits = {}
        for n in self.chat.names:
            splits[n] = n.split()[0]
        return splits

    def getPics(self) -> "dict[str, str]":
        """Collects the available profile pics or uses a placeholder picture instead

        :param names: names of the people whose profile pics should be collected
        :return: dict of people and paths to their profile pics
        """
        pics = {}
        for n in self.chat.names:
            pics[n] = "../resources/images/placeholder.jpg"
            for p in os.listdir(home / ".." / "resources" / "images"):
                if p.startswith(self.changeName(n)):
                    pics[n] = "../resources/images/p"
        return pics

    def stepSize(self, times: list) -> float:
        """Calculates the desired step size for the time chart"""
        x = sorted(times.items(), key=lambda item: item[1], reverse=True)[0][1]
        if x < 100:
            y = x if x % 10 == 0 else x + 10 - x % 10
        elif x > 100:
            y = x if x % 100 == 0 else x + 100 - x % 100
        return y / 2

    def monthLabel(self, times: list):
        """Creates labels for the time chart"""
        l = list(times.keys())
        for i in range(len(l)):
            l[i] = l[i][:7]
        return l

    def topEmojisTotal(self, to_count):
        """Prepares top emojis for the HTML"""
        l = sorted(to_count["types"].items(), key=lambda item: item[1], reverse=True)
        types = []
        counts = []
        for e in l:
            types.append(e[0])
            counts.append(e[1])
        return [types[:10], counts[:10]]

    def topEmojisPersonal(self, to_count, name: str, keyword: str):
        """Prepares personal top emojis for the HTML"""
        l = sorted(
            to_count[keyword][name].items(),
            key=lambda item: item[1],
            reverse=True,
        )
        types = []
        counts = []
        for e in l:
            types.append(e[0])
            counts.append(e[1])
        return [types[1:11], counts[1:11]]

    def topEmojis(self, to_count, keyword: str):
        """Packs the overall and top emojis for the HTML"""
        fontSizesT = list(map(str, range(300, 100, -20)))
        fontSizesP = list(map(str, range(180, 80, -10)))
        tops = {
            "total": zip(
                self.topEmojisTotal(to_count)[0],
                self.topEmojisTotal(to_count)[1],
                fontSizesT,
            )
        }
        for n in self.chat.names:
            tops[n] = zip(
                self.topEmojisPersonal(to_count, n, keyword)[0],
                self.topEmojisPersonal(to_count, n, keyword)[1],
                fontSizesP,
            )
        return tops

    def topTimes(self, time):
        """Gets the top time (year, month...) and messages in there"""
        return [
            sorted(time.items(), key=lambda item: item[1], reverse=True)[0][0],
            sorted(time.items(), key=lambda item: item[1], reverse=True)[0][1],
        ]

    def countTypes(self, to_count, keyword: str):
        """Gets the count of different emojis or reactions"""
        lens = {"total": len(to_count["types"])}
        for n in self.chat.names:
            lens[n] = len(to_count[keyword][n]) - 1
        return lens

    def avgCounts(self, to_count, keyword: str):
        """Gets the average of sent emojis or reactions"""
        avgs = {}
        for n in self.chat.names:
            avgs[n] = (
                round(to_count[keyword][n]["total"] / self.chat.people[n], 2)
                if self.chat.people[n] != 0
                else 0
            )
        return avgs

    def topsCount(self, to_count, keyword: str):
        """Gets the number of top emojis or reactions up to 10"""
        count = {"total": len(self.topEmojisTotal(to_count)[0])}
        for n in self.chat.names:
            count[n] = len(self.topEmojisPersonal(to_count, n, keyword)[0])
        return count

    def persStatsCount(self):
        """Calculates how many lines of personal stats are needed in the HTML"""
        if len(self.chat.names) > 2:
            lines = math.floor((len(self.chat.names) - 2) / 3)
            left = (len(self.chat.names) - 2) - (lines * 3)
            x = -len(self.chat.names) if left == 0 else left
            return [lines, x]
        else:
            return [0, 0]

    def emojiStatsCount(self) -> int:
        """Calculates how many lines of emojis and reactions stats are needed in the HTML"""
        if len(self.chat.names) % 2 == 0:
            return -len(self.chat.names)
        else:
            return 1
