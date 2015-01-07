import psycopg2
import cTPR
import os, sys, re
import random
import datetime

con = psycopg2.connect("dbname=image_tagging host=localhost user=postgres")
cursor = con.cursor()

cursor.execute("delete from evaluate_chosen_tweet")
con.commit()

cursor.execute("select distinct tweet_id from text_with_label30")
text_with_label30 = set(x for x in map(lambda y: y[0], cursor.fetchall()))

cursor.execute("select distinct tweet_id from text_with_label100")
text_with_label100 = set(x for x in map(lambda y: y[0], cursor.fetchall()))

cursor.execute("select distinct tweet_id from text_with_label200")
text_with_label200 = set(x for x in map(lambda y: y[0], cursor.fetchall()))

cursor.execute("select distinct tweet_id from text_with_label500")
text_with_label500 = set(x for x in map(lambda y: y[0], cursor.fetchall()))

intersection = text_with_label30 & text_with_label100 & text_with_label200 & text_with_label500

for tweet_id in intersection:
  cursor.execute('''insert into selected_tweets (tweet_id) values (%s)''', (tweet_id,))
  con.commit()

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

cursor.close()
con.close()

