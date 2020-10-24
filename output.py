from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

#basicStats = [people, photos, gifs, stickers, videos, audios, files, fromDay, toDay]

def mrHtml(names, basicStats, fromDay, toDay):
    file_loader = FileSystemLoader("resources")
    env = Environment(loader=file_loader)

    template = env.get_template('index.html')

    final = template.render(
        name1=names[0],
        name2=names[1],
        fromDay=fromDay,
        toDay=toDay,
        totalMessages=basicStats[0]["total"],
        totalImages=basicStats[1]["total"],
        totalGifs=basicStats[2]["total"],
        totalVideos=basicStats[4]["total"],
        totalStickers=basicStats[3]["total"],
        totalAudios=basicStats[5]["total"],
        totalFiles=basicStats[6]["total"],
        )

    return final
