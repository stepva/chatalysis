import datetime


class Chat:
    def __init__(
        self, basicStats, reactions, emojis, times, people, fromDay, toDay, names, title
    ):
        self.basicStats = basicStats
        self.reactions = reactions
        self.emojis = emojis
        self.times = times
        self.people = people
        self.fromDay = fromDay
        self.toDay = toDay
        self.names = names
        self.title = title
