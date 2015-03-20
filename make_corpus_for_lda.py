from gensim import corpora
from gensim import models
import psycopg2
import sys

DBPATH = "dbname=image_tagging host=localhost user=postgres"

topic_num_list = [30, 100, 200, 500]

if len(sys.argv) != 2:
  print("usage: python3.x make_corpus_for_lda.py <the number of topic>")
  exit(1)

topic_num = int(sys.argv[1])

if not topic_num in topic_num_list:
  print("the number of topic is whether 30, 100, 200, 500")
  exit(1)

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute("select tweet_id, word, count from preprocess order by tweet_id")

res = concur.fetchall()

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
    
    if count == len(res)-1:
      word_list.append(tmp_word_list)
  else:
    for i in range(term_count):
      tmp_word_list.append(each_res[1])
    
    if count == len(res)-1:
      word_list.append(tmp_word_list)
  
  count += 1

dictionary = corpora.Dictionary(word_list)

dictionary.save_as_text('lda_corpus.txt')

id_corpus = [dictionary.doc2bow(x) for x in word_list]
corpora.MmCorpus.serialize('lda_corpus.mm', id_corpus)
mm = corpora.MmCorpus('lda_corpus.mm')

lda = models.LdaModel(corpus=mm, id2word=dictionary, num_topics=topic_num)

lda.save('lda_results.model')
