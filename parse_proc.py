import os
import re
import cTPR

class Parser():
  def __init__(self, fileName="tweet.txt"):
    self.fileName = fileName
    self.parsed_list = [] 
    self.count_dic = {}
    self.raw_list = []


  def parse(self, tweet):
    self.parsed_list = []
    self.count_dic = {}
    self.raw_list = []
    
    filtered_tweet = self.filter_tweet(tweet)
    
    f = open(self.fileName, 'w')
    f.write(filtered_tweet)
    f.close()
    
    cmd = 'mecab ' + self.fileName
    proc = os.popen(cmd)
    result = proc.read()
    proc.close()
    
    result = re.sub(r'\n', '\t', result)
    
    taggered_list = result.split('\t')
    
    for i in range(len(taggered_list))[1::2]:
      if i is len(taggered_list)-1:
        break
      
      surface = taggered_list[i-1]
      feature = taggered_list[i]
      
      self.raw_list.append(surface)
      
      if cTPR.cTPR.detect_noise(surface, feature):
        if not surface in self.count_dic.keys():
          self.parsed_list.append(surface)
          self.count_dic[surface] = 1
        else:
          self.count_dic[surface] += 1


  @staticmethod
  def filter_tweet(tweet):
    # RT、ハッシュタグ記号の除去
    tweet = re.sub(r'RT|rt|#', '', tweet)
    
    # URL除去
    tweet = re.sub(r"http[s]*://[a-zA-Z0-9./-_!*'();%s:@&=+$,%]+", '', tweet)
    
    # 顔文字除去
    match_tweet    = '[0-9A-Za-zぁ-ヶ一-龠]'
    non_tweet      = '[^0-9A-Za-zぁ-ヶ一-龠]'
    allow_tweet    = '[ovっつ゜ニノ三二]'
    hw_kana       = '[ｦ-ﾟ]'
    open_branket  = '[\(∩（]'
    close_branket = '[\)∩）]'
    arround_face  = '(%s:' + non_tweet + '|' + allow_tweet + ')*'
    face          = '(%s!(%s:' + match_tweet + '|' + hw_kana + '){3,}).{3,}'
    face_char     = arround_face + open_branket + face + close_branket + arround_face
    
    tweet = re.sub(r"%s" % face_char, '', tweet)
    
    # カッコ記号を除去
    tweet = re.sub(r"[()\[\]]", '', tweet)
    
    # 笑い記号"w"の除去
    tweet = re.sub(r"[wWｗW]{2,}", '', tweet)
    
    # 意味のわからない数字の羅列を除去(6桁-8桁のもの)
    tweet = re.sub(r"[0-9]{6,7}", '', tweet)
    
    return tweet
