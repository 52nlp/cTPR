import psycopg2
import cTPR
import os, sys, re
import random
import datetime

TWEET_NUM = 30
NOUN_NUM = 10

con = psycopg2.connect("dbname=image_tagging host=localhost user=postgres")
cursor = con.cursor()

cursor.execute("delete from evaluate_chosen_tweet")
con.commit()

cursor.execute("select distinct tweet_id from selected_tweets order by tweet_id")

tweet_id_list = [x for x in map(lambda y: y[0], cursor.fetchall())]

random.seed(datetime.datetime.now())

random.shuffle(tweet_id_list)

limited_tweet_list = tweet_id_list[:TWEET_NUM]

for each_tweet_id in limited_tweet_list:
  cursor.execute('''insert into evaluate_chosen_tweet (tweet_id) values (%s)
    ''', (each_tweet_id,))
  con.commit()

cursor.close()
con.close()
