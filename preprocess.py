# データセットの２段階目の前処理を実行する．
# 10tweet以上に現れる名詞を70%以下のtweetに現れる名詞のみを抽出する．

import psycopg2
import cTPR
import os, sys
import parse_proc


DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute("delete from preprocess")

concur.execute("""select distinct on (tweet_id) user_id, tweet_id 
  from prepreprocess order by tweet_id""")

results = concur.fetchall()

user_id_list = [x for x in map(lambda y:y [0], results)]
tweet_id_list = [x for x in map(lambda y: y[1], results)]

border = len(tweet_id_list) * 0.7
print("border is {0}".format(border))

print("scanning each word")
for i in range(len(tweet_id_list)):
  print("{0}/{1}\r".format(i+1, len(tweet_id_list)), end="")

  each_tweet_id = tweet_id_list[i]
  each_user_id = user_id_list[i]

  concur.execute("""select distinct word, count from prepreprocess 
    where tweet_id=%s""", (each_tweet_id,))
  word_info_list = concur.fetchall()
  
  for each_word in word_info_list:
    word = each_word[0]
    count = each_word[1]
    
    concur.execute("""select count(*) from (select distinct tweet_id from prepreprocess 
      where and word=%s) as a""", (word,))
    
    appear_num = concur.fetchone()[0]
    
    if appear_num >= 10 and appear_num <= border:
      concur.execute("""insert into preprocess (user_id, tweet_id, word, count) 
        values (%s, %s, %s, %s)""", (each_user_id, each_tweet_id, word, count))
      
      con.commit()

concur.close()
con.close()


