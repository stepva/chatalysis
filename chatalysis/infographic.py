# Standard library imports
import locale
import os
import math, random
import pathlib
# Third party imports
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
# Application imports
from utility import home


#emojis = {"total": 0, "types": {"type": x}, "sent": {"name": {"total": x, "type": y}}}
#reactions = {"total": 0, "types": {}, "gave": {"name": {"total": x, "type": y}}, "got": {"name": {"total": x, "type": y}}}
locale.setlocale(locale.LC_ALL, '')

# Imports stats and other variables into the HTML
def mrHtml(version, names, basicStats, fromDay, toDay, times, emojis, reactions, title):
    file_loader = FileSystemLoader(f"{home}/../resources/templates")
    env = Environment(loader=file_loader)
    env.filters['space'] = s

    (people, photos, gifs, stickers, videos, audios, files) = basicStats
    (hours, days, weekdays, months, years) = times

    template = env.get_template('index.html.j2')

    wdNames = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
    labels, data, background, border = msgGraph(names, people)

    return template.render(
        #utility
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

        #personalstats
        lines=persStatsCount(names)[0],
        left=persStatsCount(names)[1],
        leftEmojis=emojiStatsCount(names),

        #messagesgraph
        labels=labels,
        data=data,
        background=background,
        border=border,

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

# Splits number by thousands with a space
def s(n):
    return "{0:n}".format(n) if n != 1 else n

# Removes non-english characters from a name
def changeName(name):
    no = 'ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝßàáâãäåçèéêëìíîïñòóôõöùúûüýÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſ'
    yes = 'AAAAAACEEEEIIIINOOOOOUUUUYsaaaaaaceeeeiiiinooooouuuuyyAaAaAaCcCcCcCcDdDdEeEeEeEeEeGgGgGgGgHhHhIiIiIiIiIiKkkLlLlLlLlLlNnNnNnNnNOoOoOoRrRrRrSsSsSsSsTtTtTtUuUuUuUuUuUuWwYyYZzZzZzs'
    l = list(name)
    if " " in l:
        l.remove(" ")
    for char in l:
        if char in no:
            ind = l.index(char)
            old = no.index(char)
            l[ind] = yes[old]
    return "".join(l).lower()

# Splits names and takes just the first name
def splitNames(names):
    splits = {}
    for n in names:
        splits[n] = n.split()[0]
    return splits

# Collects the available profile pics or uses a placeholder picture instead
def getPics(names):
    pics = {}
    for n in names:
        pics[n] = f"{home}/../resources/images/placeholder.jpg" 
        for p in os.listdir(f"{home}/../resources/images"):
            if p.startswith(changeName(n)):
                pics[n] = f"{home}/../resources/images/{p}"
    return pics

# Calculates the desired step size for the time chart
def stepSize(days):
    x = sorted(days.items(), key=lambda item: item[1], reverse=True)[0][1]
    if x < 100:
        y = x if x % 10 == 0 else x + 10 - x % 10
    elif x > 100:
        y = x if x % 100 == 0 else x + 100 - x % 100
    return y/2

# Creates labels for the time chart
def monthLabel(days):
    l = list(days.keys())
    for i in range(len(l)):
        l[i] = l[i][:7]
    return l

# Prepares top emojis for the HTML 
def topEmojisTotal(emojis):
    l = sorted(emojis["types"].items(), key=lambda item: item[1], reverse=True)
    types = []
    counts = []
    for e in l:
        types.append(e[0])
        counts.append(e[1])
    return [types[:10], counts[:10]]

# Prepares personal top emojis for the HTML 
def topEmojisPersonal(emojis, name, sent):
    l = sorted(emojis[sent][name].items(), key=lambda item: item[1], reverse=True)
    types = []
    counts = []
    for e in l:
        types.append(e[0])
        counts.append(e[1])
    return [types[1:11], counts[1:11]]

# Packs the overall and top emojis for the HTML 
def topEmojis(emojis, names, sent):
    fontSizesT = list(map(str, range(300, 100, -20)))
    fontSizesP = list(map(str, range(180, 80, -10)))
    tops = {"total": zip(topEmojisTotal(emojis)[0], topEmojisTotal(emojis)[1], fontSizesT)}
    for n in names:
        tops[n] = zip(topEmojisPersonal(emojis, n, sent)[0], topEmojisPersonal(emojis, n, sent)[1], fontSizesP)
    return tops

# Gets the top time (year, month...) and messages in there
def topTimes(time):
    return [sorted(time.items(), key=lambda item: item[1], reverse=True)[0][0], sorted(time.items(), key=lambda item: item[1], reverse=True)[0][1]]

# Gets the count of different emojis or reactions
def countTypes(names, emojis, sent):
    lens = {"total": len(emojis["types"])}
    for n in names:
        lens[n] = len(emojis[sent][n])-1
    return lens

# Gets the average of sent emojis or reactions
def avgCounts(names, people, emojis, sent):
    avgs = {}
    for n in names:
        avgs[n] = round(emojis[sent][n]["total"]/people[n], 2)
    return avgs

# Gets the number of top emojis or reactions up to 10
def topsCount(names, emojis, sent):
    count = {"total": len(topEmojisTotal(emojis)[0])}
    for n in names:
        count[n] = len(topEmojisPersonal(emojis, n, sent)[0])
    return count

# Calculates how many lines of personal stats are needed in the HTML
def persStatsCount(names):
    if len(names) > 2:
        lines = math.floor((len(names)-2)/3)
        left = (len(names)-2)-(lines*3)
        x = -len(names) if left == 0 else left
        return [lines, x]
    else:
        return [0, 0]

# Calculates how many lines of emojis and reactions stats are needed in the HTML
def emojiStatsCount(names):
    if len(names)%2 == 0:
        return -len(names)
    else: 
        return 1

# Prepares labels and data for the messages graph
def msgGraph(names, people):
    labels=[]
    data=[]
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
        "hsla(17, 80%, 66%, 0.5)"
    ]
    border = ["hsla(53, 0%, 0%, 0.5)"] * 10
    if len(names)==2:
        labels=[names[1], names[0]]
        data=[people[names[1]], people[names[0]]]
        bg=background[0:2]
        bo=border[0:2] 
    else:
        for n in sorted(people.items(), key=lambda item: item[1], reverse=True)[1:10]:
            labels.append(n[0])
            data.append(n[1])
            bg=background[0:9]
            bo=border[0:9]
        if len(names) > 9:
            labels.append("Others")
            sofar=sum(data)
            data.append(people["total"]-sofar)
            bg.append(background[9])
            bo.append(border[9])        
    return (labels, data, background, border)
    
