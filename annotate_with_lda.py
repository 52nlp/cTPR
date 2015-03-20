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

# 保存済みデータをロード
dictionary = corpora.Dictionary.load_from_text('lda_corpus.txt')

mm = corpora.MmCorpus('lda_corpus.mm')

lda = models.LdaModel.load('lda_results.model')

print(word_list[25])
  
print(dictionary.doc2bow(word_list[25]))

print(lda[dictionary.doc2bow(word_list[25])])
