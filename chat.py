#TODO: argparse, emojis???, WORK ON REACTIONS GRAPH, ideas: first message, time of day distribution, nicks and groupchat names, lenght of voices (need to be from files not json)

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
        title = decode1(data["title"])
        names = getNames(data)
    
    messages = []
    for f in files:
        with open(f) as data:
            data = json.load(data)
            messages.extend(data["messages"])
    messages = sorted(messages, key=lambda k: k["timestamp_ms"])     
    decodeMsgs(messages)

    result = chatAlysis(messages, names)
    format(result, title, messages, names)
    
    pprint(result, indent=2, sort_dicts=True)

    days = dayStats(messages)
    months = monthStats(messages)

    topDay(messages)
    topMonth(months)
    topDoW(days)
    """
    reacts = reactionStats(messages, names)
    pprint(reacts, indent=2, sort_dicts=False)
 
    graphPieDict(result, names)
    graphBarValues(days)
    graphBarValues(months)
    """

def decode1(word):
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

def decode(dictx):
    final = {}
    for k in dictx:
        final[k.encode('iso-8859-1').decode('utf-8')] = dictx[k]
    return final

def getResult(chatRess):
    return {k: sum(t.get(k, 0) for t in chatRess) for k in set.union(*[set(t) for t in chatRess])}

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
    print(f"On average, most messages were sent on {dayDay}s.")

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
    #mNames = {"1": "Januray", "2": "February", "3": "March", "4": "April", "5": "May", "6": "June", "7": "July", "8": "August", "9": "September", "10": "October", "11": "November", "12": "December"}
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

def reactionStats(messages, names):
    reactTypes = {"sad": "\u00f0\u009f\u0098\u00a2",
                  "heart": "\u00e2\u009d\u00a4",
                  "wow": "\u00f0\u009f\u0098\u00ae",
                  "like": "\u00f0\u009f\u0091\u008d",
                  "haha": "\u00f0\u009f\u0098\u0086",
                  "angry": "\u00f0\u009f\u0098\u00a0",
                  "dislike": "\u00f0\u009f\u0091\u008e",
                  "heart_eyes": "\u00f0\u009f\u0098\u008d"
                  }
    reactionNames = list(reactTypes.keys())

    reactions = {"total": 0}
    avgReacts = {}
    reactsGiven = {}
    sad = {"sad": 0}
    heart = {"heart": 0}
    wow = {"wow": 0}
    like = {"like": 0}
    haha = {"haha": 0}
    angry = {"angry": 0}
    dislike = {"dislike": 0}
    wrong = []

    for n in names:
        reactions[n] = 0
        reactsGiven[n] = 0
        sad[n] = 0
        heart[n] = 0
        wow[n] = 0
        like[n] = 0
        haha[n] = 0
        angry[n] = 0
        dislike[n] = 0
        for m in messages:
            if "reactions" in m:
                for i in m["reactions"]:
                    if i["actor"] == n:
                        reactsGiven[n] += 1
                if m["sender_name"]==n:    
                    reactions["total"] += len(m["reactions"])
                    reactions[n] += len(m["reactions"])
                    for i in m["reactions"]:
                        if i["reaction"] == reactTypes["sad"]: 
                            sad[n] += 1
                            sad["sad"] += 1
                        elif i["reaction"] == reactTypes["heart"] or i["reaction"] == reactTypes["heart_eyes"]: 
                            heart[n] += 1
                            heart["heart"] += 1
                        elif i["reaction"] == reactTypes["wow"]: 
                            wow[n] += 1
                            wow["wow"] += 1
                        elif i["reaction"] == reactTypes["like"]: 
                            like[n] += 1
                            like["like"] += 1
                        elif i["reaction"] == reactTypes["haha"]: 
                            haha[n] += 1
                            haha["haha"] += 1
                        elif i["reaction"] == reactTypes["angry"]: 
                            angry[n] += 1
                            angry["angry"] += 1
                        elif i["reaction"] == reactTypes["dislike"]: 
                            dislike[n] += 1
                            dislike["dislike"] += 1
                        else: wrong.append(i["reaction"]) 
        if reactions[n] > 0:
            avgReacts[n] = round(reactions[n]/countFiltered(messages, lambda x: x["sender_name"] == n), 2)
        else:
            avgReacts[n] = 0    

    if len(wrong) > 0: 
        raise Exception("UNEXPECTED REACT")
 
    reactNames = ["sad", "heart", "wow", "like", "haha", "angry", "dislike"]
    totals = [sad["sad"], heart["heart"], wow["wow"], like["like"], haha["haha"], angry["angry"], dislike["dislike"]]
    totalReacts = reactions["total"]
    topReact = [reactionNames[totals.index(max(totals))], max(totals)]
    
    totalsPct = []
    for i in totals:
        totalsPct.append(round(i/totalReacts, 2))

    finalStats = {
        "total reactions": totalReacts,
        "most used reaction": topReact,
        "gets most reactions": sorted(decode(reactions).items(), key=lambda item: item[1])[-2],
        "gets most reactions on avg": sorted(decode(avgReacts).items(), key=lambda item: item[1])[-1],
        "gives most reactions": sorted(decode(reactsGiven).items(), key=lambda item: item[1])[-1]
    }

    graphPie(totalsPct, reactNames)
    return finalStats

def graphBarValues(dictio):
    plt.bar(*zip(*dictio.items()))
    plt.show()

def graphPieDict(result, names):
    result = decode(result)
    sizes = []
    for n in names:
        code = n + " %"
        sizes.append(result[code])
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=names, autopct="%1.2f %%")
    ax1.axis("equal")
    plt.show()

def graphPie(values, labels):
    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels)
    ax1.axis("equal")
    plt.show()

if __name__ == "__main__":
    main()
