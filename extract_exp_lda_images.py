import psycopg2
import cTPR
import os, sys, re

WINDOW_SIZE = 3 #ワードグラフを作成する際に使うウィンドウのサイズを指定
DAMPING_FACTOR = 0.1 #cTPRの計算式で使うdamping factor（他トピックからのジャンブ率）を指定
ITERATION = 100 #cTPRアルゴリズムのイテレーション数を指定
TOP_M = 20 #アノテーションに使うキーワードの数を指定
IMAGE_LIMIT = 30 #結果として使う画像の枚数を指定
USER_COUNT = 10 #トピック形成に貢献しているユーザを上位何名まで考慮するか（ワードグラフにも関係）
DBPATH = "dbname=image_tagging host=localhost user=postgres" #計算に使うデータを格納しているDBを指定

con = psycopg2.connect(DBPATH)
concur = con.cursor()

print("processing on each topic_id")

concur.execute("select distinct topic_id from text_with_label order by topic_id")

topic_id_list = [x for x in map(lambda x: x[0], concur.fetchall())]

for each_topic_id in topic_id_list:
  base_str = "\rtopic_id: {0}/{1} ".format(each_topic_id+1, len(topic_id_list))

  print(base_str+"fetching tweets    ", end="")

  concur.execute('''select user_id, distribution from topic_distribution_on_users 
    where topic_id=%s''', (each_topic_id,))

  score_dic = {}
  for each in concur:
    score_dic[each[0]] = each[1]

  concur.execute("select sum(count) from topic_counts_on_users where topic_id=%s", (each_topic_id,))
  total_topic_count = concur.fetchone()[0]

  concur.execute('''select user_id, count from topic_counts_on_users 
    where topic_id=%s''', (each_topic_id,))

  for each in concur:
    score_dic[each[0]] = score_dic[each[0]] * (each[1] / total_topic_count)

  target_user = []
  count = 0
  for k, v in sorted(score_dic.items(), key=lambda x: x[1], reverse=True):
    if v is 0:
      break

    target_user.append(k)

    count += 1
    if count >= USER_COUNT:
      break

  tweet_list = []
  tweet_id_list = []
  for each_user_id in target_user:
    concur.execute('''select distinct b.tweet, b.tweet_id from text_with_label as a, twipple as b 
      where a.tweet_id = b.tweet_id and a.topic_id=%s and a.user_id=%s''', (each_topic_id, each_user_id))

    results = concur.fetchall()

    tweet_list.extend(list(x for x in map(lambda y: y[0], results)))
    tweet_id_list.extend(list(x for x in map(lambda y: y[1], results)))
    
  #print(base_str+"done.\r", end="")

  cTPR_components = cTPR.cTPR(each_topic_id, WINDOW_SIZE, DAMPING_FACTOR, ITERATION, DBPATH)

  # cTPRクラスのmake_graphメソッドを活用してワードグラフを作成する
  print(base_str+"making word graph   ", end="")
  cTPR_components.make_word_graph(tweet_list)
  #print(base_str+"done.\r", end="")

  # cTPRクラスのrun_pagerankメソッドを活用してキーワードのスコア付けをする
  print(base_str+"running pagerank    ", end="")
  cTPR_components.run_pagerank()
  #print(base_str+"iteration finished.\r", end="")

  top_res = cTPR_components.get_top_m(TOP_M)

  concur.execute("""select distinct on (b.tweet) b.tweet, b.tweet_id
    from text_with_label as a, twipple as b 
    where a.tweet_id=b.tweet_id and a.topic_id=%s""", (each_topic_id,))

  rows = concur.fetchall()

  print(base_str+"registering tags    ", end="")
  for each_row in rows:
    tweet = each_row[0]
    tweet_id = each_row[1]

    f = open('tweet.txt', 'w')
    f.write(tweet)
    f.close()

    cmd = 'mecab tweet.txt'
    proc = os.popen(cmd)
    result = proc.read()
    proc.close()

    result = re.sub(r'\n', '\t', result)

    taggered_list = result.split('\t')

    contain_list = []
    for each_tag in top_res:
      if each_tag[0] in taggered_list:
        contain_list.append(each_tag[0])

    for each_contain_tag in contain_list:
      concur.execute("""insert into evaluate_exp_lda (tweet_id, tag) 
        values (%s, %s)""", (tweet_id, each_contain_tag))

      con.commit()

concur.close()
con.close()

