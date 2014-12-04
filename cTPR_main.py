import psycopg2
import cTPR
import os, sys

TOPIC_ID = 4 #アノテーションの対象となるトピックを指定
WINDOW_SIZE = 3 #ワードグラフを作成する際に使うウィンドウのサイズを指定
DAMPING_FACTOR = 0.1 #cTPRの計算式で使うdamping factor（他トピックからのジャンブ率）を指定
ITERATION = 100 #cTPRアルゴリズムのイテレーション数を指定
TOP_M = 10 #アノテーションに使うキーワードの数を指定
IMAGE_LIMIT = 30 #結果として使う画像の枚数を指定
USER_COUNT = 5 #トピック形成に貢献しているユーザを上位何名まで考慮するか（ワードグラフにも関係）
DBPATH = "dbname=image_tagging host=localhost user=postgres" #計算に使うデータを格納しているDBを指定

con = psycopg2.connect(DBPATH)
concur = con.cursor()

print("fetching tweets.")

concur.execute('''select user_id, distribution from topic_distribution_on_users 
  where topic_id=%s''', (TOPIC_ID,))

score_dic = {}
for each in concur:
  score_dic[each[0]] = each[1]

concur.execute("select sum(count) from topic_counts_on_users where topic_id=%s", (TOPIC_ID,))
total_topic_count = concur.fetchone()[0]

concur.execute('''select user_id, count from topic_counts_on_users 
  where topic_id=%s''', (TOPIC_ID,))

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
    where a.tweet_id = b.tweet_id and a.topic_id=%s and a.user_id=%s''', (TOPIC_ID, each_user_id))

  results = concur.fetchall()

  tweet_list.extend(list(x for x in map(lambda y: y[0], results)))
  tweet_id_list.extend(list(x for x in map(lambda y: y[1], results)))
  
print("done.")

cTPR_components = cTPR.cTPR(TOPIC_ID, WINDOW_SIZE, DAMPING_FACTOR, ITERATION, DBPATH)

# cTPRクラスのmake_graphメソッドを活用してワードグラフを作成する
print("making word graph.")
cTPR_components.make_word_graph(tweet_list)
print("done.")

# cTPRクラスのrun_pagerankメソッドを活用してキーワードのスコア付けをする
print("running pagerank.")
cTPR_components.run_pagerank()
print("iteration finished.")

top_res = cTPR_components.get_top_m(TOP_M)

print("top {0} keywords are as below.".format(TOP_M))
for each in top_res:
  print("{0}\t{1}".format(each[0], each[1]))


# 画像へアノテーションした結果を出力
image_dic = {}
for each_tweet_id in tweet_id_list:
  concur.execute("""select distinct on (b.tweet) b.id, b.tweet, b.image 
    from text_with_label as a, twipple as b
    where a.tweet_id=b.tweet_id and a.tweet_id=%s""", (each_tweet_id,))

  tmp_info = concur.fetchone()

  tmp_image_id = tmp_info[0]
  tmp_tweet = tmp_info[1]
  tmp_image_data = tmp_info[2]

  image_dic[tmp_image_id] = {"tweet":tmp_tweet, "keyword":[]}

  for each_keyword in sorted(top_res, key=lambda x: x[1], reverse=True):
    image_dic[tmp_image_id]["keyword"].append((each_keyword[0], each_keyword[1]))

  file_path = "./image/{0}.jpg".format(tmp_image_id)
  if not os.path.isfile(file_path):
    f = open(file_path, 'bw')
    f.write(tmp_image_data)
    f.close()
  
# 結果表示用ページの作成
f = open('template.html', 'r')
tmp_str = f.read()
f.close()

emb_str = ""
for image_id, values in image_dic.items():
  words = ""
  for each_word in values["keyword"]:
    words += "{0}({1})  ".format(each_word[0], round(each_word[1], 3))
  
  emb_str += """
  <br />
  {0}<br />
  <img src="./image/{0}.jpg"><br />
  <ul>
    <li>
      {1}
    </li>
    <li>
      {2}
    </li>
  </ul>
  <br />
  <br />""".format(image_id, values["tweet"], words)

result_str = tmp_str.format(emb_str)
result_filename = str(TOPIC_ID) + ".html"

f = open(result_filename, 'w')
f.write(result_str)
f.close()

concur.close()
con.close()


