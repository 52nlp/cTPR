import psycopg2
import MeCab
import cTPR
import re

DBPATH = "dbname=image_tagging host=localhost user=postgres"

con = psycopg2.connect(DBPATH)
cursor = con.cursor()

cursor.execute('select topic_id from text_with_label group by topic_id order by topic_id')
res = cursor.fetchall()

tagger = MeCab.Tagger('')

for each_topic_id in res:
	word_count = {}

	cursor.execute('select distinct on (b.tweet_id) b.tweet from text_with_label as a, ' + \
			'twipple as b where a.tweet_id=b.tweet_id and a.topic_id=%s', (each_topic_id[0],))
	tweets = cursor.fetchall()
	for each_tweet in tweets:
		tweet = each_tweet[0]
		
		node = tagger.parseToNode(tweet)
		while node:
			try:
				if cTPR.cTPR.detect_noise(node.feature):
					if not node.surface in word_count.keys():
						word_count[node.surface] = 1
					else:
						word_count[node.surface] += 1
			
			except:
				print(tweet)
					
			node = node.next
		
	for k, v in word_count.items():
		cursor.execute('insert into word_count (topic_id, word, count) values (%s, %s, %s)',
				(each_topic_id[0], k, v))
	
	con.commit()

cursor.close()
con.close()




