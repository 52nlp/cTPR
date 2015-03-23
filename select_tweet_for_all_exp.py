import psycopg2
import cTPR
import os, sys, re
import random
import datetime
import copy

con = psycopg2.connect("dbname=image_tagging host=localhost user=postgres")
concur = con.cursor()

concur.execute("delete from answer_all")

concur.execute("select distinct tweet_id from answer")
answer = set(x for x in map(lambda y: y[0], concur.fetchall()))

concur.execute("select distinct tweet_id from exp_rawlda30")
exp_rawlda30 = set(x for x in map(lambda y: y[0], concur.fetchall()))

concur.execute("select distinct tweet_id from exp_rawlda100")
exp_rawlda100 = set(x for x in map(lambda y: y[0], concur.fetchall()))

concur.execute("select distinct tweet_id from exp_rawlda200")
exp_rawlda200 = set(x for x in map(lambda y: y[0], concur.fetchall()))

concur.execute("select distinct tweet_id from exp_rawlda500")
exp_rawlda500 = set(x for x in map(lambda y: y[0], concur.fetchall()))

intersection = exp_rawlda30 & exp_rawlda100 & exp_rawlda200 & exp_rawlda500 & answer

for each_tweet_id in intersection:
  concur.execute('''insert into answer_all (tweet_id) values (%s)''', (each_tweet_id,))

con.commit()

concur.close()
con.close()


