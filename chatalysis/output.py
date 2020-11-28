
# Standard library imports
import locale
import os
# Third party imports
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template


#emojis = {"total": 0, "types": {"type": x}, "sent": {"name": {"total": x, "type": y}}}
#reactions = {"total": 0, "types": {}, "gave": {"name": {"total": x, "type": y}}, "got": {"name": {"total": x, "type": y}}}
locale.setlocale(locale.LC_ALL, '')


def mrHtml(version, names, basicStats, fromDay, toDay, times, emojis, reactions, title):
    file_loader = FileSystemLoader("resources")
    env = Environment(loader=file_loader)
    env.filters['space'] = s

    (people, photos, gifs, stickers, videos, audios, files) = basicStats
    (hours, days, weekdays, months, years) = times

    template = env.get_template('index.html.j2')

    wdNames = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}

    return template.render(
        #utility
        path=os.getcwd(),
        participants=len(names),
        version=version,
        fromDay=fromDay,
        toDay=toDay,

        #names
        title=title,
        names=names,
        splits=splitNames(names),

        #pictures
        pictures=getPics(names),

        #stats
        messages=people,
        images=photos,
        gifs=gifs,
        videos=videos,
        stickers=stickers,
        audios=audios,
        files=files,

        #timestats
        topDay=topTimes(days),
        topWeekday=[wdNames[topTimes(weekdays)[0]], topTimes(weekdays)[1]],
        topMonth=topTimes(months),
        topYear=topTimes(years),

        #daysgraph
        days=list(days.values()),
        daysLab=monthLabel(days),
        stepSizeY=stepSize(days),

        #hourgraph
        hours=list(hours.values()),
        hoursLab=list(hours.keys()),
        stepSizeYh=stepSize(hours),

        #emojis
        emojisCount=emojis,
        diffEmojis=countTypes(names, emojis, "sent"),
        avgEmojis=avgCounts(names, people, emojis, "sent"),
        topEmojis=topEmojis(emojis, names, "sent"),
        emojisL=topsCount(names, emojis, "sent"),

        #reactions
        reacsCount=reactions,
        diffReacsGave=countTypes(names, reactions, "gave"),
        avgReacs=avgCounts(names, people, reactions, "gave"),
        topReacs=topEmojis(reactions, names, "got"),
        reacsL=topsCount(names, reactions, "got"),
    )

def s(n):
    return "{0:n}".format(n) if n != 1 else n

def changeName(name):
    no = 'ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝßàáâãäåçèéêëìíîïñòóôõöùúûüýÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſ'
    yes = 'AAAAAACEEEEIIIINOOOOOUUUUYsaaaaaaceeeeiiiinooooouuuuyyAaAaAaCcCcCcCcDdDdEeEeEeEeEeGgGgGgGgHhHhIiIiIiIiIiKkkLlLlLlLlLlNnNnNnNnNOoOoOoRrRrRrSsSsSsSsTtTtTtUuUuUuUuUuUuWwYyYZzZzZzs'
    l = list(name)
    l.remove(" ")
    for char in l:
        if char in no:
            ind = l.index(char)
            old = no.index(char)
            l[ind] = yes[old]
    return "".join(l).lower()

def splitNames(names):
    splits = []
    for n in names:
        splits.append(n.split()[0])
    return splits

def getPics(names):
    pics = {}
    for n in names:
        nn = changeName(n)
        for p in os.listdir(f"{path}/resources"):
            if p.startswith(nn):
                pics[n] = f"{path}/resources/{p}"
    return pics

def stepSize(days):
    x = sorted(days.items(), key=lambda item: item[1], reverse=True)[0][1]
    if x < 100:
        y = x if x % 10 == 0 else x + 10 - x % 10
    elif x > 100:
        y = x if x % 100 == 0 else x + 100 - x % 100
    return y/2

def monthLabel(days):
    l = list(days.keys())
    for i in range(len(l)):
        l[i] = l[i][:7]
    return l

def topEmojisTotal(emojis):
    l = sorted(emojis["types"].items(), key=lambda item: item[1], reverse=True)
    types = []
    counts = []
    for e in l:
        types.append(e[0])
        counts.append(e[1])
    return [types[:10], counts[:10]]

def topEmojisPersonal(emojis, name, sent):
    l = sorted(emojis[sent][name].items(), key=lambda item: item[1], reverse=True)
    types = []
    counts = []
    for e in l:
        types.append(e[0])
        counts.append(e[1])
    return [types[1:11], counts[1:11]]

def topEmojis(emojis, names, sent):
    fontSizesT = ["300", "275", "250", "225", "200", "180", "160", "140", "120", "100"]
    fontSizesP = list(map(str, range(180, 80, -10)))
    tops = {"total": zip(topEmojisTotal(emojis)[0], topEmojisTotal(emojis)[1], fontSizesT)}
    for n in names:
        tops[n] = zip(topEmojisPersonal(emojis, n, sent)[0], topEmojisPersonal(emojis, n, sent)[1], fontSizesP)
    return tops

def topTimes(time):
    return [sorted(time.items(), key=lambda item: item[1], reverse=True)[0][0], sorted(time.items(), key=lambda item: item[1], reverse=True)[0][1]]

def countTypes(names, emojis, sent):
    lens = {"total": len(emojis["types"])}
    for n in names:
        lens[n] = len(emojis[sent][n])-1
    return lens

def avgCounts(names, people, emojis, sent):
    avgs = {}
    for n in names:
        avgs[n] = round(emojis[sent][n]["total"]/people[n], 2)
    return avgs

def topsCount(names, emojis, sent):
    count = {"total": len(topEmojisTotal(emojis)[0])}
    for n in names:
        count[n] = len(topEmojisPersonal(emojis, n, sent)[0])
    return count
