# データセットの前処理を実行する．
# 8tweet以上しているユーザの投稿したtweetで，尚かつあらゆる品詞を計上して
# 3単語以上を含むtweetのみ抽出．

import psycopg2
import cTPR
import os, sys
import parse_proc
import datetime

# DBに接続
DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
cursor = con.cursor()

cursor.execute("delete from prepreprocess")
con.commit()

# 指定期日のtweetのうち8tweet以上しているユーザによるtweetのみを抽出
begin_time = datetime.datetime(year=2014, month=12, day=11)
end_time = datetime.datetime(year=2014, month=12, day=18)

cursor.execute("""select user_id from (select user_id, count(*) as num from 
  (select distinct on (tweet_id) user_id from origin_dataset where time between %s and %s) as a 
  group by user_id) as b where num > 7""", (begin_time, end_time))

users = [ x for x in map(lambda x: x[0], cursor.fetchall())]
total_user_num = len(users)

parser = parse_proc.Parser()
counter = 1
print("scanning each user's tweets")

# あらゆる品詞を計上して３単語以上が含まれているtweetのみをテーブル"preprocess"に登録
for each_user_id in users:
  print("{0}/{1}\r".format(counter, total_user_num), end="")

  cursor.execute("""select distinct on (tweet_id) tweet_id, tweet from origin_dataset 
    where user_id=%s and time between %s and %s""", (each_user_id, begin_time, end_time))
  tweets = cursor.fetchall()

  for each_tweet in tweets:
    tweet_id = each_tweet[0]
    tweet = each_tweet[1]
    
    parser.parse(tweet)
    
    if len(parser.raw_list) > 2:
      for surface, count in parser.count_dic.items():
        cursor.execute("""insert into prepreprocess (user_id, tweet_id, word, count) values 
            (%s, %s, %s, %s)""", (each_user_id, tweet_id, surface, count))
        
        con.commit()
  
  counter += 1

cursor.close()
con.close()

