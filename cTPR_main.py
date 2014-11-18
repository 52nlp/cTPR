import psycopg2
import cTPR
import os, sys

TOPIC_ID = 11 #アノテーションの対象となるトピックを指定
WINDOW_SIZE = 2 #ワードグラフを作成する際に使うウィンドウのサイズを指定
DAMPING_FACTOR = 0.1 #cTPRの計算式で使うdamping factor（他トピックからのジャンブ率）を指定
ITERATION = 100 #cTPRアルゴリズムのイテレーション数を指定
TOP_M = 20 #最終的にアノテーションに使うキーワードの数を指定
IMAGE_LIMIT = 30 #結果として使う画像の枚数を指定
DBPATH = "dbname=image_tagging host=localhost user=postgres" #計算に使うデータを格納しているDBを指定

con = psycopg2.connect(DBPATH)
concur = con.cursor()

print("fetching tweets.")

concur.execute('''select b.tweet from text_with_label as a, twipple as b where  
	a.tweet_id = b.tweet_id and a.topic_id = %s''', (TOPIC_ID,))

tweet_list = []
for each_tweet in concur:
	tweet_list.append(each_tweet[0])

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
concur.execute("""select user_id from topic_distribution_on_users where topic_id=%s 
		order by distribution desc limit 3""", (TOPIC_ID,))
result = concur.fetchall()
tweet_id_list = []
image_dic = {}
for each_id in list(map(lambda x: x[0], result)):
	concur.execute("""select distinct on (b.tweet) b.id, b.tweet, b.image 
			from text_with_label as a, twipple as b
			where a.tweet_id=b.tweet_id and a.user_id=b.user_id and b.user_id=%s and 
			a.topic_id=%s""", (each_id, TOPIC_ID))

	for tmp_info in concur:
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
	<li><img src="./image/{0}.jpg">
	<ul>
		<li>
			{1}
		</li>
		<li>
			{2}
		</li>
	</ul>
	</li>
	<br />
	<br />""".format(image_id, values["tweet"], words)

result_str = tmp_str.format(emb_str)
result_filename = str(TOPIC_ID) + ".html"

f = open(result_filename, 'w')
f.write(result_str)
f.close()

concur.close()
con.close()




