# Standard library imports
import math
import os
from typing import Any

# Third party imports
import locale
from jinja2 import Environment, FileSystemLoader

# Application imports
from __init__ import __version__
from utils.utility import html_spaces, home, change_name
from utils.const import DAYS
from chats.chat import Chat, Times, BasicStats


# emojis = {"total": 0, "types": {"type": x}, "sent": {"name": {"total": x, "type": y}}}
# reactions = {"total": 0, "types": {}, "gave": {"name": {"total": x, "type": y}}, "got": {"name": {"total": x, "type": y}}}


locale.setlocale(locale.LC_ALL, "")


class Analyzer:
    def __init__(self, chat: Chat) -> None:
        self.chat = chat

    # region Public API

    def mrHtml(self):
        """Exports stats and other variables into HTML"""
        file_loader = FileSystemLoader(home / "resources" / "templates")
        env = Environment(loader=file_loader)
        env.filters["space"] = html_spaces

        (people, photos, gifs, stickers, videos, audios, files) = self.chat.basic_stats
        (hours, days, weekdays, months, years) = self.chat.times

        template = env.get_template("index.html.j2")

        days_names = DAYS
        labels, data, background, border = self._msg_graph(people)

        return template.render(
            # utility
            # needs to be relative path from the output directory inside HTML
            chartjs="../node_modules/chart.js/dist/Chart.js",
            chartjs_labels="../node_modules/chartjs-plugin-labels/src/chartjs-plugin-labels.js",
            participants=len(self.chat.names),
            version=__version__,
            from_day=self.chat.from_day,
            to_day=self.chat.to_day,
            # names
            title=self.chat.title,
            names=self.chat.names,
            splits=self._split_names(),
            # pictures
            pictures=self._get_pics(),
            # stats
            messages=people,
            images=photos,
            gifs=gifs,
            videos=videos,
            stickers=stickers,
            audios=audios,
            files=files,
            # personalstats
            lines=self._pers_stats_count()[0],
            left=self._pers_stats_count()[1],
            left_emojis=self._emoji_stats_count(),
            # messagesgraph
            labels=labels,
            data=data,
            background=background,
            border=border,
            # timestats
            top_day=self._top_times(days),
            top_weekday=[days_names[self._top_times(weekdays)[0]], self._top_times(weekdays)[1]],
            top_month=self._top_times(months),
            top_year=self._top_times(years),
            # daysgraph
            days=list(days.values()),
            days_lab=self._month_label(days),
            step_size_Y=self._step_size(days),
            # hourgraph
            hours=list(hours.values()),
            hours_lab=list(hours.keys()),
            step_size_Yh=self._step_size(hours),
            # emojis
            emojis_count=self.chat.emojis,
            diff_emojis=self._count_types(self.chat.emojis, "sent"),
            avg_emojis=self._avg_counts(self.chat.emojis, "sent"),
            top_emojis=self._top_emojis(self.chat.emojis, "sent"),
            emojis_L=self._tops_count(self.chat.emojis, "sent"),
            # reactions
            reacts_count=self.chat.reactions,
            diff_reacts_gave=self._count_types(self.chat.reactions, "gave"),
            avg_reacts=self._avg_counts(self.chat.reactions, "gave"),
            top_reacts=self._top_emojis(self.chat.reactions, "got"),
            reacts_L=self._tops_count(self.chat.reactions, "got"),
        )

    def emoji_stats(self, emojis: dict, names, people) -> dict:
        """Prepares emoji stats for terminal output

        :param emojis: dict with structure
                    {"total": 0, "types": {"type": x}, "sent": {"name": {"total": x, "type": y}}}
        :param names:
        :param people:
        :return: dictionary with emoji stats
        """
        sents = {}
        sents_avg = {}

        for n in names:
            sents[n] = emojis["sent"][n]["total"]
            sents_avg[n] = round(emojis["sent"][n]["total"] / people[n], 2)

        stats = {
            "1) total emojis": emojis["total"],
            "2) total different emojis": len(emojis["types"]),
            "3) top emojis": sorted(emojis["types"].items(), key=lambda item: item[1], reverse=True)[0:5],
            "4) sent most emojis": sorted(sents.items(), key=lambda item: item[1], reverse=True)[0],
            "5) sent most emojis on avg": sorted(sents_avg.items(), key=lambda item: item[1], reverse=True)[0],
        }

        for n in names:
            stats[n] = {
                "total": sents[n],
                "avg": sents_avg[n],
                "dif": len(emojis["sent"][n]) - 1,
                "top": sorted(emojis["sent"][n].items(), key=lambda item: item[1], reverse=True)[1:6],
            }

        return stats

    def time_stats(self, times: Times):
        """Creates time stats for terminal output

        :param times: namedtuple of [hours, days, weekdays, months, years]
        :return: dictionary of time stats
        """
        wd_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}

        top_day = sorted(times.days.items(), key=lambda item: item[1], reverse=True)[0]
        top_wd = sorted(times.weekdays.items(), key=lambda item: item[1], reverse=True)[0]
        top_month = sorted(times.months.items(), key=lambda item: item[1], reverse=True)[0]
        top_year = sorted(times.years.items(), key=lambda item: item[1], reverse=True)[0]

        stats = {
            "1) The top day": [top_day[0], f"{top_day[1]} messages"],
            "2) Top hours of day": sorted(times[0].items(), key=lambda item: item[1], reverse=True)[0:3],
            "3) Top weekday": [wd_names[top_wd[0]], top_wd[1]],
            "4) Top month": top_month,
            "5) Top year": top_year,
        }
        return stats

    def chat_stats(self, basic_stats: BasicStats, names: "list[str]") -> "dict[str, Any]":
        """Creates basic chat stats for a terminal output

        :param basic_stats: tuple of [people, photos, gifs, stickers, videos, audios, files]
        :param names: list of names of participants in the conversation
        :return: dictionary of conversation stats
        """
        info = {
            "1) Total messages": basic_stats.people["total"],
            "2) Total audios": basic_stats.audios["total"],
            "3) Total files": basic_stats.files["total"],
            "4) Total gifs": basic_stats.gifs["total"],
            "5) Total images": basic_stats.photos["total"],
            "6) Total stickers": basic_stats.stickers["total"],
            "7) Total videos": basic_stats.videos["total"],
        }
        for n in names:
            if n in basic_stats.people:
                info[n] = basic_stats.people[n]
                info[f"{n} %"] = round(basic_stats.people[n] / basic_stats.people["total"] * 100, 2)
            if n in basic_stats.photos:
                info[n + " images"] = basic_stats.photos[n]
            if n in basic_stats.gifs:
                info[n + " gifs"] = basic_stats.gifs[n]
            if n in basic_stats.videos:
                info[n + " videos"] = basic_stats.videos[n]
            if n in basic_stats.stickers:
                info[n + " stickers"] = basic_stats.stickers[n]
            if n in basic_stats.audios:
                info[n + " audio"] = basic_stats.audios[n]
            if n in basic_stats.files:
                info[n + " files"] = basic_stats.files[n]

        return info

    def reaction_stats(self, reactions: dict, names, people):
        """Creates reaction stats for a terminal output

        :param reactions: dictionary with structure
                        {"total": 0, "types": {}, "gave": {"name": {"total": x, "type": y}}, "got": {"name": {"total": x, "type": y}}}
        :param names:
        :param people:
        :return: dictionary of reaction stats
        """
        gaves = {}
        gots = {}
        gots_avg = {}

        for n in names:
            gaves[n] = reactions["gave"][n]["total"]
            gots[n] = reactions["got"][n]["total"]
            gots_avg[n] = round(reactions["got"][n]["total"] / people[n], 2)

        stats = {
            "1) total reactions": reactions["total"],
            "2) total different reactions": len(reactions["types"]),
            "3) top reactions": sorted(reactions["types"].items(), key=lambda item: item[1], reverse=True)[0:5],
            "4) got most reactions": sorted(gots.items(), key=lambda item: item[1], reverse=True)[0],
            "5) got most reactions on avg": sorted(gots_avg.items(), key=lambda item: item[1], reverse=True)[0],
            "6) gave most reactions": sorted(gaves.items(), key=lambda item: item[1], reverse=True)[0],
        }

        for n in names:
            stats[n] = {
                "total got": gots[n],
                "avg got": gots_avg[n],
                "dif got": len(reactions["got"][n]) - 1,
                "top got": sorted(reactions["got"][n].items(), key=lambda item: item[1], reverse=True)[1:4],
                "total gave": gaves[n],
                "dif gave": len(reactions["gave"][n]) - 1,
                "top gave": sorted(reactions["gave"][n].items(), key=lambda item: item[1], reverse=True)[1:4],
            }

        return stats

    # endregion

    # region utilities

    def _msg_graph(self, people):
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
            for n in sorted(people.items(), key=lambda item: item[1], reverse=True)[1:10]:
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

    def _split_names(self) -> "dict[str, str]":
        """Splits names and takes just the first name

        :return: dict {full name: first name}
        """
        splits = {}
        for n in self.chat.names:
            splits[n] = n.split()[0]
        return splits

    def _get_pics(self) -> "dict[str, str]":
        """Collects the available profile pics or uses a placeholder picture instead

        :return: dict of people and paths to their profile pics
        """
        pics = {}
        for n in self.chat.names:
            # needs to be relative path from the output directory inside HTML
            pics[n] = "../resources/images/placeholder.jpg"
            for p in os.listdir(home / "resources" / "images"):
                if p.startswith(change_name(n)):
                    pics[n] = "../resources/images/p"
        return pics

    @staticmethod
    def _step_size(times) -> float:
        """Calculates the desired step size for the time chart"""
        x = sorted(times.items(), key=lambda item: item[1], reverse=True)[0][1]
        if x < 100:
            y = x if x % 10 == 0 else x + 10 - x % 10
        elif x > 100:
            y = x if x % 100 == 0 else x + 100 - x % 100
        return y / 2

    @staticmethod
    def _month_label(times):
        """Creates labels for the time chart"""
        l = list(times.keys())
        for i in range(len(l)):
            l[i] = l[i][:7]
        return l

    def _top_emojis_total(self, to_count):
        """Prepares top emojis for the HTML"""
        l = sorted(to_count["types"].items(), key=lambda item: item[1], reverse=True)
        types = []
        counts = []
        for e in l:
            types.append(e[0])
            counts.append(e[1])
        return [types[:10], counts[:10]]

    def _top_emojis_personal(self, to_count, name: str, keyword: str):
        """Prepares personal top emojis for the HTML"""
        l = sorted(to_count[keyword][name].items(), key=lambda item: item[1], reverse=True)
        types = []
        counts = []
        for e in l:
            types.append(e[0])
            counts.append(e[1])
        return [types[1:11], counts[1:11]]

    def _top_emojis(self, to_count, keyword: str):
        """Packs the overall and top emojis for the HTML"""
        fontSizesT = list(map(str, range(300, 100, -20)))
        fontSizesP = list(map(str, range(180, 80, -10)))
        tops = {"total": zip(self._top_emojis_total(to_count)[0], self._top_emojis_total(to_count)[1], fontSizesT)}
        for n in self.chat.names:
            tops[n] = zip(
                self._top_emojis_personal(to_count, n, keyword)[0],
                self._top_emojis_personal(to_count, n, keyword)[1],
                fontSizesP,
            )
        return tops

    def _top_times(self, time):
        """Gets the top time (year, month...) and messages in there"""
        return [
            sorted(time.items(), key=lambda item: item[1], reverse=True)[0][0],
            sorted(time.items(), key=lambda item: item[1], reverse=True)[0][1],
        ]

    def _count_types(self, to_count, keyword: str):
        """Gets the count of different emojis or reactions"""
        lens = {"total": len(to_count["types"])}
        for n in self.chat.names:
            lens[n] = len(to_count[keyword][n]) - 1
        return lens

    def _avg_counts(self, to_count, keyword: str):
        """Gets the average of sent emojis or reactions"""
        avgs = {}
        for n in self.chat.names:
            avgs[n] = round(to_count[keyword][n]["total"] / self.chat.people[n], 2) if self.chat.people[n] != 0 else 0
        return avgs

    def _tops_count(self, to_count, keyword: str):
        """Gets the number of top emojis or reactions up to 10"""
        count = {"total": len(self._top_emojis_total(to_count)[0])}
        for n in self.chat.names:
            count[n] = len(self._top_emojis_personal(to_count, n, keyword)[0])
        return count

    def _pers_stats_count(self):
        """Calculates how many lines of personal stats are needed in the HTML"""
        if len(self.chat.names) > 2:
            lines = math.floor((len(self.chat.names) - 2) / 3)
            left = (len(self.chat.names) - 2) - (lines * 3)
            x = -len(self.chat.names) if left == 0 else left
            return [lines, x]
        else:
            return [0, 0]

    def _emoji_stats_count(self) -> int:
        """Calculates how many lines of emojis and reactions stats are needed in the HTML"""
        if len(self.chat.names) % 2 == 0:
            return -len(self.chat.names)
        else:
            return 1

    # endregion
