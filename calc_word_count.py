import psycopg2
import cTPR
import re
import os

DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
cursor = con.cursor()

# テーブルを初期化
cursor.execute("delete from word_count")
con.commit()

cursor.execute('select topic_id from text_with_label group by topic_id order by topic_id')
topic_id_list = [x for x in map(lambda y: y[0], cursor.fetchall())]

for each_topic_id in topic_id_list:
  word_count = {}

  cursor.execute('''select b.tweet from text_with_label as a,
    twipple as b where a.tweet_id=b.tweet_id and a.topic_id=%s''', (each_topic_id,))
  tweets = cursor.fetchall()
  for each_tweet in tweets:
    tweet = each_tweet[0]
    
    f = open('tweet.txt', 'w')
    f.write(tweet)
    f.close()
    
    cmd = 'mecab tweet.txt'
    proc = os.popen(cmd)
    result = proc.read()
    proc.close()

    result = re.sub(r'\n', '\t', result)

    taggered_list = result.split('\t')
    for i in range(len(taggered_list))[1::2]:
      surface = taggered_list[i-1]
      feature = taggered_list[i]
      try:
        if cTPR.cTPR.detect_noise(feature):
          if not surface in word_count.keys():
            word_count[surface] = 1
          else:
            word_count[surface] += 1
      
      except:
        print(tweet)
          
  for k, v in word_count.items():
    cursor.execute('insert into word_count (topic_id, word, count) values (%s, %s, %s)',
      (each_topic_id, k, v))
  
  con.commit()

cursor.close()
con.close()




