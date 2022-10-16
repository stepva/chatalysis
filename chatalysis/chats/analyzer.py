import math
from typing import Any

from jinja2 import Environment, FileSystemLoader

from __init__ import __version__
from chats.charts.plotly_messages import daily_messages_bar, hourly_messages_line, messages_pie
from chats.stats import Stats, Times
from utils.const import DAYS
from utils.utility import list_folder, html_spaces, change_name, home

# emojis = {"total": 0, "types": {"type": x}, "sent": {"name": {"total": x, "type": y}}}
# reactions = {"total": 0, "types": {}, "gave": {"name": {"total": x, "type": y}}, "got": {"name": {"total": x, "type": y}}}


class Analyzer:
    def __init__(self, chat: Stats) -> None:
        self.chat = chat

    # region Public API

    def mrHtml(self):
        """Exports chat stats and other variables into HTML"""
        file_loader = FileSystemLoader(home / "resources" / "templates")
        env = Environment(loader=file_loader)
        env.filters["space"] = html_spaces

        (hours, days, weekdays, months, years) = self.chat.times

        template = env.get_template("chat.html.j2")

        return template.render(
            # utility
            participants=len(self.chat.participants),
            version=__version__,
            from_day=self.chat.from_day,
            to_day=self.chat.to_day,
            # names
            title=self.chat.title,
            names=self.chat.participants,
            splits=self._split_names(),
            # pictures
            pictures=self._get_pics(),
            # stats
            messages=self.chat.people,
            images=self.chat.photos,
            gifs=self.chat.gifs,
            videos=self.chat.videos,
            stickers=self.chat.stickers,
            audios=self.chat.audios,
            files=self.chat.files,
            # personal stats
            lines=self._pers_stats_count()[0],
            left=self._pers_stats_count()[1],
            left_emojis=self._emoji_stats_count(),
            # messages graph
            messages_pie=messages_pie(self.chat.people),
            # time stats
            top_day=self._top_times(days),
            top_weekday=[DAYS[self._top_times(weekdays)[0]], self._top_times(weekdays)[1]],
            top_month=self._top_times(months),
            top_year=self._top_times(years),
            # days graph
            daily_messages_bar=daily_messages_bar(days),
            # hour graph
            hourly_messages_line=hourly_messages_line(hours),
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
            # chat type
            chat_type=self.chat.stats_type.value,
        )

    def personalHtml(self):
        """Exports personal stats and other variables into HTML"""
        file_loader = FileSystemLoader(home / "resources" / "templates")
        env = Environment(loader=file_loader)
        env.filters["space"] = html_spaces

        (hours, days, weekdays, months, years) = self.chat.times

        template = env.get_template("personal.html.j2")

        return template.render(
            # utility
            version=__version__,
            from_day=self.chat.from_day,
            to_day=self.chat.to_day,
            # names
            title=self.chat.title,
            names=self.chat.participants,
            # pictures
            pictures=self._get_pics(),
            # stats
            messages=self.chat.people,
            images=self.chat.photos,
            gifs=self.chat.gifs,
            videos=self.chat.videos,
            stickers=self.chat.stickers,
            audios=self.chat.audios,
            files=self.chat.files,
            # time stats
            top_day=self._top_times(days),
            top_weekday=[DAYS[self._top_times(weekdays)[0]], self._top_times(weekdays)[1]],
            top_month=self._top_times(months),
            top_year=self._top_times(years),
            # days graph
            daily_messages_bar=daily_messages_bar(days),
            # hour graph
            hourly_messages_line=hourly_messages_line(hours),
            # emojis
            emojis_count=self.chat.emojis,
            diff_emojis=self._count_types(self.chat.emojis, "sent"),
            top_emojis=self._top_emojis(self.chat.emojis, "sent"),
            emojis_L=self._tops_count(self.chat.emojis, "sent"),
            # reactions
            reacts_count=self.chat.reactions,
            diff_reacts_gave=self._count_types(self.chat.reactions, "gave"),
            top_reacts=self._top_emojis(self.chat.reactions, "got"),
            reacts_L=self._tops_count(self.chat.reactions, "got"),
        )

    @staticmethod
    def emoji_stats(emojis: dict, names, people) -> dict:
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

    @staticmethod
    def time_stats(times: Times):
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

    def chat_stats(self, names: "list[str]") -> "dict[str, Any]":
        """Creates basic chat stats for a terminal output

        :param names: list of names of participants in the conversation
        :return: dictionary of conversation stats
        """
        info = {
            "1) Total messages": self.chat.people["total"],
            "2) Total audios": self.chat.audios["total"],
            "3) Total files": self.chat.files["total"],
            "4) Total gifs": self.chat.gifs["total"],
            "5) Total images": self.chat.photos["total"],
            "6) Total stickers": self.chat.stickers["total"],
            "7) Total videos": self.chat.videos["total"],
        }
        for n in names:
            if n in self.chat.people:
                info[n] = self.chat.people[n]
                info[f"{n} %"] = round(self.chat.people[n] / self.chat.people["total"] * 100, 2)
            if n in self.chat.photos:
                info[n + " images"] = self.chat.photos[n]
            if n in self.chat.gifs:
                info[n + " gifs"] = self.chat.gifs[n]
            if n in self.chat.videos:
                info[n + " videos"] = self.chat.videos[n]
            if n in self.chat.stickers:
                info[n + " stickers"] = self.chat.stickers[n]
            if n in self.chat.audios:
                info[n + " audio"] = self.chat.audios[n]
            if n in self.chat.files:
                info[n + " files"] = self.chat.files[n]

        return info

    @staticmethod
    def reaction_stats(reactions: dict, names, people):
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

    def _split_names(self) -> "dict[str, str]":
        """Splits names and takes just the first name

        :return: dict {full name: first name}
        """
        splits = {}
        for n in self.chat.participants:
            splits[n] = n.split()[0]
        return splits

    def _get_pics(self) -> "dict[str, str]":
        """Collects the available profile pics or uses a placeholder picture instead

        :return: dict of people and paths to their profile pics
        """
        pics = {}
        for n in self.chat.participants:
            # needs to be relative path from the output directory inside HTML
            pics[n] = "../resources/images/placeholder.jpg"
            for p in list_folder(home / "resources" / "images"):
                if p.startswith(change_name(n)):
                    pics[n] = f"../resources/images/{p}"
        return pics

    @staticmethod
    def _top_emojis_total(to_count):
        """Prepares top emojis for the HTML"""
        l = sorted(to_count["types"].items(), key=lambda item: item[1], reverse=True)
        types = []
        counts = []
        for e in l:
            types.append(e[0])
            counts.append(e[1])
        return [types[:10], counts[:10]]

    @staticmethod
    def _top_emojis_personal(to_count, name: str, keyword: str):
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
        for n in self.chat.participants:
            tops[n] = zip(
                self._top_emojis_personal(to_count, n, keyword)[0],
                self._top_emojis_personal(to_count, n, keyword)[1],
                fontSizesP,
            )
        return tops

    @staticmethod
    def _top_times(time):
        """Gets the top time (year, month...) and messages in there"""
        return [
            sorted(time.items(), key=lambda item: item[1], reverse=True)[0][0],
            sorted(time.items(), key=lambda item: item[1], reverse=True)[0][1],
        ]

    def _count_types(self, to_count, keyword: str):
        """Gets the count of different emojis or reactions"""
        lens = {"total": len(to_count["types"])}
        for n in self.chat.participants:
            lens[n] = len(to_count[keyword][n]) - 1
        return lens

    def _avg_counts(self, to_count, keyword: str):
        """Gets the average of sent emojis or reactions"""
        avgs = {}
        for n in self.chat.participants:
            avgs[n] = round(to_count[keyword][n]["total"] / self.chat.people[n], 2) if self.chat.people[n] != 0 else 0
        return avgs

    def _tops_count(self, to_count, keyword: str):
        """Gets the number of top emojis or reactions up to 10"""
        count = {"total": len(self._top_emojis_total(to_count)[0])}
        for n in self.chat.participants:
            count[n] = len(self._top_emojis_personal(to_count, n, keyword)[0])
        return count

    def _pers_stats_count(self):
        """Calculates how many lines of personal stats are needed in the HTML"""
        if len(self.chat.participants) > 2:
            lines = math.floor((len(self.chat.participants) - 2) / 3)
            left = (len(self.chat.participants) - 2) - (lines * 3)
            x = -len(self.chat.participants) if left == 0 else left
            return [lines, x]
        else:
            return [0, 0]

    def _emoji_stats_count(self) -> int:
        """Calculates how many lines of emojis and reactions stats are needed in the HTML"""
        if len(self.chat.participants) % 2 == 0:
            return -len(self.chat.participants)
        else:
            return 1

    # endregion
