import psycopg2
import os, sys


TOPIC_NUM_LIST = [30, 100, 200, 500]

if len(sys.argv) is 1:
  print("トピック数を入力")
  exit()

topic_num = int(sys.argv[1])
if not topic_num in TOPIC_NUM_LIST:
  print("入力可能なトピック数は ", end="")
  
  for each in TOPIC_NUM_LIST:
    print("{0} ".format(each), end="")
  
  print("です．")
  exit()

DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute('''select distinct a.tweet_id from answer as a, answer_all as b 
  where a.tweet_id=b.tweet_id''')
tweet_id_list = [x for x in map(lambda y: y[0], concur.fetchall())]

lda_score = {}
except_score = {}
histgram_dic = {}
query = "select distinct tag from exp_lda{0} where tweet_id=%s".format(topic_num)
for each_tweet_id in tweet_id_list:
  concur.execute(query, (each_tweet_id,))
  tag_set = { x for x in map(lambda y: y[0], concur.fetchall()) }
  
  concur.execute('''select distinct tag from answer where tweet_id=%s''', (each_tweet_id,))
  except_tag_set = { x for x in map(lambda y: y[0], concur.fetchall()) } - tag_set
  
  good_num = 0
  bad_num = 0
  for each_tag in tag_set:
    concur.execute('''select score from answer 
      where tweet_id=%s and tag=%s''', (each_tweet_id, each_tag))
    score = concur.fetchone()[0]
    
    if score is 1:
      good_num += 1
    else:
      bad_num += 1
  
  if not bad_num in histgram_dic.keys():
    histgram_dic[bad_num] = 1
  else:
    histgram_dic[bad_num] += 1
  
  except_good_num = 0
  except_bad_num = 0
  for each_tag in except_tag_set:
    concur.execute('''select score from answer 
      where tweet_id=%s and tag=%s''', (each_tweet_id, each_tag))
    score = concur.fetchone()[0]
    
    if score is 1:
      except_good_num += 1
    else:
      except_bad_num += 1
  
  lda_score[each_tweet_id] = {'good_num': good_num, 'bad_num': bad_num}
  except_score[each_tweet_id] = {'good_num': except_good_num, 'bad_num': except_bad_num}

good_rate_sum = 0
good_only_num = 0
bad_only_num = 0
good_sum = 0
bad_sum = 0
zero_num = 0
for each_tweet_id, value in lda_score.items():
  each_good_num = value['good_num']
  each_bad_num = value['bad_num']
  
  good_sum += each_good_num
  bad_sum += each_bad_num
  
  if each_good_num > 0 and each_bad_num is 0:
    good_only_num += 1
  
  if each_good_num is 0 and each_bad_num > 0:
    bad_only_num += 1
  
  if each_good_num + each_bad_num == 0:
    zero_num += 1
  else:
    good_rate_sum += each_good_num / (each_good_num + each_bad_num)

good_rate = round(good_rate_sum / (len(lda_score) - zero_num), 3)
total_good_rate = round(good_sum / (good_sum + bad_sum), 3)

except_good_sum = 0
except_bad_sum = 0
except_bad_rate_sum = 0
zero_num = 0
for each_tweet_id, value in except_score.items():
  each_good_num = value['good_num']
  each_bad_num = value['bad_num']
  
  except_good_sum += each_good_num
  except_bad_sum += each_bad_num
  
  if each_good_num + each_bad_num is 0:
    zero_num += 1
  else:
    except_bad_rate_sum += each_bad_num / (each_good_num + each_bad_num)

except_bad_rate = round(except_bad_rate_sum / (len(except_score)-zero_num), 3)
remain_bad_rate = round(bad_sum / (bad_sum + except_bad_sum), 3)
total_tag_num = good_sum + bad_sum + except_good_sum + except_bad_sum

good_only_rate = round(good_only_num / len(lda_score), 3)
good_and_bad_rate = round((len(lda_score) - bad_only_num - good_only_num) / len(lda_score), 3)
bad_only_rate = 1.0 - good_only_rate - good_and_bad_rate

