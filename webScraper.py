#!/usr/bin/env python

import json
import urllib
import re
import unicodedata
from HTMLParser import HTMLParser

#putting variables here doesn't seem right, and I'm sure I can move the constAddr1 and constAddr3 variables
page = ""
constAddr1 = "http://en.wikipedia.org/w/api.php?format=json&action=query&titles="
addr2 = ""
constAddr3 = "&prop=revisions&rvprop=content"
htmlText = ""
data = ""
lines = ""

def whichPage():
    global page
    global constAddr1
    global constAddr3
    global addr2
    global lines
    lines = open('sitesToGet.txt').readlines()
    addr2 = lines[0][:-1]
    page = constAddr1 + addr2 + constAddr3

def getPage():
    global htmlText
    global page
    htmlfile = urllib.urlopen(page)
    htmlText = htmlfile

#removes the html tags but keeps content between them
def removeTags(html):
    global data
    global htmlText
    s = MLStripper()
    s.feed(html)
    data = s.get_data()

def removeFirstSiteToGet():
    f = open('sitesToGet.txt').readlines()
    siteFile = open('sitesToGet.txt', 'w')
    for i in range(1, len(f) - 1):
        siteFile.write(f[i])
    siteFile.close()

def getContent():
    global htmlText
    global data
    data = json.load(htmlText)
    data = data["query"]["pages"]
    data = data[data.keys()[0]]
    #this try/except checks if the page is missing
    #if it is, it'll run cleanly. If it's not missing
    #then the key "revisions" exists and there won't
    #be a problem...hopefully
    try:
        data["missing"]
        removeFirstSiteToGet()
        print " : page missing",
        return 0
    except KeyError:
        data = data["revisions"]
        data = data[-1] #I don't even know what's going on here, it works, not changing it now
        data = data["*"]
        return 1

def setupRedirect():
    global data
    p = re.compile('\[\[.*?\]\]')
    rawText = re.search(p, data).group(0)
    rawText = rawText[2:]
    rawText = rawText[:-2]
    words = rawText.split('|')
    link = words[0]
    f = open('sitesToGet.txt').readlines()
    siteFile = codes.open('sitesToGet.txt', 'w', "UTF-8")
    siteFile.write(link + "\n")
    for i in range(1, len(lines) - 1):
        siteFile.write(f[i])
    siteFile.close()

def checkRedirect():
    global data
    if data.find('REDIRECT') >= 0:
        setupRedirect()
        print " : redirected, ignoring",
        return 0
    return 1

#removes everything from the section onwards
def removeReferences():
    global data
    if data.find("==References==") >= 0:
        data = data[:data.find("==References==") - 1]
    if data.find("==See also==") >= 0:
        data = data[:data.find("==See also==") - 1]
    if data.find("==Notes==") >= 0:
        data = data[:data.find("==Notes==") - 1]

#removes the infobox because it's rarely natural
def removeInfobox():
    global data
    p = re.compile('\|\s.*')
    data = re.sub(p, '', data)
    p = re.compile('\{\{[iI]nfobox.*?\}\}', re.S)
    data = re.sub(p, '', data)

#removes the cite tags
def removeCite():
    global data
    p = re.compile('\{\{[cC]ite.*?\}\}', re.S)
    data = re.sub(p, '', data)

#removes wikitables because they are rarely natural
def removeWikitables():
    global data
    p = re.compile('\{\|\sclass=\"wikitable\".*?\|}', re.S)
    data = re.sub(p, '', data)

#must come after removeReferences
#removes the heading of a section because it's not natural
def removeHeadings():
    global data
    p = re.compile('==*.*?==*')
    data = re.sub(p, '', data)
    p = re.compile('\{\{[mM]ain.*?\}\}')
    data = re.sub(p, '', data)

#removes File elements, generally describing an image
def removeFile():
    global data
    p = re.compile('\[\[[fF]ile.*?\]\].*?\..*?\]\]')
    data = re.sub(p, '', data)
    p = re.compile('\[\[[fF]ile.*?\|thumb\|.*?\]\]')
    data = re.sub(p, '', data)

