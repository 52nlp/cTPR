import psycopg2
import MeCab
import re

class cTPR:
	def __init__(self, topic_id, window_size, damping_factor, iteration, dbpath):
		self.topic_id = topic_id
		self.window_size = window_size
		self.damping_factor = damping_factor
		self.iteration = iteration
		self.dbpath = dbpath
		self.graph_dic = {}
		self.score_dic = {}


	def make_word_graph(self, tweet_list):
		# 渡されたtweetのリストから指定された
		# ウィンドウサイズを用いてワードグラフを作成する．
		# 戻り値はグラフの構造が示された辞書．
		
		tagger = MeCab.Tagger('')
		
		for tweet in tweet_list:
			tmp_word_list = []
			
			node = tagger.parseToNode(tweet)
			# tweetをトークナイズ
			# ノイズ語は-1と表現し，それ以外はnode.surfaceを格納
			while node:
				if node.surface is not '' and self.detect_noise(node.feature):
					tmp_word_list.append(node.surface)
				else:
					tmp_word_list.append(-1)
				
				node = node.next
			
			# 定められたwindow_sizeを用いてグラフを作成
			for begin_pos in range(len(tmp_word_list)):
				if tmp_word_list[begin_pos] is not -1:
					pos_of_window = 1
					begin_word = tmp_word_list[begin_pos]
					for end_pos in range(begin_pos+1, len(tmp_word_list)):
						if tmp_word_list[end_pos] is not -1:
							# keyが始点となる単語，valueが終点となる単語をkeyに，valueに共起頻度を持つ
							end_word = tmp_word_list[end_pos]
							if not begin_word in self.graph_dic.keys():
								self.graph_dic[begin_word] = {}
							
							if end_word in self.graph_dic[begin_word].keys():
								self.graph_dic[begin_word][end_word] += 1
							else:
								self.graph_dic[begin_word][end_word] = 1
						
						pos_of_window += 1
						if pos_of_window >= self.window_size:
							break


	def run_pagerank(self):
		# PageRankアルゴリズムを走らせ，スコアの降順にソートされた
		# キーワードのリストを返す．
		
		con = psycopg2.connect(self.dbpath)
		cursor = con.cursor()
		
		vertex_size = self.get_vertex_size()
		word_list = self.get_word_list()
		
		for each_word in word_list:
			self.score_dic[each_word] = 1/vertex_size
		
		for i in range(self.iteration):
			print("{0}/{1}\r".format(i+1, self.iteration), end="")
			for target_word in self.graph_dic.keys():
				cursor.execute('select count, topic_id from word_count where word=%s', (target_word,))
				res = cursor.fetchall()
				
				all_count = 0
				topic_count = 0
				for each in res:
					all_count += each[0]
					
					if each[1] is self.topic_id:
						topic_count += each[0]
				
				score_sum = 0
				for counter_word, value in self.graph_dic.items():
					if target_word in value.keys():
						weight_sum = 0
						for weight in value.values():
							weight_sum += weight
						
						score_sum += (self.graph_dic[counter_word][target_word] / weight_sum) * \
							self.score_dic[counter_word]
						
				self.score_dic[target_word] = self.damping_factor * score_sum + \
					(1 - self.damping_factor) * (topic_count / all_count)
		
		print("")
		
		
	def get_top_m(self, m):
		# トップM個の単語を割り出して返す
		
		topM = []
		
		count = 0
		for k, v in sorted(self.score_dic.items(), key=lambda x: x[1], reverse=True):
			topM.append((k, v))
			
			count += 1
			if count >= m:
				break
		
		return topM


	@staticmethod
	def detect_noise(feature):
		# ノイズと思われる単語を除去する．
		# MeCabによりParseした結果であるfeatureを
		# 探索することで検出する．
		
		if '名詞' in feature:
			if 'サ変接続' in feature:
				return False
			
			if '名詞,固有名詞,組織,*,*,*,*' in feature:
				return False
			
			if '数' in feature:
				return False
			
			if '形容動詞' in feature:
				return False
			
			if '副詞' in feature:
				return False

			if '接尾' in feature:
				return False

			if '接頭' in feature:
				return False
			
			return True
		
		return False


	def get_vertex_size(self):
		word_list = []
		for begin_word, value in self.graph_dic.items():
			if not begin_word in word_list:
				word_list.append(begin_word)
			
			for end_word in value.keys():
				if not end_word in word_list:
					word_list.append(end_word)
		
		return len(word_list)


	def get_word_list(self):
		word_list = []
		for begin_word, value in self.graph_dic.items():
			if not begin_word in word_list:
				word_list.append(begin_word)
			
			for end_word in value.keys():
				if not end_word in word_list:
					word_list.append(end_word)
		
		return word_list


	
		




