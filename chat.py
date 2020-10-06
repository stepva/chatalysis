import json, operator, sys, os
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

    files.sort()

    with open(files[0]) as chat:
        data = json.load(chat)
        title = data["title"]
        names = getNames(data)
        
    messages = []
    for f in files:
        with open(f) as data:
            data = json.load(data)
            messages.extend(data["messages"])

    result = chatAlysis(messages, names)
    format(result, title, messages, names)

    final = decode(result)
    pprint(final, indent=2, sort_dicts=True)

    topDay(messages)
    topMonth(monthStats(messages))
    topDoW(dayStats(messages))

def getNames(data):
    ns = []
    for i in range(len(data["participants"])):
        ns.append(data["participants"][i]["name"])
    return ns

def countFiltered(iterable, predicate):
    return len(list(filter(predicate, iterable)))

def chatAlysis(ms, names):
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

    info["2) Total audios"] = sum_aud
    info["3) Total files"] = sum_fil
    info["4) Total gifs"] = sum_gif
    info["5) Total images"] = sum_img
    info["6) Total stickers"] = sum_sti
    info["7) Total videos"] = sum_vid

    for n in names:
        num = countFiltered(ms, lambda x: x["sender_name"]==n)
        info[n] = num

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
    sumsum = sum_con + sum_img + sum_gif + sum_vid + sum_aud + sum_fil + sum_sti
    if sumsum != total:
        print(f"something’s wrong: {str(sumsum)}")
        #print(list(filter(lambda x: not any(y in ["content", "photos", "gifs", "sticker", "videos", "audio_files", "files"] for y in x), ms)))
    
    return info

def format(result, title, messages, names):
    toDay = str(date.fromtimestamp(messages[0]["timestamp_ms"]//1000))
    fromDay = str(date.fromtimestamp(messages[-1]["timestamp_ms"]//1000))
    result[f"0) Chat: {title}"] = fromDay + " to " + toDay
    for n in names:
        result[f"{n} %"] = str(round(result[n]/result["1) Total messages"]*100, 2)) + " %"
    return result

def decode(dictx):
    final = {}
    for k in dictx:
        final[k.encode('iso-8859-1').decode('utf-8')] = dictx[k]
    return final

def getResult(chatRess):
    return {k: sum(t.get(k, 0) for t in chatRess) for k in set.union(*[set(t) for t in chatRess])}

def topDay(messages):
    topD = 0
    countD = 0
    dayX = date.fromtimestamp(messages[0]["timestamp_ms"]//1000)
    countX = 0
    for i in range(len(messages)):
        dayY = date.fromtimestamp(messages[i]["timestamp_ms"]//1000)
        if dayY == dayX:
            countX += 1
            if countX > countD:
                countD = countX
                topD = dayX
        else:
            countX = 1
            dayX = dayY
    print(f"The top day was {str(topD)} with {str(countD)} messages.")

def dayStats(messages):
    days = {}
    for d in range(1,8):
        msgD = countFiltered(messages, lambda x: date.fromtimestamp(x["timestamp_ms"]//1000).isoweekday() == d)
        days[f"{d}"] = msgD
    return days

def topDoW(days):
    dNames = {"1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
    dayDay = max(days.items(), key=operator.itemgetter(1))[0]
    dayDayN = dNames[dayDay]
    #dayDayC = days[dayDay]
    print(f"On average, most messages were sent on {dayDayN}s.")

def monthStats(messages):
    first = date.fromtimestamp(messages[-1]["timestamp_ms"]//1000).year
    last = date.fromtimestamp(messages[0]["timestamp_ms"]//1000).year
    months = {}
    for y in range(first, last+1):
        for m in range(1,13):
            msgM = countFiltered(messages, lambda x: date.fromtimestamp(x["timestamp_ms"]//1000).month == m and date.fromtimestamp(x["timestamp_ms"]//1000).year == y)
            if msgM > 0:
                months[f"{m}/{y}"] = msgM
    return months

def topMonth(months):
    #mNames = {"1": "Januray", "2": "February", "3": "March", "4": "April", "5": "May", "6": "June", "7": "July", "8": "August", "9": "September", "10": "October", "11": "November", "12": "December"}
    monthMonth = max(months.items(), key=operator.itemgetter(1))[0]
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

if __name__ == "__main__":
    main()
