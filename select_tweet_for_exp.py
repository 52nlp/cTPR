import psycopg2
import cTPR
import os, sys, re
import random
import datetime
import copy

UPPER_NOUN_NUM = 7
LOWER_NOUN_NUM = 2
NG_WORDS = ['視聴率', '中出し', 'エロ', '風俗', 'ネトウヨ', 'ネット右翼', '缶バッジ', 'sougofollow']

con = psycopg2.connect("dbname=image_tagging host=localhost user=postgres")
concur = con.cursor()

concur.execute("delete from selected_tweets")
con.commit()

concur.execute("select distinct tweet_id from exp_lda30")
exp_lda30 = set(x for x in map(lambda y: y[0], concur.fetchall()))

concur.execute("select distinct tweet_id from exp_lda100")
exp_lda100 = set(x for x in map(lambda y: y[0], concur.fetchall()))

concur.execute("select distinct tweet_id from exp_lda200")
exp_lda200 = set(x for x in map(lambda y: y[0], concur.fetchall()))

concur.execute("select distinct tweet_id from exp_lda500")
exp_lda500 = set(x for x in map(lambda y: y[0], concur.fetchall()))

intersection = exp_lda30 & exp_lda100 & exp_lda200 & exp_lda500

i = 1
for each_tweet_id in intersection:
  print("\r{0}/{1}".format(i,len(intersection)), end="")
  i += 1
  
  # NGワードがtweet内にあるか検閲
  concur.execute('''select distinct tweet from origin_dataset where tweet_id=%s''', (each_tweet_id,))
  tweet = concur.fetchone()[0]
  
  ng_flag = False
  for each_ng_word in NG_WORDS:
    if each_ng_word in tweet:
      ng_flag = True
      break
  
  if ng_flag:
    continue
  
  # 名詞数が規定範囲内かどうか検閲
  concur.execute('''select count(*) from (select distinct word from preprocess 
    where tweet_id=%s) as a''', (each_tweet_id,))
  noun_num = concur.fetchone()[0]
  
  if noun_num < LOWER_NOUN_NUM or noun_num > UPPER_NOUN_NUM:
    continue

  concur.execute('''insert into selected_tweets (tweet_id) values (%s)''', (each_tweet_id,))
  con.commit()

#for tweet_id in true_intersection:
#  concur.execute('''insert into selected_tweets (tweet_id) values (%s)''', (tweet_id,))
#  con.commit()

#cursor.execute("select distinct topic_id from text_with_label order by topic_id")
#topic_id_list = [x for x in map(lambda y: y[0], cursor.fetchall())]
#
#random.seed(datetime.datetime.now())
#
#for each_topic_id in topic_id_list:
#  cursor.execute("""select distinct a.tweet_id from evaluate_exp_lda as a, text_with_label as b 
#    where a.tweet_id=b.tweet_id and b.topic_id=%s""", (each_topic_id,))
#  tweet_id_list = [x for x in map(lambda y: y[0], cursor.fetchall())]
#  
#  chosen_tweet_id = random.choice(tweet_id_list)
#  
#  #chosen_tag_lda = ""
#  #chosen_tag_raw = ""
#  #while chosen_tag_lda == chosen_tag_raw:
#  #  
#  #  chosen_tweet_id = random.choice(tweet_id_list)
#  #  
#  #  # Twitter-LDA
#  #  cursor.execute("select tag from evaluate_exp_lda where tweet_id=%s", (chosen_tweet_id,))
#  #  tag_list = [x for x in map(lambda y: y[0], cursor.fetchall())]
#  #  
#  #  chosen_tag_lda = random.choice(tag_list)
#  #  
#  #  
#  #  # 名詞そのまま
#  #  cursor.execute("select tag from evaluate_exp_raw where tweet_id=%s", (chosen_tweet_id,))
#  #  tag_list = [x for x in map(lambda y: y[0], cursor.fetchall())]
#  #  
#  #  chosen_tag_raw = random.choice(tag_list)
#  # 
#  # cursor.execute("""insert into evaluate_chosen_tags (tweet_id, lda_tag, raw_tag) 
#  # values (%s, %s, %s)""", (chosen_tweet_id, chosen_tag_lda, chosen_tag_raw))
#  
#  cursor.execute("""insert into evaluate_chosen_tweet (tweet_id) values (%s)""", (chosen_tweet_id,))
#  
#  con.commit()

concur.close()
con.close()

