#TODO: argparse, WORK ON GRAPHS 
#ideas: nicks and groupchat names, lenght of voices (need to be from files not json), emojis

import json, sys, os, matplotlib.pyplot as plt
from datetime import datetime, date
from pprint import pprint

def main():
    path = ""

    if not os.path.isdir(path):
        raise Exception("NOT A FOLDER")

    files = []
    for file in os.listdir(path):
        if file.startswith("message") and file.endswith(".json"):
            files.append(path + "/" + file)

    if not files:
        raise Exception("NO JSON FILES")

    with open(files[0]) as chat:
        data = json.load(chat)
        title = decode(data["title"])
        names = getNames(data)
    
    messages = []
    for f in files:
        with open(f) as data:
            data = json.load(data)
            messages.extend(data["messages"])
    messages = sorted(messages, key=lambda k: k["timestamp_ms"])     
    decodeMsgs(messages)

    result = chatStats(messages, names)
    format(result, title, messages, names)

    pprint(result, indent=2, sort_dicts=True)

    days = dayStats(messages)
    months = monthStats(messages)
    hours = hoursStats(messages)

    topDay(messages)
    topHours(hours)
    topMonth(months)
    topDoW(days)
    firstMsg(messages)

    reacts = reactionStats(messages)
    pprint(reacts, indent=2, sort_dicts=False)  

    #graphBarMessages(days, title, "Days", "Messages per day of the week")
    #graphBarMessages(months, title, "Months", "Messages per month")
    #graphBarMessages(hours, title, "Hours", "Messages per hours of the day")
    #graphPieMessages(result, names, title, "Messages per person")

def decode(word):
    return word.encode('iso-8859-1').decode('utf-8')

def decodeMsgs(messages):
    for m in messages:
        m["sender_name"] = m["sender_name"].encode('iso-8859-1').decode('utf-8')
        if "content" in m:
            m["content"] = m["content"].encode('iso-8859-1').decode('utf-8')
        if "reactions" in m:
            for r in m["reactions"]:
                r["reaction"] = r["reaction"].encode('iso-8859-1').decode('utf-8')
                r["actor"] = r["actor"].encode('iso-8859-1').decode('utf-8')
    return messages

def getNames(data):
    ns = []
    for i in data["participants"]:
        ns.append(i["name"].encode('iso-8859-1').decode('utf-8'))
    return ns

def countFiltered(iterable, predicate):
    return len(list(filter(predicate, iterable)))

def chatStats(ms, names):
    total = len(ms)

    info = {
        "1) Total messages": total
    }

    sum_con = countFiltered(ms, lambda x: "content" in x)
    sum_img = countFiltered(ms, lambda x: "photos" in x)
    sum_gif = countFiltered(ms, lambda x: "gifs" in x)
    sum_sti = countFiltered(ms, lambda x: "sticker" in x)
    sum_vid = countFiltered(ms, lambda x: "videos" in x)
    sum_aud = countFiltered(ms, lambda x: "audio_files" in x)
    sum_fil = countFiltered(ms, lambda x: "files" in x)
    sumsum = sum_con + sum_img + sum_gif + sum_vid + sum_aud + sum_fil + sum_sti

    info["2) Total audios"] = sum_aud
    info["3) Total files"] = sum_fil
    info["4) Total gifs"] = sum_gif
    info["5) Total images"] = sum_img
    info["6) Total stickers"] = sum_sti
    info["7) Total videos"] = sum_vid
    info["8) Deleted messages"] = total-sumsum

    for n in names:
        info[n] = countFiltered(ms, lambda x: x["sender_name"]==n)

    if sum_img > 0:
        for n in names:
            info[n + " images"] = countFiltered(ms, lambda x: "photos" in x and x["sender_name"]==n)

    if sum_gif > 0:
        for n in names:
            info[n + " gifs"] = countFiltered(ms, lambda x: "gifs" in x and x["sender_name"]==n)

    if sum_vid > 0:
        for n in names:
            info[n + " videos"] = countFiltered(ms, lambda x: "videos" in x and x["sender_name"]==n)

    if sum_sti > 0:
        for n in names:
            info[n + " stickers"] = countFiltered(ms, lambda x: "sticker" in x and x["sender_name"]==n)

    if sum_aud > 0:
        for n in names:
            info[n + " audio"] = countFiltered(ms, lambda x: "audio_files" in x and x["sender_name"]==n)

    if sum_fil > 0:
        for n in names:
            info[n + " files"] = countFiltered(ms, lambda x: "files" in x and x["sender_name"]==n)

    #vibecheck
    #if sumsum != total:
        #print(f"something’s wrong: {str(sumsum)}")
        #print(list(filter(lambda x: not any(y in ["content", "photos", "gifs", "sticker", "videos", "audio_files", "files"] for y in x), ms)))
    
    return info

