import psycopg2
import re
import os, sys
from cTPR import cTPR

DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute("""select distinct a.tweet_id, a.tweet from twipple as a, 
  (select distinct tweet_id from evaluate_exp_lda) as b
  where a.tweet_id=b.tweet_id""")
results = concur.fetchall()

tweet_id_list = [x for x in map(lambda y: y[0], results)]
tweet_list = [x for x in map(lambda y: y[1], results)]

for i in range(len(tweet_id_list)):
  print("\r{0}/{1}".format(i+1, len(tweet_id_list)), end="")

  f = open('tweet.txt', 'w')
  f.write(tweet_list[i])
  f.close()

  cmd = 'mecab tweet.txt'
  proc = os.popen(cmd)
  result = proc.read()
  proc.close()

  result = re.sub(r'\n', '\t', result)

  taggered_list = result.split('\t')

  contain_list = []
  for j in range(len(taggered_list))[1::2]:
    surface = taggered_list[j - 1]
    feature = taggered_list[j]
    if cTPR.detect_noise(feature):
      contain_list.append(surface)

  for each_contain_tag in contain_list:
    concur.execute("""insert into evaluate_exp_raw (tweet_id, tag) 
      values (%s, %s)""", (tweet_id_list[i], each_contain_tag))

    con.commit()

print()

concur.close()
con.close()





