import praw
import config
import time
from datetime import datetime, date
import calendar
from twilio.rest import Client

# pip install -r requirements.txt to import necessary packages

reddit = praw.Reddit(client_id=config.personalUseScript,
                     client_secret=config.secret,
                     user_agent="keyboard-scrape",
                     username=config.redditUser,
                     password=config.redditPass)
subreddit = reddit.subreddit('mechmarket')


def scrape():
    idOfPosts = set()
    idOfPostsList = [None] * 20
    listIndex = 0

    while True:
        for submission in subreddit.new(limit=8):
            if submission.link_flair_text in ["Buying", "Selling"]:
                title = submission.title.lower()
                if ("rama" in title or "u80" in title) and submission.id not in idOfPosts:

                    if (idOfPostsList[listIndex % 20]):
                        idOfPosts.remove(idOfPostsList[listIndex % 20])

                    idOfPostsList[listIndex % 20] = submission.id
                    idOfPosts.add(submission.id)
                    listIndex += 1

                    client = Client(config.twilioSID, config.twilioToken)
                    client.messages.create(
                        to=config.cell, from_=config.twilioNum, body=submission.url)

        time.sleep(31)
        # to prevent integer overflow
        if listIndex % 20 == 0:
            listIndex = 0
        print(len(idOfPosts))


def scrapeLots():
    res = []
    items = ["rama", "u80", ]
    postBeforeStartOfDay = False
    # yesterday = date(2020, 10, 10)
    # we're 7 hrs behind UTC so today at 12:00 am is yesterday at 5pm
    yesterday = date.today()
    # will check all today + 7 hours of yesterday
    timestamp = calendar.timegm(yesterday.timetuple())
    print(timestamp)
    datetime.utcfromtimestamp(timestamp)
    submissions = subreddit.new(limit=1000)

    for submission in submissions:
        if submission.created_utc > timestamp:
            if submission.link_flair_text in ["Buying", "Selling"]:
                title = submission.title.lower()
                for each in items:
                    if each in title:
                        res.append(submission.url)

        else:
            # post made before yesterday
            postBeforeStartOfDay = True

    for each in res:
        print(each)

    # if true it means you've searched for all new posts from yesterday
    if postBeforeStartOfDay:
        print('searched all posts since yesterday')
    else:
        print('more posts since yesterday, change subreddit.new() to a higher limit')


scrapeLots()
