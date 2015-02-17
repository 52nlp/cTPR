import psycopg2
import os, sys


DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute('select distinct tweet_id from answer')
tweet_id_list = [x for x in map(lambda y: y[0], concur.fetchall())]

good_sum = 0
bad_sum = 0
good_rate_sum = 0
fmeasure_sum = 0
good_only_num = 0
good_img_sum = 0
res_dic = {}
for each_tweet_id in tweet_id_list:
  concur.execute('''select distinct tag from answer where tweet_id=%s''', (each_tweet_id,))
  tag_set = { x for x in map(lambda y: y[0], concur.fetchall()) }
  
  good_num = 0
  bad_num = 0
  for each_tag in tag_set:
    concur.execute('''select score from answer where tweet_id=%s and tag=%s
      ''', (each_tweet_id, each_tag))
    score = concur.fetchone()[0]
    
    if score is 1:
      good_num += 1
      good_sum += 1
    else:
      bad_num += 1
      bad_sum += 1
  
  if good_num > 0 and bad_num == 0:
    good_only_num += 1
  
  if good_num > 0:
    good_img_sum += 1
  
  res_dic[each_tweet_id] = {'good_num': good_num, 'bad_num': bad_num}
  
  good_rate_sum += good_num / (good_num + bad_num)
  fmeasure_sum += 2*good_num*1.0 / (good_num + 1.0)

good_precision = round(good_sum / (good_sum + bad_sum), 3)
fmeasure = round(2*good_precision*1.0 / (good_precision + 1.0), 3)
ave_good_presicion = round(good_rate_sum / len(tweet_id_list), 3)
ave_fmeasure = round(fmeasure_sum / len(tweet_id_list), 3)

print('''正解タグ
全体の適合率: {0}
全体の再現率: {1}
F値: {2}
適合率の平均: {3}
再現率の平均: {4}
F値の平均: {5}
'''.format(good_precision, 1.0, fmeasure, ave_good_presicion, 1.0, ave_fmeasure))



print('''除去したノイズタグ(一切除去していないため全て0）
全体の適合率: {0}
全体の再現率: {1}
F値: {2}
適合率の平均: {3}
再現率の平均: {4}
F値（平均）: {5}
'''.format(0,0,0,0,0,0))

good_only_rate = round(good_only_num / len(res_dic), 3)
good_img_rate = round(good_img_sum / len(res_dic), 3)

good_and_bad_img_sum = good_img_sum - good_only_num
good_and_bad_img_rate = round(good_and_bad_img_sum / len(res_dic), 3)

print('''正解タグのみの割合: {0}
正解タグとノイズタグを含む割合： {1}
正解タグを含む割合： {2}
'''.format(good_only_rate, good_and_bad_img_rate, good_img_rate))



