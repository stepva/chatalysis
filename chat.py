import json, pprint, operator, sys, os
from datetime import datetime, date

def main():
    path = "messages/inbox/eliskakalinova_ogwzg96p3q"

    if not os.path.isdir(path):
        raise Exception("NOT A FOLDER")

    files = []
    for file in os.listdir(path):
        if os.path.isfile(file) and file.startswith("message") and file.endswith(".json"):
            files.append(file)

    if not files:
        raise Exception("NO JSON FILES")
    file = 'message_1.json'

    with open(files[0]) as chat:
        data = json.load(chat)
        title = data["title"]
        names = getNames(data)
    
    messages = []
    for f in files:
        with open(f) as data:
            data = json.load(data)
            messages.extend(data["messages"])

    fromDay = str(date.fromtimestamp(messages[-1]["timestamp_ms"]//1000))
    toDay = str(date.fromtimestamp(messages[0]["timestamp_ms"]//1000))
    
    chats = [chatAlysis(messages, names)]
    result = getResult(chats)

    result["0) Chat: " + title] = fromDay + " to " + toDay
    for n in names:
        result["{0} %".format(n)] = str(round(result[n]/result["1) Total messages"]*100, 2)) + " %"

    finale = decode(result)
    pprint.pprint(finale, indent=2, sort_dicts=True)
    topDays = [topDay(data)]
    theTopDay = max(topDays, key=lambda x: x[1])
    print("The top day was " + str(theTopDay[0]) + " with " + str(theTopDay[1]) + " messages.")
    daySts = [dayStats(data)]
    dayStsSum = getResult(daySts)
    topDoW(dayStsSum)
    monSts = [monthStats(data)]
    monStsSum = getResult(monSts)  
    topMoY(monStsSum)



def getNames(data):
    ns = []
    for i in range(len(data["participants"])):
        ns.append(data["participants"][i]["name"])
    return ns

def chatAlysis(ms, names):
    total = len(ms)

    info = {
        "1) Total messages": total
    }

    def msgCount(names):
        for n in names:
            num = sum(1 for i in range(total) if ms[i]["sender_name"]==n)
            info[n] = num
        return info

    def imgCount(names):
        sum_img = sum(1 for i in range(total) if "photos" in ms[i])
        if sum_img > 0:
            info["4) Total images"] = sum_img
            for n in names:
                info[n + " images"] = sum(1 for i in range(total) if "photos" in ms [i] and ms[i]["sender_name"]==n)
        return info

    def gifCount(names):
        sum_gif = sum(1 for i in range(total) if "gifs" in ms[i])
        if sum_gif > 0:
            info["3) Total gifs"] = sum_gif
            for n in names:
                info[n + " gifs"] = sum(1 for i in range(total) if "gifs" in ms [i] and ms[i]["sender_name"]==n)
        return info

    def vidCount(names):
        sum_vid = sum(1 for i in range(total) if "videos" in ms[i])
        if sum_vid > 0:
            info["6) Total videos"] = sum_vid
            for n in names:
                info[n + " videos"] = sum(1 for i in range(total) if "videos" in ms [i] and ms[i]["sender_name"]==n)
        return info

    def stiCount(names):
        sum_sti = sum(1 for i in range(total) if "sticker" in ms[i])
        if sum_sti > 0:
            info["5) Total stickers"] = sum_sti
            for n in names:
                info[n + " stickers"] = sum(1 for i in range(total) if "sticker" in ms [i] and ms[i]["sender_name"]==n)
        return info

    def audioCount(names):
        sum_aud = sum(1 for i in range(total) if "audio_files" in ms[i])
        if sum_aud > 0:
            info["7) Total audios"] = sum_aud
            for n in names:
                info[n + " audio"] = sum(1 for i in range(total) if "audio_files" in ms [i] and ms[i]["sender_name"]==n)
        return info

    def fileCount(names):
        sum_fil = sum(1 for i in range(total) if "files" in ms[i])
        if sum_fil > 0:
            info["2) Total files"] = sum_fil
            for n in names:
                info[n + " files"] = sum(1 for i in range(total) if "files" in ms [i] and ms[i]["sender_name"]==n)
        return info

    msgCount(names)
    imgCount(names)
    gifCount(names)
    vidCount(names)
    stiCount(names)
    audioCount(names)
    fileCount(names)

    #pprint.pprint(final, indent=2, sort_dicts=False)

    #vibecheck
    sum_con = sum(1 for i in range(total) if "content" in ms[i])
    sum_img = sum(1 for i in range(total) if "photos" in ms[i])
    sum_gif = sum(1 for i in range(total) if "gifs" in ms[i])
    sum_sti = sum(1 for i in range(total) if "sticker" in ms[i])
    sum_vid = sum(1 for i in range(total) if "videos" in ms[i])
    sum_aud = sum(1 for i in range(total) if "audio_files" in ms[i])
    sum_fil = sum(1 for i in range(total) if "files" in ms[i])
    sumsum = sum_con + sum_img + sum_gif + sum_vid + sum_aud + sum_fil + sum_sti
    if sumsum != total:
        print("something’s wrong: " + str(sumsum))

    return info

def decode(dictx):
    final = {}
    for k in dictx:
        final[k.encode('iso-8859-1').decode('utf-8')] = dictx[k]
    return final

def getResult(chatRess):
    return {k: sum(t.get(k, 0) for t in chatRess) for k in set.union(*[set(t) for t in chatRess])}

def topDay(dataO):
    topD = 0
    countD = 0
    dayX = date.fromtimestamp(dataO["messages"][0]["timestamp_ms"]//1000)
    countX = 0
    for i in range(len(dataO["messages"])):
        dayY = date.fromtimestamp(dataO["messages"][i]["timestamp_ms"]//1000)
        if dayY == dayX:
            countX += 1
            if countX > countD:
                countD = countX
                topD = dayX
        else:
            countX = 1
            dayX = dayY
    return [topD, countD]

def dayStats(dataO):
    days = {}
    for d in range(1,8):
        msgD = sum(1 for i in range(len(dataO["messages"])) if date.fromtimestamp(dataO["messages"][i]["timestamp_ms"]//1000).isoweekday()==d)
        if msgD > 0:
            days["{0}".format(d)] = msgD
    return days

def topDoW(dayss):
    dNames = {"1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
    dayDay = max(dayss.items(), key=operator.itemgetter(1))[0]
    dayDayN = dNames[dayDay]
    dayDayC = dayss[dayDay]
    print("Most messages were sent on " + dayDayN + "s - " + str(dayDayC) + ".")


def monthStats(dataO):
    months = {}
    for m in range(1,12):
        msgM = sum(1 for i in range(len(dataO["messages"])) if date.fromtimestamp(dataO["messages"][i]["timestamp_ms"]//1000).month==m)
        if msgM > 0:
            months["{0}".format(m)] = msgM
    return months

def topMoY(monthss):
    dNames = {"1": "Januray", "2": "February", "3": "March", "4": "April", "5": "May", "6": "June", "7": "July", "8": "August", "9": "September", "10": "October", "11": "November", "12": "December"}
    monthMonth = max(monthss.items(), key=operator.itemgetter(1))[0]
    monthMonthN = dNames[monthMonth]
    monthMonthC = monthss[monthMonth]
    print("Most messages were sent in " + monthMonthN + " - " + str(monthMonthC) + ".")


if __name__ == "__main__":
    main()