import psycopg2
import os, sys


DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute('select distinct tweet_id from answer')
tweet_id_list = [x for x in map(lambda y: y[0], concur.fetchall())]

histgram_dic = {}
for each_tweet_id in tweet_id_list:
  concur.execute('''select distinct tag from answer where tweet_id=%s''', (each_tweet_id,))
  tag_set = { x for x in map(lambda y: y[0], concur.fetchall()) }
  
  good_num = 0
  bad_num = 0
  for each_tag in tag_set:
    concur.execute('''select score from answer where tweet_id=%s and tag=%s
      ''', (each_tweet_id, each_tag))
    score = concur.fetchone()[0]
    
    if score is 1:
      good_num += 1
    else:
      bad_num += 1
  
  if not bad_num in histgram_dic.keys():
    histgram_dic[bad_num] = 1
  else:
    histgram_dic[bad_num] += 1

print("元データのノイズ数分布")
for k, v in sorted(histgram_dic.items(), key=lambda x: x[0]):
  print("{0},{1}".format(k, v))
  