print('''正解タグのみの割合: {0}({1})
正解タグとノイズ両方を含む割合: {2}
ノイズタグのみを含む割合: {3}
正解タグ含有率の平均: {4}
付与したタグのうち正解だった数: {5} / {6} = {7}
全ノイズタグのうち除去できなかったタグの数: {8} / {9} = {10}
全タグ数: {11}
'''.format(good_only_rate, len(lda_score), good_and_bad_rate, bad_only_rate, good_rate, good_sum, good_sum+bad_sum, \
  total_good_rate, bad_sum, bad_sum+except_bad_sum, remain_bad_rate, total_tag_num))

good_recall_rate_sum = 0
fmeasure_sum = 0
zero_num = 0
for each_tweet_id in tweet_id_list:
  each_good_num = lda_score[each_tweet_id]['good_num']
  each_bad_num = lda_score[each_tweet_id]['bad_num']
  each_except_good_num = except_score[each_tweet_id]['good_num']
  
  if each_good_num + each_except_good_num is 0:
    zero_num += 1
  else:
    if each_good_num + each_bad_num != 0:
      precision = each_good_num / (each_good_num + each_bad_num)
    else:
      precision = 0
    
    if each_good_num + each_except_good_num != 0:
      recall = each_good_num / (each_good_num + each_except_good_num)
    else:
      recall = 0
    
    good_recall_rate_sum += recall
    
    if precision + recall != 0:
      fmeasure_sum += 2*precision*recall / (precision + recall)
  

ave_recall_rate  = round(good_recall_rate_sum / (len(lda_score)-zero_num), 3)

total_recall = round(good_sum / (good_sum+except_good_sum), 3)

good_fmeasure = round(2*total_good_rate*total_recall / (total_good_rate + total_recall), 3)
ave_good_fmeasure = round(fmeasure_sum / (len(tweet_id_list)-zero_num), 3)

print('''正解タグ
全体の適合率: {0}
全体の再現率: {1}
F値: {2}
適合率の平均: {3}
再現率の平均: {4}
F値（平均）: {5}
'''.format(total_good_rate, total_recall, good_fmeasure, good_rate, ave_recall_rate, ave_good_fmeasure))

except_bad_recall_rate_sum = 0
removed_fmeasure_sum = 0
zero_num = 0
for each_tweet_id in tweet_id_list:
  each_bad_num = lda_score[each_tweet_id]['bad_num']
  each_except_good_num = except_score[each_tweet_id]['good_num']
  each_except_bad_num = except_score[each_tweet_id]['bad_num']
  
  if each_bad_num + each_except_bad_num is 0:
    zero_num += 1
  else:
    if each_except_good_num + each_except_bad_num != 0:
      precision = each_except_bad_num / (each_except_good_num + each_except_bad_num)
    else:
      precision = 0
    
    if each_bad_num + each_except_bad_num != 0:
      recall = each_except_bad_num / (each_bad_num + each_except_bad_num)
    else:
      recall = 0
    
    except_bad_recall_rate_sum += recall
    
    if precision + recall != 0:
      removed_fmeasure_sum += 2*precision*recall / (precision + recall)
  

ave_bad_recall_rate  = round(except_bad_recall_rate_sum / (len(lda_score)-zero_num), 3)

removed_bad_precision = round(except_bad_sum / (except_good_sum + except_bad_sum), 3)

removed_bad_recall = round(except_bad_sum / (bad_sum + except_bad_sum), 3)

removed_bad_fmeasure = round(2*removed_bad_precision*removed_bad_recall / (removed_bad_precision + removed_bad_recall), 3)

ave_removed_bad_fmeasure = round(removed_fmeasure_sum / (len(tweet_id_list)-zero_num), 3)

print('''除去したノイズタグ
全体の適合率: {0}
全体の再現率: {1}
F値: {2}
適合率の平均: {3}
再現率の平均: {4}
F値（平均）: {5}
'''.format(removed_bad_precision, removed_bad_recall, removed_bad_fmeasure, except_bad_rate, ave_bad_recall_rate, ave_removed_bad_fmeasure))


print("提案手法適用後のノイズ数分布(トピック数:{0})".format(topic_num))
print("ノイズ数,画像数")
for k, v in histgram_dic.items():
  print("{0},{1}".format(k, v))








