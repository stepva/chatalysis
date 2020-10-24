from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

#basicStats = [0: people, 1: photos, 2: gifs, 3: stickers, 4: videos, 5: audios, 6: files]

def mrHtml(names, basicStats, fromDay, toDay):
    file_loader = FileSystemLoader("resources")
    env = Environment(loader=file_loader)

    template = env.get_template('index.html')

    name1 = names[0]
    name2 = names[1]

    final = template.render(
        name1=name1,
        name2=name2,
        fromDay=fromDay,
        toDay=toDay,
        totalMessages=basicStats[0]["total"],
        totalImages=basicStats[1]["total"],
        totalGifs=basicStats[2]["total"],
        totalVideos=basicStats[4]["total"],
        totalStickers=basicStats[3]["total"],
        totalAudios=basicStats[5]["total"],
        totalFiles=basicStats[6]["total"],
        messages1=basicStats[0].get(name1, 0),
        images1=basicStats[1].get(name1, 0),
        gifs1=basicStats[2].get(name1, 0),
        stickers1=basicStats[3].get(name1, 0),
        audios1=basicStats[5].get(name1, 0),
        videos1=basicStats[4].get(name1, 0),
        files1=basicStats[6].get(name1, 0),
        messages2=basicStats[0].get(name2, 0),
        images2=basicStats[1].get(name2, 0),
        gifs2=basicStats[2].get(name2, 0),
        stickers2=basicStats[3].get(name2, 0),
        audios2=basicStats[5].get(name2, 0),
        videos2=basicStats[4].get(name2, 0),
        files2=basicStats[6].get(name2, 0),
        )
    return final
