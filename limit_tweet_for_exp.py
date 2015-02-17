import psycopg2
import cTPR
import os, sys, re
import random
import datetime

TWEET_NUM = 300

con = psycopg2.connect("dbname=image_tagging host=localhost user=postgres")
concur = con.cursor()

concur.execute("delete from evaluate_chosen_tweet")
con.commit()

concur.execute("select distinct tweet_id from selected_tweets order by tweet_id")

tweet_id_list = [x for x in map(lambda y: y[0], concur.fetchall())]

random.seed(datetime.datetime.now())

random.shuffle(tweet_id_list)

limited_tweet_list = tweet_id_list[:TWEET_NUM]

for each_tweet_id in limited_tweet_list:
  concur.execute('''insert into evaluate_chosen_tweet (tweet_id, censorship) values (%s, %s)
    ''', (each_tweet_id, -1))
  con.commit()

concur.close()
con.close()
