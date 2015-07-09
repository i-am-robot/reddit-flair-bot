#I tore up and repurposed one of /u/GoldenSights's script <3
import traceback
import praw
import time
import sqlite3

'''USER CONFIGURATION'''

TRIGGER_PHRASES = ['Legit!', 'OP is legit'] # Not case sensitive
REPLY_MESSAGE = 'Changed flair!'

USERNAME  = "Beep-Boop-I-Am-Robot"
PASSWORD  = "redacted"

USERAGENT = "Python Flair Bot by /u/wildmonkeys"

SUBREDDIT = "monkeybottesting"

MAXPOSTS = 100

WAIT = 30
# Time between cycles
CLEANCYCLES = 10
# After this many cycles, the bot will clean its database
# Keeping only the latest (2*MAXPOSTS) items

'''All done!'''

numCycles = 1

sql = sqlite3.connect('flair.db')
print('Loaded SQL Database')
cur = sql.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS oldposts(id TEXT)')

sql.commit()

print('Logging in...')
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD) 

def flairbot():
	print('Cycle #%i' % numCycles)
    print('Searching %s.' % SUBREDDIT)
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = list(subreddit.get_comments(limit=MAXPOSTS))
    posts.reverse()
    for post in posts:
        # Anything that needs to happen every loop goes here.
        pid = post.id
		
        try:
            pauthor = post.author.name
        except AttributeError:
            # Author is deleted. We don't care about this post.
            continue

        #if pauthor.lower() in [USERNAME.lower()]:
            # Don't reply to yourself, robot!
        #    continue

        cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
        if cur.fetchone():
            #print('already in database')
            continue

        cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
        sql.commit()
        pbody = post.body.lower()
        if any(phrase.lower() == pbody for phrase in TRIGGER_PHRASES):
            print('Triggered')
            print(post.submission.author.name)
            r.set_flair(SUBREDDIT, post.submission.author.name, 'LEGIT')
            post.reply(REPLY_MESSAGE)

cycles = 0
while True:
    try:
        flairbot()
        cycles += 1
		numCycles +=1
    except Exception as e:
        traceback.print_exc()
    if cycles >= CLEANCYCLES:
        print('Cleaning database')
        cur.execute('DELETE FROM oldposts WHERE id NOT IN (SELECT id FROM oldposts ORDER BY id DESC LIMIT ?)', [MAXPOSTS * 2])
        sql.commit()
        cycles = 0
    print('Running again in %d seconds \n' % WAIT)
    time.sleep(WAIT)

    