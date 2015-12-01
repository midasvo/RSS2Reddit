import requests
from bs4 import BeautifulSoup
import time
import praw
from urllib.parse import urlparse
import urllib.request
import os
from praw.handlers import MultiprocessHandler


# Database file, saves submitted links
DB_FILE = "db.txt"
# Initialize the submissions list for global use
submissions = []
links = []
# Should we log?
LOGGING = True

# File to log to
LOG_FILE = "log.txt"

# Reddit credentials
REDDIT_USERNAME = "username"
REDDIT_PASSWORD = "password"


# Name of the subreddit we will submit to
SUBREDDIT = "SubredditName"

# The amount of submissions to get from subreddit to test against
SUBMISSION_LIMIT = 500

# Search subreddit submissions on: hot, top, new
SORT_CAT = "hot" # "hot", "top", "new"

# RSS URL to check for posts to submit
RSS_URL = "http://domainname.tld/rss"

# The time in seconds to sleep between running the bot
SLEEP_TIME = 1200

# The time in seconds to sleep between submitting links (skips already in database and subreddit)
SUBMIT_SLEEP = 600

def loginToReddit():
    r = praw.Reddit('/u/username | RSS2Reddit Worker')
    r.login(username=REDDIT_USERNAME, password=REDDIT_PASSWORD, disable_warning=True)
    return r

def createDB():
    if not os.path.exists(DB_FILE):
        log("Creating a new database")
        open(DB_FILE, 'w').close()
        file = open(DB_FILE, "a")
        file.write("<--- RSS2Reddit DATABASE FILE --->\n")
        ct = time.strftime("%c")
        file.write("Created on: " + ct +'\n')

        file.close()
    else:
        log("Using existing database")

def createLog():
    if not os.path.exists(LOG_FILE):
        log("Creating log file")
        open(LOG_FILE, 'w').close()
        file = open(LOG_FILE, "a")
        file.write("<--- RSS2Reddit LOG FILE --->\n")
        file.close()
    else:
        log("Using existing log file")



def fileInDB(url):
    found = False
    file = open(DB_FILE, "r")
    filelist = file.readlines()
    file.close()
    if url not in filelist:
        found=False
    else:
        found=True
    return found

def writeToDB(url):
    log("Writing " + url + " to " + DB_FILE)
    file = open(DB_FILE, "a")
    file.write(url+'\n')
    file.close()

def submit(r, t, l):
    r.submit(SUBREDDIT, t, url=l)
    writeToDB(l)
    log("Submitted " + l + " to " + SUBREDDIT)
    time.sleep(SUBMIT_SLEEP)

def getSubmissions(r):
    print(submissions)
    log("Getting submissions from /r/" + SUBREDDIT)
    subreddit = r.get_subreddit(SUBREDDIT)
    for submission in subreddit.get_hot(limit=SUBMISSION_LIMIT):
        if submission.url not in submissions:
            submissions.append(submission.url)

def inSubreddit(url):
    if url in submissions:
        return True

def check(r):
    links = getRSS()
    submissions = getSubmissions(r)
    for link in links:
        title = link[0]
        url = link[1]
        log("Checking " + url)
        if(fileInDB(url+'\n')):
            log("Found in " + DB_FILE + " ... No need to submit")
        else:
            log("Did not find " + url + " in " + DB_FILE)
            if(inSubreddit(url)):
                writeToDB(url)
            else:
                submit(r, title, url)


def getRSS():

    log("Requesting RSS from " + RSS_URL)
    request = requests.get(RSS_URL)
    soup = BeautifulSoup(request.text, 'lxml-xml')

    for link in soup.find_all('item'):
        linky = link.title.get_text(), link.link.get_text()
        links.append(linky)
    return links

def log(msg):
    if(LOGGING):
        file = open(LOG_FILE, "a")
        ct = time.strftime("%c")
        file.write("[" + ct + "] " + msg+'\n')
        file.close()

def cleanse():
    del links[:]
    del submissions[:]


def RSS2Reddit(r):
    cleanse()
    check(r)
    print("---------------------------")
    print("Links: ")
    print("---------------------------")
    print(links)
    print("---------------------------")
    print("Submissions: ")
    print("---------------------------")
    print(submissions)
    print("---------------------------")

def main():
    r = loginToReddit()

    createLog()
    createDB()
    while True: # Run all the time
        print("Running bot...")
        log("Running bot")
        RSS2Reddit(r)
        log("Sleeping for " + str(SLEEP_TIME) + " seconds")
        time.sleep(SLEEP_TIME)

main()