#removes what redirects to this page because it's not natural
def removeRedirected():
    global data
    p = re.compile('\{\{.*?\|.*?\}\}')
    data = re.sub(p, '', data)

#removes reference tags (and everything between) because they are not natural
def removeRefTags():
    global data
    p = re.compile('<ref>.*?</ref>', re.S)
    data = re.sub(p, '', data)

#removes code tags (and everything between) because they are not natural
def removeCode():
    global data
    p = re.compile('<code>.*?</code>', re.S)
    data = re.sub(p, '', data)

#remove double open double close {} (and everything between) because the text is rarely natural between them
def removeBraces():
    global data
    p = re.compile('\{\{.*?\}\}')
    data = re.sub(p, '', data)

#remove certain punctuation marks
def removePunctuation():
    global data
#    p = re.compile('[\'\"]')
    p = re.compile('\"')
    data = re.sub(p, '', data)
    p = re.compile('\&nbsp\;')
    data = re.sub(p, ' ', data)

#replaces newline characters and puts everything on a single line. This can be made more efficient
def removeNewLine():
    global data
    p = re.compile('\n')
    data = re.sub(p, '', data)
    p = re.compile('\.')
    data = re.sub(p, '. ', data)
    p = re.compile('\s\s')
    data = re.sub(p, ' ', data)

#everything that needs to be removed
def removals():
    removeRefTags()
    removeCode()
    removeTags(data)
    removeWikitables()
    removeInfobox()
    removeReferences()
    removeCite()
    removeHeadings()
    removeRedirected()
    removeFile()
    removeBraces()
    removePunctuation()
    removeNewLine()

#finds all the links left on the page after removal, and writes them to file and replaces the link with the correct word in the data
def getLinksFromPage():
    global data
    siteFile = open('sitesToGet.txt', 'a')
    p = re.compile('\[\[.*?\]\]')
    rawText = re.search(p, data)
    while rawText:
        rawText = rawText.group(0)
        rawText = rawText[2:]
        rawText = rawText[:-2]
        words = rawText.split('|')
        link = words[0]
        word = words[len(words) - 1]
        data = re.sub(p, word, data, 1)
        if link.find("#") < 0:
            siteFile.write(link + "\n")
        rawText = re.search(p, data)
    siteFile.close()

#write the resulting data to a file
#totalDown.txt stores a single number, which is used as a filename
def savePage():
    global data
    f = open('totalDown.txt', 'r')
    fileNumber = f.readline()[:-1]
    f.close()
    fileName = "/media/usbstick/wikiPages/" + fileNumber + ".txt" #change this line to save to a different location
    f = open(fileName, 'w')
    f.write(data)
    f.close()
    fileNumber = int(fileNumber)
    fileNumber += 1
    f = open('totalDown.txt', 'w')
    f.write(str(fileNumber) + "\n")
    f.close()

def parse():
    global data
    if getContent() == 1:
        if checkRedirect() == 0:
            return 0
        removals()
        data = unicodedata.normalize('NFKD', data).encode('UTF-8', errors='ignore')
        getLinksFromPage()
        savePage()
        return 1
    return 0

#updates all the necessary files
#sitesCompleted.txt lists all the sites that have been downloaded
#sitesToGet.txt lists all the sites that have been found to exist from finding links for them.
def updateFiles():
    global lines
    global addr2
    f = open('sitesCompleted.txt', 'a')
    f.write(addr2 + " | " + page + "\n")
    f.close()
    lines = open('sitesToGet.txt').readlines()
    f = open('sitesToGet.txt', 'w')
    for i in range(1, len(lines) - 1):
        f.write(lines[i])
    f.close()

def main():
    global addr2
    for i in range(0, 1000): #change the upper bound on the range to scrape more pages
        whichPage()
        print "Working on: " + addr2,
        getPage()
        if parse() == 1:
            updateFiles()
        print ""

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)
    def get_data(self):
        return ''.join(self.fed)

if __name__ == "__main__":
    main()
