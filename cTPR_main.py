import psycopg2
import cTPR
import os, sys

TOPIC_ID = 7
WINDOW_SIZE = 4
DAMPING_FACTOR = 0.3
ITERATION = 5
TOP_M = 10
IMAGE_LIMIT = 30
DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
concur = con.cursor()

concur.execute('select tweet_id from text_with_label where topic_id = %s', (TOPIC_ID,))
tweet_id_list = []
for each_id in concur:
	tweet_id_list.append(each_id[0])

tweet_list = []
print("fetching tweets.")
for each_id in tweet_id_list:
	concur.execute('select tweet from twipple where tweet_id=%s limit 1', (each_id,))
	tweet_list.append(concur.fetchone()[0])
print("done.")

# cTPRクラスのmake_graphメソッドを活用してワードグラフを作成する
cTPR_components = cTPR.cTPR(TOPIC_ID, WINDOW_SIZE, DAMPING_FACTOR, ITERATION, DBPATH)

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
for each_id in tweet_id_list[:IMAGE_LIMIT]:
	concur.execute("select id, tweet, image from twipple where tweet_id = %s limit 1", (each_id,))
	tmp_info = concur.fetchone()
	tmp_image_id = tmp_info[0]
	tmp_tweet = tmp_info[1]
	tmp_image_data = tmp_info[2]

	image_dic[tmp_image_id] = {"tweet":"", "keyword":[]}

	for each_keyword in sorted(top_res, key=lambda x: x[1], reverse=True):
		image_dic[tmp_image_id]["keyword"].append((each_keyword[0], each_keyword[1]))

	image_dic[tmp_image_id]["tweet"] = tmp_tweet

	file_path = "./image/{0}.jpg".format(tmp_image_id)
	if not os.path.isfile(file_path):
		f = open(file_path, 'bw')
		f.write(tmp_image_data)
		f.close()
	
# 結果表示用htmlのテンプレートを読み込み
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




