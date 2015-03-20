from gensim import corpora
from gensim import models
import psycopg2

DOC_NUM = 4

DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

#concur.execute("select tweet_id, word from preprocess order by tweet_id")

concur.execute("delete from exp_rawlda")

concur.execute("""select distinct a.tweet_id, a.word, a.count 
  from preprocess as a, answer as b where a.tweet_id = b.tweet_id 
  order by tweet_id""")

res = concur.fetchall()

tweet_id_list = []
word_list = []
tmp_tweet_id = 0
tmp_word_list = []
count = 0
for each_res in res:
  term_count = each_res[2]
  
  if each_res[0] != tmp_tweet_id:
    if count > 0:
      word_list.append(tmp_word_list)
    
    tmp_word_list = []
    for i in range(term_count):
      tmp_word_list.append(each_res[1])
    
    tmp_tweet_id = each_res[0]
    tweet_id_list.append(tmp_tweet_id)
    
    if count == len(res)-1:
      word_list.append(tmp_word_list)
  else:
    for i in range(term_count):
      tmp_word_list.append(each_res[1])
    
    if count == len(res)-1:
      word_list.append(tmp_word_list)
  
  count += 1

# 保存済みデータをロード
dictionary = corpora.Dictionary.load_from_text('lda_corpus.txt')

mm = corpora.MmCorpus('lda_corpus.mm')

lda = models.LdaModel.load('lda_results.model')

#print(word_list[DOC_NUM], tweet_id_list[DOC_NUM])
##print(dictionary.doc2bow(word_list[DOC_NUM]))
#
#dist = lda[dictionary.doc2bow(word_list[DOC_NUM])]
#
#top_topic_id = sorted(dist, key=lambda x: x[1], reverse=True)[0][0]
#
#for each_tuple in sorted(dist, key=lambda x: x[1], reverse=True):
#  print(each_tuple)
#
#print(top_topic_id)
#print(lda.show_topic(top_topic_id, 20))
#
#annotate_word_list = []
#for each_topic_word in lda.show_topic(top_topic_id, 20):
#  annotate_word_list.append(each_topic_word[1])
#
#annotate_word_set = set(annotate_word_list)
#
#final_annotate_word_set = annotate_word_set.intersection(set(word_list[DOC_NUM]))
#
#print(final_annotate_word_set)

for i in range(len(word_list)):
  tweet_id = tweet_id_list[i]

  dist = lda[dictionary.doc2bow(word_list[i])]

  try:
    top_topic_id = sorted(dist, key=lambda x: x[1], reverse=True)[0][0]
  except:
    print(word_list[i])
    print(dist)
    continue

  annotate_word_list = []
  for each_topic_word in lda.show_topic(top_topic_id, 20):
    annotate_word_list.append(each_topic_word[1])

  annotate_word_set = set(annotate_word_list)

  final_annotate_word_set = annotate_word_set.intersection(set(word_list[i]))

  for each_word in final_annotate_word_set:
    concur.execute("""insert into exp_rawlda (tweet_id, tag) values (%s, %s)
      """, [tweet_id, each_word])
 
con.commit()

concur.close()
con.close()



