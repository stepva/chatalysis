from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
import locale
import os
locale.setlocale(locale.LC_ALL, '')

#basicStats = [0: people, 1: photos, 2: gifs, 3: stickers, 4: videos, 5: audios, 6: files]

def mrHtml(version, names, basicStats, fromDay, toDay):
    file_loader = FileSystemLoader("resources")
    env = Environment(loader=file_loader)

    template = env.get_template('index.html')

    path = os.getcwd()

    name1 = names[0]
    name2 = names[1]
    newNames = changeNames(names)
    
    pictures = getPics(newNames, path)
    picture1 = pictures.get(newNames[0], False) or f"{path}/resources/placeholder.jpg"
    picture2 = pictures.get(newNames[1], False) or f"{path}/resources/placeholder.jpg"

    final = template.render(
        version=version,
        name1=name1,
        name2=name2,
        fromDay=fromDay,
        toDay=toDay,
        picture1=picture1,
        picture2=picture2,
        totalMessages=s(basicStats[0]["total"]),
        totalImages=s(basicStats[1]["total"]),
        totalGifs=s(basicStats[2]["total"]),
        totalVideos=s(basicStats[4]["total"]),
        totalStickers=s(basicStats[3]["total"]),
        totalAudios=s(basicStats[5]["total"]),
        totalFiles=s(basicStats[6]["total"]),
        messages1=s(basicStats[0].get(name1, 0)),
        images1=s(basicStats[1].get(name1, 0)),
        gifs1=s(basicStats[2].get(name1, 0)),
        stickers1=s(basicStats[3].get(name1, 0)),
        audios1=s(basicStats[5].get(name1, 0)),
        videos1=s(basicStats[4].get(name1, 0)),
        files1=s(basicStats[6].get(name1, 0)),
        messages2=s(basicStats[0].get(name2, 0)),
        images2=s(basicStats[1].get(name2, 0)),
        gifs2=s(basicStats[2].get(name2, 0)),
        stickers2=s(basicStats[3].get(name2, 0)),
        audios2=s(basicStats[5].get(name2, 0)),
        videos2=s(basicStats[4].get(name2, 0)),
        files2=s(basicStats[6].get(name2, 0)),
        graphMessages=f"{path}/resources/jordanfisher_messages.png"
        )
    return final

def s(n):
    return "{0:n}".format(n)

def changeNames(names):
    no = 'ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝßàáâãäåçèéêëìíîïñòóôõöùúûüýÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſ'
    yes = 'AAAAAACEEEEIIIINOOOOOUUUUYsaaaaaaceeeeiiiinooooouuuuyyAaAaAaCcCcCcCcDdDdEeEeEeEeEeGgGgGgGgHhHhIiIiIiIiIiKkkLlLlLlLlLlNnNnNnNnNOoOoOoRrRrRrSsSsSsSsTtTtTtUuUuUuUuUuUuWwYyYZzZzZzs'
    newNames = []
    for n in names:
        s = list(n)
        s.remove(" ")
        for char in s:
            if char in no:
                ind = s.index(char)
                old = no.index(char)
                s[ind] = yes[old]
        newNames.append("".join(s).lower())
    return newNames

def getPics(newNames, path):
    pics = {}
    for n in newNames:
        for p in os.listdir(f"{path}/resources"):
            if p.startswith(n):
                pics[n] = f"{path}/resources/{p}"
    return pics
