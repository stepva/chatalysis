import json
from datetime import datetime

with open("message_1.json") as chat:
    data = json.load(chat)

ps = data["participants"]
ms = data["messages"]
total = len(ms)
first = str(datetime.fromtimestamp(ms[-1]["timestamp_ms"]//1000))
last = str(datetime.fromtimestamp(ms[0]["timestamp_ms"]//1000))

info = {
    "from": first,
    "to": last,
    "total": total
}

def getNames():
    ns = []
    for i in range(len(ps)):
        ns.append(ps[i]["name"])
    return ns

def msgCount(names):
    for n in names:
        info[n] = (sum(1 for i in range(total) if ms[i]["sender_name"]==n))
    return info

def imgCount(names):
    sum_img = sum(1 for i in range(total) if "photos" in ms[i])
    info["total_images"] = sum_img
    if sum_img > 0:
        for n in names:
            info[n + " images"] = (sum(1 for i in range(total) if "photos" in ms [i] and ms[i]["sender_name"]==n))
    return info

def gifCount(names):
    sum_gif = sum(1 for i in range(total) if "gifs" in ms[i])
    info["total_gifs"] = sum_gif
    if sum_gif > 0:
        for n in names:
            info[n + " gifs"] = (sum(1 for i in range(total) if "gifs" in ms [i] and ms[i]["sender_name"]==n))
    return info

def audioCount(names):
    sum_aud = sum(1 for i in range(total) if "audio_files" in ms[i])
    info["total_audio"] = sum_aud
    if sum_aud > 0:
        for n in names:
            info[n + " audio"] = (sum(1 for i in range(total) if "audio_files" in ms [i] and ms[i]["sender_name"]==n))
    return info

names = getNames()
msgCount(names)
imgCount(names)
gifCount(names)
audioCount(names)

print(json.dumps(info, indent=2))
print("ahoj testuju github")


def imgs():
    return sum(1 for i in range(total) if "photos" in ms[i])
def gifs():
    return sum(1 for i in range(total) if "gifs" in ms[i])
def audios():
    return sum(1 for i in range(total) if "audio_files" in ms[i])
def contentCount():
    return sum(1 for i in range(total) if "content" in ms[i])
if audios()+gifs()+imgs()+contentCount()==total:
    print("ano")
