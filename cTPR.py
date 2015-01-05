import psycopg2
import MeCab
import re
import os
import parse_proc
import copy

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
    
    parser = parse_proc.Parser()
    
    for tweet in tweet_list:
      parser.parse(tweet)
      
      tmp_word_list = copy.deepcopy(parser.parsed_list)
      
      # 定められたwindow_sizeを用いてグラフを作成
      for begin_pos in range(len(tmp_word_list)):
        if tmp_word_list[begin_pos] is not -1:
          pos_of_window = 1
          begin_word = tmp_word_list[begin_pos]
          for end_pos in range(begin_pos + 1, len(tmp_word_list)):
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
      self.score_dic[each_word] = 1 / vertex_size
    
    sum_dic = {}
    sum_prob = 0
    for target_word in self.graph_dic.keys():
      #cursor.execute('select count, topic_id from word_count where word=%s', (target_word,))
      cursor.execute('''select a.count, b.topic_id from preprocess as a, text_with_label as b
        where a.tweet_id=b.tweet_id and a.word=%s''', (target_word,))
      res = cursor.fetchall()
      
      all_count = 0
      topic_count = 0
      for each in res:
        all_count += each[0]
        
        if each[1] is self.topic_id:
          topic_count += each[0]
        
        assert topic_count <= all_count
      
      sum_dic[target_word] = topic_count / all_count
      sum_prob += topic_count / all_count
    
    for k in sum_dic.keys():
      sum_dic[k] = sum_dic[k] / sum_prob
    
    for i in range(self.iteration):
      #print("{0}/{1}\r".format(i + 1, self.iteration), end="")
      
      converge_flag = True
      tmp_score_dic = {}
      for target_word in self.graph_dic.keys():
        score_sum = 0
        for counter_word, value in self.graph_dic.items():
          if target_word in value.keys():
            weight_sum = 0
            for weight in value.values():
              weight_sum += weight
            
            score_sum += (self.graph_dic[counter_word][target_word] / weight_sum) * \
              self.score_dic[counter_word]
        
        tmp_score = 0
        try:
          tmp_score = self.damping_factor * score_sum + (1 - self.damping_factor) * sum_dic[target_word]
        except:
          f = open("error_terms.txt", "a")
          f.write(target_word+"\n")
          f.close()
        
        if abs(tmp_score - self.score_dic[target_word]) > 0.001:
          converge_flag = False
        
        tmp_score_dic[target_word] = tmp_score
      
      if converge_flag:
        #print("the score of each vertex converged.", end="")
        break
      else:
        self.score_dic = tmp_score_dic
    
    #f = open("{0}.csv".format(self.topic_id), 'w')
    #emb_str = ""
    #count = 0
    #for k, v in sorted(self.score_dic.items(), key=lambda x: x[1], reverse=True):
    #  emb_str += "{0},{1}\n".format(k, v)
    #  count += 1
    #  if count >= 100:
    #    break
    
    #f.write(emb_str)
    #f.close()
    
    #print("")


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
    # 探索することで検出する
    
    #if len(surface) <= 1:
    #  return False
    
    if '名詞' in feature:
      #if 'サ変接続' in feature:
      #  return False
      #
      #if '名詞,固有名詞,組織,*,*,*,*' in feature:
      #  return False
      #
      if '数' in feature:
        return False
      #
      #if '形容動詞' in feature:
      #  return False
      #
      #if '副詞' in feature:
      #  return False
      #
      #if '接尾' in feature:
      #  return False
      #
      #if '接頭' in feature:
      #  return False
      
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


  



