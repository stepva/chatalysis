# Chatalysis

Chatalysis lets you analyse and, more importantly, visualise stats from your own Facebook Messenger chats in a nice and clean way, which is easily shareable with your friends. It works for group chats, too, and includes emojis and reactions as well.

## Installation

1. Download your messages from <https://www.facebook.com/dyi/>. You only need to select Messages and make sure to choose JSON as the Format and Low for Media Quality. It will take Facebook some time (several hours) to prepare your file and you can expect to be few gigabytes large.
> *If you want to select the Time Range, the end date is not included - i.e. if you choose 1st of December, it will only download messages up to the end of 30th of November.*
2. Download chatalysis in a zip folder and extract it wherever you want to. 
3. Move the "messages" folder which you downloaded from Facebook into the extracted (chatalysis-master) folder.
4. Download [Python](https://www.python.org/downloads/) and [Node.js](https://nodejs.org/en/download/) if you do not have them installed.
5. In your command line, locate the downloaded chatalysis folder, for example:
```
    cd Desktop/chatalysis-master
```
6. Install required packages:
```
    python install -r requirements.txt
    npm install
```
7. Now you can finally run chatalysis!
```
    python chatalysis
```
or, for example,
```
    python Desktop/chatalysis-master/chatalysis
```

