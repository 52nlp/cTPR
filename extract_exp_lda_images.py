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

concur.execute("delete from evaluate_exp_lda")
con.commit()

print("processing on each topic_id")

concur.execute("select distinct topic_id from text_with_label order by topic_id")

topic_id_list = [x for x in map(lambda x: x[0], concur.fetchall())]

for each_topic_id in topic_id_list:
  base_str = "\rtopic_id: {0}/{1} ".format(each_topic_id+1, len(topic_id_list))

  print(base_str+"fetching tweets    ", end="")

  concur.execute("""select distinct user_id from text_with_label 
    where topic_id=%s and confidence=1.0""", (each_topic_id,))

  target_user = [x for x in map(lambda y: y[0], concur.fetchall())]

  tweet_list = []
  for each_user_id in target_user:
    concur.execute('''select distinct b.tweet from text_with_label as a, origin_dataset as b 
      where a.tweet_id = b.tweet_id and a.topic_id=%s and a.user_id=%s''', (each_topic_id, each_user_id))
    
    results = concur.fetchall()
    
    tweet_list.extend(list(x for x in map(lambda y: y[0], results)))
    

  cTPR_components = cTPR.cTPR(each_topic_id, WINDOW_SIZE, DAMPING_FACTOR, ITERATION, DBPATH)

  # cTPRクラスのmake_graphメソッドを活用してワードグラフを作成する
  print(base_str+"making word graph   ", end="")
  cTPR_components.make_word_graph(tweet_list)

  # cTPRクラスのrun_pagerankメソッドを活用してキーワードのスコア付けをする
  print(base_str+"running pagerank    ", end="")
  cTPR_components.run_pagerank()

  top_res = cTPR_components.get_top_m(TOP_M)

  print(base_str+"registering tags    ", end="")
  
  for each_tag in top_res:
    concur.execute("""select distinct a.tweet_id from preprocess as a, text_with_label as b 
      where a.tweet_id=b.tweet_id and b.topic_id=%s and a.word=%s""", (each_topic_id, each_tag[0]))
    
    results = concur.fetchall()
    
    for each_row in results:
      tweet_id = each_row[0]
      
      concur.execute("""insert into evaluate_exp_lda (tweet_id, tag) 
        values (%s, %s)""", (tweet_id, each_tag[0]))
      
      con.commit()

concur.close()
con.close()

