from dataclasses import dataclass

@dataclass
class Chat:
    def __init__(
        self, basic_stats, reactions, emojis, times, people, from_day, to_day, names, title
    ):
        self.basic_stats = basic_stats
        self.reactions = reactions
        self.emojis = emojis
        self.times = times
        self.people = people
        self.from_day = from_day
        self.to_day = to_day
        self.names = names
        self.title = title
