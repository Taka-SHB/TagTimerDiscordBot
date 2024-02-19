# TagTimerDiscordBot

A timer that can record the measurement time for each tag. Also has simple analysis functions

## このボットで主に出来ること

- タグを設定して時間の計測を行うことで，その計測時間などを記録出来る
- 記録に対してキャプションを残すことが出来る
- タグごとに，記録されている総時間や日ごとの合計時間を出力できる
- 記録されている情報をCSV形式で出力できる
- 記録されている情報からグラフを作成し出力できる

## 使い方

`main.py`と同じディレクトリに，botのトークンが一行目に書き込まれた`token.txt`を用意してください．`main.py`の`db_name`を適宜変更し，
```
python main.py
```
を実行するとbotが起動します．

## 機能一覧

現在ボットに実装されているコマンドは以下のとおりです．

- [$timer](#timer)：時間の計測を行い，記録する
- [$tag](#tag)：登録されているタグの一覧を表示する
- [$set_tag](#set_tag)：記録や分析を行うタグを設定する
- [$add_tag](#add_tag)：タグを追加する
- [$del_tag](#del_tag)：タグを削除する
- [$merge_tag](#merge_tag)：2つのタグを統合する
- [$rename_tag](#rename_tag)：タグの名称を変更する
- [$report](#report)：設定されているタグの総時間や日ごとの合計時間を出力する
- [$report_all](#report_all)：タグごとの総時間を出力する
- [$csv](#csv)：設定されているタグに記録されている情報をCSVファイルで出力する
- [$csv_all](#csv_all)：記録されている全ての情報をCSVファイルで出力する
- [$plot](#plot)：設定されているタグの計測記録をグラフにして画像で出力する
- [$delete_record](#delete_record)：記録されている情報を削除する
- [$fix_record](#fix_record)：記録されている情報を編集する

### $timer
```
$timer
```
時間計測を開始するためのボタンを送信します．
計測を開始後，終了用のボタンを送信します．
計測を終了すると，計測時間を送信するとともに，キャプションを追加するためのボタンを送信します．

キャプション追加のボタンは，キャプションを追加するか，新たなコマンドを入力することで無効化されます．

**注：時間計測中は全てのコマンドが無効化されます**

### $tag
```
$tag
```
現在設定されているタグとタグの一覧が送信されます．

ここで表示されるタグ番号は`$set_tag`や`$del_tag`等のコマンドで必要になります．

### $set_tag
```
$set_tag [タグ番号]
```
記録や分析を行うタグを，タグ番号で指定したタグに設定します．

### $add_tag
```
$add_tag
```
タグを追加するためのボタンを送信します．ボタン押下で開かれるモーダルに新しいタグの名称を入力します．

ボタンは，タグを追加するか新しいコマンドを入力することで無効化されます．

### $del_tag
```
$del_tag [タグ番号]
```
タグ番号で指定したタグとそのタグに記録されている情報を全て削除します．削除するには，コマンド入力後に送信されるボタンを押してください．

ボタンは，タグを削除するか，新しいコマンドを入力することで無効化されます．

### $merge_tag
```
$merge_tag [タグ番号1] [タグ番号2]
```
タグ番号1のタグにタグ番号2のタグに記録されている情報を全て統合します．最終的にはタグ番号1のタグが残り，タグ番号2のタグは削除されます．統合するには，コマンド入力後に送信されるボタンを押してください．

ボタンは，タグを統合するか，新しいコマンドを入力することで無効化されます．

### $rename_tag
```
$rename_tag [タグ番号]
```
タグ番号で指定したタグの名称を変更するためのボタンを送信します．ボタン押下で開かれるモーダルに新しいタグの名称を入力します．

ボタンは，タグの名称を変更するか，新しいコマンドを入力することで無効化されます．

### $report
```
$report [日付](任意)
```
現在設定されているタグの記録時間の総計や日ごとの合計時間を送信します．

日付を入力しなかった場合，記録時間の総計と日ごとの合計時間を最新から5件前まで送信します．

日付を入力した場合，記録時間の総計は送信されず，日付以降の日ごとの合計時間を最大10件送信します．

日付は`2024_1_1`という形式で入力してください．

### $report_all
```
$report_all [日付1](任意) [日付2](任意)
```
タグごとの記録されている総時間や任意の期間での合計時間を送信します．

日付1を設定しなかった場合，全期間での総時間をタグごとに計上し送信します．

日付1を設定し日付2を設定しなかった場合，日付1以降での合計時間をタグごとに計上し送信します．

日付1と日付2をともに設定した場合，日付1から日付2までの期間の合計時間をタグごとに計上し送信します．

日付は`2024_1_1`という形式で入力してください．

### $csv
```
$csv
```
現在設定されているタグに記録されている情報をCSVファイルにして送信します．

### $csv_all
```
$csv_all
```
タグに関係なく，記録されている全ての情報をCSVファイルにして送信します．

### $plot
```
$plot [日付1](任意) [日付2](任意)
```
現在設定されているタグの全期間または任意の期間での計測時間の推移をグラフにして画像ファイルを送信します．

日付1を設定しなかった場合，全期間でのグラフを送信します．

日付1を設定し日付2を設定しなかった場合，日付1以降の期間でのグラフを送信します．

日付1と日付2をともに設定した場合，日付1から日付2までの期間でのグラフを送信します．

日付は`2024_1_1`という形式で入力してください．

### $delete_record
```
$delete_record [日時]
```
現在設定されているタグの日時での記録を削除します．削除するには，コマンド入力後に送信されるボタンを押してください．

日時は`2024_1_1 00:00:00`という形式で，`$csv`で得られるファイルの`start_date`に相当します．

ボタンは，記録を削除するか，新しいコマンドを入力することで無効化されます．

### $fix_record
```
$fix_record [日時]
```
現在設定されているタグの日時での記録を編集するためのボタンを送信します．ボタン押下で開かれるモーダルから編集を行えます．

日時は`2024_1_1 00:00:00`という形式で，`$csv`で得られるファイルの`start_date`に相当します．

ボタンは，記録を編集するか，新しいコマンドを入力することで無効化されます．
