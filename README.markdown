#必要な環境
+ Python3系
+ Python3系の追加パッケージ
 - psycopg2(PostgreSQLをPython3系から使うため)
+ PostgreSQL
+ Javaの実行環境(JRE7)
+ MeCab
+ Unix環境

#実験手順（上から下に実行）
+ prepreprocess.pyにより実験対象とする期限の限定と各tweetのフィルタリング（8 tweet以上しているユーザのtweetでなおかつ条件に合った単語が3つ以上含まれているtweet）を行う
```
$ python3.3 prepreprocess.py
```
+ preprocess.pyにより10 tweet以上に現れない単語，あるいは70%以上のtweetに現れる単語を除去する
```
$ python3.3 preprocess.py
```
+ 以下の作業をトピック数30，100，200，500のそれぞれについて行う
 - Twitter-LDAによりトピックを抽出(1)
 - 抽出結果が別のトピック設定で上書きされるため，計算結果をトピックごとに別テーブルに保存(2)
 - キーワードを抽出して画像へアノテーション(各トピックごとに計算）(3)
```
# (1)
# EclipseからTwitterLDAmainを実行した後，以下のコマンドを実行
# (2)
$ psql -q -c 'create table text_with_label<topic number> as select * from text_with_label' image_tagging
$ psql -q -c 'create table exp_lda<topic number> as select * from exp_lda' image_tagging
# (3)
$ python3.3 extract_exp_lda_images.py
```
 - 抽出結果を別テーブルに保存
+ 各トピックごとにアノテーションした画像集合の重なり部分を抽出する
```
$ python3.3 select_tweet_for_exp.py
```
+ 抽出した重なり部分から全名詞数が一定数以下のtweetをM個取り出す
```
$ python3.3 limit_tweet_for_exp.py
```

##評価手順（上から下に実行）
+ evaluate_resultsテーブルから多数決をとることで正解データを作成してテーブルに保存
```
$ python3.3 make_answer.py
```
+ 提案手法がアノテーションした各単語の◯，×を確かめる
 - <topic number>にはトピック数を入力（30，100，200，500のどれか）
```
$ python3.3 calc_final_result.py <topic number>
```
+ 元データの各画像がもつノイズ数の分布を算出
```
$ python3.3 make_histgram.py
```
+ 正解データについて，全ての名詞をそのままアノテーションしたときの以下のデータを計算する(calc_naive_result.pyを利用)
 - アノテーション精度
 - ノイズ除去精度
 - 正解データを含む画像の割合
```
$ python3.3 calc_naive_result.py
```
+ 名詞をそのままアノテーションしたときのカバー率を計算する
 - 100%（名詞がついてるものしかデータセットに用いていないため）


