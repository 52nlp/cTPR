from gensim import corpora
from gensim import models
import psycopg2

DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute("select tweet_id, word from preprocess order by tweet_id")

res = concur.fetchall()

word_list = []
tmp_tweet_id = 0
tmp_word_list = []
count = 0
for each_res in res:
  if each_res[0] != tmp_tweet_id:
    word_list.append(tmp_word_list)
    
    tmp_word_list = []
    tmp_word_list.append(each_res[1])
    
    tmp_tweet_id = each_res[0]
    
    if count == len(res)-1:
      word_list.append(tmp_word_list)
  else:
    tmp_word_list.append(each_res[1])
  
  count += 1

dictionary = corpora.Dictionary(word_list)

dictionary.save_as_text('lda_corpus.txt')

id_corpus = [dictionary.doc2bow(x) for x in word_list]
corpora.MmCorpus.serialize('lda_corpus.mm', id_corpus)
mm = corpora.MmCorpus('lda_corpus.mm')

lda = models.LdaModel(corpus=mm, id2word=dictionary, num_topics=30)

lda.save('lda_results.model')