def format(result, title, messages, names):
    fromDay = str(date.fromtimestamp(messages[0]["timestamp_ms"]//1000))
    toDay = str(date.fromtimestamp(messages[-1]["timestamp_ms"]//1000))
    result[f"0) Chat: {title}"] = fromDay + " to " + toDay
    for n in names:
        result[f"{n} %"] = round(result[n]/result["1) Total messages"]*100, 2)
    return result

def topDay(messages):
    days = {}
    for i in messages:
        day = date.fromtimestamp(i["timestamp_ms"]//1000)
        if day in days:
            days[day] += 1
        else:
            days[day] = 1
    topD = sorted(days.items(), key=lambda item: item[1])[-1]
    print(f"The top day was {str(topD[0])} with {str(topD[1])} messages.")

def dayStats(messages):
    weekdays = {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}
    dNames = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
    for d in range(1,8):
        msgD = countFiltered(messages, lambda x: date.fromtimestamp(x["timestamp_ms"]//1000).isoweekday() == d)
        weekdays[dNames[d]] = msgD
    return weekdays

def topDoW(days):
    dayDay = max(days.items(), key=lambda item: item[1])[0]
    print(f"Most messages were sent on {dayDay}s.")

def monthStats(messages):
    first = date.fromtimestamp(messages[0]["timestamp_ms"]//1000).year
    last = date.fromtimestamp(messages[-1]["timestamp_ms"]//1000).year
    months = {}
    for y in range(first, last+1):
        for m in range(1,13):
            msgM = countFiltered(messages, lambda x: date.fromtimestamp(x["timestamp_ms"]//1000).month == m and date.fromtimestamp(x["timestamp_ms"]//1000).year == y)
            if msgM > 0:
                months[f"{m}/{y}"] = msgM
    return months

def topMonth(months):
    monthMonth = max(months.items(), key=lambda item: item[1])[0]
    monthMonthC = months[monthMonth]
    print(f"The top month was {monthMonth} with {str(monthMonthC)} messages.")

def yearStats(messages):
    first = date.fromtimestamp(messages[-1]["timestamp_ms"]//1000).year
    last = date.fromtimestamp(messages[0]["timestamp_ms"]//1000).year
    years = {}
    for y in range(first, last+1):
        msgY = countFiltered(messages, lambda x: date.fromtimestamp(x["timestamp_ms"]//1000).year == y)
        years[f"{y}"] = msgY
    return years

def hoursStats(messages):
    hours = {
        "00:00 - 03:59": countFiltered(messages, lambda x: datetime.fromtimestamp(x["timestamp_ms"]//1000).hour < 4),
        "04:00 - 07:59": countFiltered(messages, lambda x: datetime.fromtimestamp(x["timestamp_ms"]//1000).hour >= 4 and datetime.fromtimestamp(x["timestamp_ms"]//1000).hour < 8),
        "08:00 - 11:59": countFiltered(messages, lambda x: datetime.fromtimestamp(x["timestamp_ms"]//1000).hour >= 8 and datetime.fromtimestamp(x["timestamp_ms"]//1000).hour < 12),
        "12:00 - 15:59": countFiltered(messages, lambda x: datetime.fromtimestamp(x["timestamp_ms"]//1000).hour >= 12 and datetime.fromtimestamp(x["timestamp_ms"]//1000).hour < 16),
        "16:00 - 19:59": countFiltered(messages, lambda x: datetime.fromtimestamp(x["timestamp_ms"]//1000).hour >= 16 and datetime.fromtimestamp(x["timestamp_ms"]//1000).hour < 20),
        "20:00 - 23:59": countFiltered(messages, lambda x: datetime.fromtimestamp(x["timestamp_ms"]//1000).hour >= 20)
    }
    return hours

def topHours(hours):
    hoursH = max(hours.items(), key=lambda item: item[1])[0]
    countH = hours[hoursH]
    print(f"Most messages were sent between {hoursH[:5]} and {hoursH[-5:]}.")

def reactionStats(messages):
    reaccs = {}
    gave = {}
    got = {}
    gotAvg = {}
    for m in messages:
        if "reactions" in m:
            for r in m["reactions"]:
                reaccs[r["reaction"]] = 1 + reaccs.get(r["reaction"], 0)
                gave[r["actor"]] = 1 + gave.get(r["actor"], 0)
                got[m["sender_name"]] = 1 + got.get(m["sender_name"], 0)

    for k in got:
        gotAvg[k] = round(got[k]/countFiltered(messages, lambda x: x["sender_name"] == k), 2)

    stats = {
        "total reactions": sum(reaccs.values()),
        "top reactions": sorted(reaccs.items(), key=lambda item: item[1], reverse=True)[0:5],
        "gets most reactions": sorted(got.items(), key=lambda item: item[1], reverse=True)[0],
        "gets most reactions on avg": sorted(gotAvg.items(), key=lambda item: item[1], reverse=True)[0],
        "gives most reactions": sorted(gave.items(), key=lambda item: item[1], reverse=True)[0]
    }
    return stats

def firstMsg(messages):
    if not "content" in messages[0]:
        raise Exception("FIRST MESSAGE WASN'T A TEXT")
    msg = messages[0]["content"]
    author = messages[0]["sender_name"]
    print(f"First message was \"{msg}\" sent by {author}")

def graphBarMessages(stats, title, x, graphtitle):
    plt.bar(*zip(*stats.items()))
    plt.suptitle(f"Chat {title}: {graphtitle}")
    plt.ylabel("Messages")
    plt.xlabel(x)
    plt.savefig(graphtitle)
    plt.show()

def graphPieMessages(result, names, title, graphtitle):
    sizes = []
    for n in names:
        sizes.append(result[n])
    def func(pct, allvalues):
        absolute = int(pct / 100.*sum(allvalues))
        return "{:d}\n({:.1f} %)".format(absolute, pct)
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=names, autopct=lambda pct: func(pct, sizes))
    ax.axis("equal")
    plt.suptitle(f"Chat {title}: {graphtitle}")
    plt.savefig(graphtitle)
    plt.show()

def graphBarhReacts(stats):
    reacts = stats["top reactions"]
    types = []
    values = []
    for r in reacts:
        types.append(r[0])
        values.append(r[1])
    #y_pos = arrange(len(bars))
    plt.barh(types, values)
    #plt.yticks(types)
    plt.show()

if __name__ == "__main__":
    main()
