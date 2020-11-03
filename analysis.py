import emoji
import regex
from datetime import datetime, date, timedelta


def raw(messages, names):
    fromDay = date.fromtimestamp(messages[0]["timestamp_ms"]//1000)
    toDay = date.fromtimestamp(messages[-1]["timestamp_ms"]//1000)
    people = {"total": 0}
    photos = {"total": 0}
    gifs = {"total": 0}
    stickers = {"total": 0}
    videos = {"total": 0}
    audios = {"total": 0}
    files = {"total": 0}
    reactions = {"total": 0, "types": {}, "gave": {}, "got": {}}
    emojis = {"total": 0, "types": {}, "sent": {}}
    days = daysList(messages)
    months = {}
    years = {}
    weekdays = {}
    hours = hoursList()

    for n in names:
        reactions["gave"][n] = {"total": 0}
        reactions["got"][n] = {"total": 0}
        emojis["sent"][n] = {"total": 0}

    for m in messages:
        name = m["sender_name"]
        people["total"] += 1
        people[name] = 1 + people.get(name, 0)
        day = date.fromtimestamp(m["timestamp_ms"]//1000)
        days[str(day)] += 1
        month = f"{day.month}/{day.year}"
        months[month] = 1 + months.get(month, 0)
        year = f"{day.year}"
        years[year] = 1 + years.get(year, 0)
        weekday = date.fromtimestamp(m["timestamp_ms"]//1000).isoweekday()
        weekdays[weekday] = 1 + weekdays.get(weekday, 0)
        hour = datetime.fromtimestamp(m["timestamp_ms"]//1000).hour
        hours[hour] += 1
        if "content" in m:
            data = regex.findall(r'\X', m["content"])
            for c in data:
                if any(char in emoji.UNICODE_EMOJI for char in c):
                    emojis["total"] += 1
                    emojis["types"][c] = 1 + emojis["types"].get(c, 0)
                    emojis["sent"][name]["total"] += 1
                    emojis["sent"][name][c] = 1 + emojis["sent"][name].get(c, 0)
        elif "photos" in m:
            photos["total"] += 1
            photos[name] = 1 + photos.get(name, 0)
        elif "gifs" in m:
            gifs["total"] += 1
            gifs[name] = 1 + gifs.get(name, 0)
        elif "sticker" in m:
            stickers["total"] += 1
            stickers[name] = 1 + stickers.get(name, 0)
        elif "videos" in m:
            videos["total"] += 1
            videos[name] = 1 + videos.get(name, 0)
        elif "audio_files" in m:
            audios["total"] += 1
            audios[name] = 1 + audios.get(name, 0)
        elif "files" in m:
            files["total"] += 1
            files[name] = 1 + files.get(name, 0)
        if "reactions" in m:
            for r in m["reactions"]:
                reactions["total"] += 1
                reactions["types"][r["reaction"]] = 1 + reactions["types"].get(r["reaction"], 0)
                reactions["gave"][r["actor"]]["total"] += 1
                reactions["gave"][r["actor"]][r["reaction"]] = 1 + reactions["gave"][r["actor"]].get(r["reaction"], 0)
                reactions["got"][name]["total"] += 1
                reactions["got"][name][r["reaction"]] = 1 + reactions["got"][name].get(r["reaction"], 0)
    
    basicStats = (people, photos, gifs, stickers, videos, audios, files)
    times = (hours, days, weekdays, months, years)
    return basicStats, reactions, emojis, times, people, fromDay, toDay

def daysList(messages):
    fromDay = date.fromtimestamp(messages[0]["timestamp_ms"]//1000)
    toDay = date.fromtimestamp(messages[-1]["timestamp_ms"]//1000)
    delta = toDay - fromDay
    days = {}
    for i in range(delta.days + 1):
        day = fromDay + timedelta(days=i)
        days[str(day)] = 0
    return days

def hoursList():
    hours = {}
    for i in range(24):
        hours[i] = 0
    return hours

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

def chatStats(basicStats, names):
    #basicStats = [people, photos, gifs, stickers, videos, audios, files]
    info = {
        "1) Total messages": basicStats[0]["total"],
        "2) Total audios": basicStats[5]["total"],
        "3) Total files": basicStats[6]["total"],
        "4) Total gifs": basicStats[2]["total"],
        "5) Total images": basicStats[1]["total"],
        "6) Total stickers": basicStats[3]["total"],
        "7) Total videos": basicStats[4]["total"]
    }
    for n in names:
        if n in basicStats[0]: 
            info[n] = basicStats[0][n]
            info[f"{n} %"] = round(basicStats[0][n]/basicStats[0]["total"]*100, 2)
        if n in basicStats[1]: info[n + " images"] = basicStats[1][n]
        if n in basicStats[2]: info[n + " gifs"] = basicStats[2][n]
        if n in basicStats[4]: info[n + " videos"] = basicStats[4][n]
        if n in basicStats[3]: info[n + " stickers"] = basicStats[3][n]
        if n in basicStats[5]: info[n + " audio"] = basicStats[5][n]
        if n in basicStats[6]: info[n + " files"] = basicStats[6][n]
        
    return info

def header(title, messages):
    fromDay = str(date.fromtimestamp(messages[0]["timestamp_ms"]//1000))
    toDay = str(date.fromtimestamp(messages[-1]["timestamp_ms"]//1000))
    print(f"Chat: {title}, from {fromDay} to {toDay}")

def timeStats(times):
    #times = [hours, days, weekdays, months, years]
    wdNames = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}

    topDay = sorted(times[1].items(), key=lambda item: item[1], reverse=True)[0]
    topWd = sorted(times[2].items(), key=lambda item: item[1], reverse=True)[0]
    topMonth = sorted(times[3].items(), key=lambda item: item[1], reverse=True)[0]
    topYear = sorted(times[4].items(), key=lambda item: item[1], reverse=True)[0]

    stats = {
        "1) The top day": [topDay[0], f"{topDay[1]} messages"],
        "2) Top hours of day": sorted(times[0].items(), key=lambda item: item[1], reverse=True)[0:3],
        "3) Top weekday": [wdNames[topWd[0]], topWd[1]],
        "4) Top month": topMonth,
        "5) Top year": topYear
    }
    return stats

def reactionStats(reactions, names, people):
    #reactions = {"total": 0, "types": {}, "gave": {"name": {"total": x, "type": y}}, "got": {"name": {"total": x, "type": y}}}
    gaves = {}
    gots = {}
    gotsAvg = {}

    for n in names:
        gaves[n] = reactions["gave"][n]["total"]
        gots[n] = reactions["got"][n]["total"]
        gotsAvg[n] = round(reactions["got"][n]["total"]/people[n], 2)

    stats = {
        "1) total reactions": reactions["total"],
        "2) total different reactions": len(reactions["types"]),
        "3) top reactions": sorted(reactions["types"].items(), key=lambda item: item[1], reverse=True)[0:5],
        "4) got most reactions": sorted(gots.items(), key=lambda item: item[1], reverse=True)[0],
        "5) got most reactions on avg": sorted(gotsAvg.items(), key=lambda item: item[1], reverse=True)[0],
        "6) gave most reactions": sorted(gaves.items(), key=lambda item: item[1], reverse=True)[0]
    }

    for n in names:
        stats[n] = {
            "total got": gots[n], 
            "avg got": gotsAvg[n], 
            "dif got": len(reactions["got"][n])-1, 
            "top got": sorted(reactions["got"][n].items(), key=lambda item: item[1], reverse=True)[1:4],
            "total gave": gaves[n],
            "dif gave": len(reactions["gave"][n])-1,
            "top gave": sorted(reactions["gave"][n].items(), key=lambda item: item[1], reverse=True)[1:4]
        }   

    return stats

def firstMsg(messages):
    author = messages[0]["sender_name"]
    texts = {}
    i = 0
    while True:
        if messages[i]["sender_name"] == author:
            keys = list(messages[i].keys())
            texts[messages[i]["sender_name"]] = messages[i][keys[2]]
            i += 1
        else:
            keys = list(messages[i].keys())
            texts[messages[i]["sender_name"]] = messages[i][keys[2]]
            break
    return texts

def emojiStats(emojis, names, people):
    #emojis = {"total": 0, "types": {"type": x}, "sent": {"name": {"total": x, "type": y}}}
    sents = {}
    sentsAvg = {}

    for n in names:
        sents[n] = emojis["sent"][n]["total"]
        sentsAvg[n] = round(emojis["sent"][n]["total"]/people[n], 2)

    stats = {
        "1) total emojis": emojis["total"],
        "2) total different emojis": len(emojis["types"]),
        "3) top emojis": sorted(emojis["types"].items(), key=lambda item: item[1], reverse=True)[0:5],
        "4) sent most emojis": sorted(sents.items(), key=lambda item: item[1], reverse=True)[0],
        "5) sent most emojis on avg": sorted(sentsAvg.items(), key=lambda item: item[1], reverse=True)[0]
    }

    for n in names:
        stats[n] = {
            "total": sents[n], 
            "avg": sentsAvg[n], 
            "dif": len(emojis["sent"][n])-1, 
            "top": sorted(emojis["sent"][n].items(), key=lambda item: item[1], reverse=True)[1:6]
        }

    return stats     


