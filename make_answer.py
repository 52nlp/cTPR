import psycopg2
import os, sys


DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute("delete from answer")

concur.execute('''select tweet_id from (select tweet_id, count(*) as num 
  from evaluate_results group by tweet_id) as a where num > 2''')

tweet_id_list = [x for x in map(lambda y: y[0], concur.fetchall())]

for each_tweet_id in tweet_id_list:
  concur.execute('''select tag, score from evaluate_results 
    where tweet_id=%s''', (each_tweet_id,))
  
  score_dic = {}
  for each_res in concur:
    tag = each_res[0]
    score = each_res[1]
    
    if not tag in score_dic.keys():
      score_dic[tag] = score
    else:
      score_dic[tag] += score
  
  for tag, score in score_dic.items():
    if score > 1:
      concur.execute('''insert into answer (tweet_id, tag, score) 
        values (%s, %s, %s)''',(each_tweet_id, tag, 1))
      con.commit()
    else:
      concur.execute('''insert into answer (tweet_id, tag, score) 
        values (%s, %s, %s)''',(each_tweet_id, tag, 0))
      con.commit()
 
concur.close()
con.close()
