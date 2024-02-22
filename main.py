import discord
from discord.ext import commands

from utils.Timer import Timer, StartButton, StopButton
from utils.TagManager import TagManager, AddTag, DeleteTag, MergeTag, RenameTag,load_tag_dict_from_db
from utils.Analyzer import Analyzer
from utils.RecordFixer import RecordFixer, DeleteRecord, FixRecord
import utils.CheckDB

import datetime

intents = discord.Intents.default()
intents.message_content = True

with open("token.txt", "r") as f:
    token = f.readline()

db_name = "DEMODB"
utils.CheckDB.check(db_name)
Timer.DB_NAME = TagManager.DB_NAME = Analyzer.DB_NAME = RecordFixer.DB_NANE = db_name

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    TagManager.TAG_DICT = load_tag_dict_from_db()
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$'):
        
        if Timer.IS_RUNNING and (not message.content.startswith('$stop')):
            await message.channel.send("申し訳ありません！　時間計測中はコマンドの入力を受け付けられません．\n計測は以下のボタンから終了できます．")
            await message.channel.send(view = StopButton())
            return
        reset_flag()
        await bot.process_commands(message)
        return

    c = message.content
    await message.channel.send('{}...ですか？'.format(c))

@bot.command()
async def timer(ctx):
    if TagManager.CURRENT_ID == "":
        await ctx.send("現在のタグは選択されていません．\nこの状態では計測時間が記録されません．\nそれでも良ければボタンを押してください．".format(TagManager.CURRENT_ID))
    else:
        await ctx.send("現在のタグは【{}】です．\n準備が完了したらボタンを押してください．".format(TagManager.TAG_DICT[TagManager.CURRENT_ID]))
    Timer.CURRENT_ID = TagManager.CURRENT_ID
    await ctx.send(view = StartButton())

@bot.command()
async def stop(ctx):
    if Timer.IS_RUNNING:
        await ctx.send("計測を終了するには以下のボタンを押してください．")
        await ctx.send(view = StopButton())
    else :
        await ctx.send("現在は計測していないようですね...")

@bot.command()
async def tag(ctx):
    if TagManager.TAG_DICT == {}:
       await ctx.send("タグはまだ何一つ登録されていません．\n$add_tagで新しいタグを登録しましょう！") 
       return
    elif TagManager.CURRENT_ID == "":
        await ctx.send("現在のタグは選択されていません．")
    else:
        await ctx.send("現在のタグは【{}】です．".format(TagManager.TAG_DICT[TagManager.CURRENT_ID]))

    res = "タグは以下から選択できます！\n"
    for i, t in enumerate(TagManager.TAG_DICT.values()):
        if len(t) > 30:
            t = t[:27] + "..."
        res += "{:>3}: {}\n".format(i+1, t)
    await ctx.send(res)

@bot.command()
async def set_tag(ctx, s):
    try:
        s = int(s)
    except:
        await ctx.send("タグは番号で指定してください！\n$tagを使えば，タグの番号を知ることができます．")
        return
    if 0 < s <= len(TagManager.TAG_DICT):
        TagManager.CURRENT_ID = list(TagManager.TAG_DICT.keys())[s-1]
        await ctx.send("タグを【{}】に設定しました．".format(TagManager.TAG_DICT[TagManager.CURRENT_ID]))
    else:
        await ctx.send("タグは1～{}までの整数で指定してください！\n$tagを使えば，タグの番号を知ることができます．".format(len(TagManager.TAG_DICT)))
@set_tag.error
async def info_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("$set_tagには設定するタグの番号が必要です！\nタグ番号が分かりませんか？　$tagで知ることが出来ます！")

@bot.command()
async def add_tag(ctx):
    await ctx.send("新しいタグを追加しますか？　下のボタンからお願いします！")
    await ctx.send(view = AddTag())

@bot.command()
async def del_tag(ctx, s):
    try:
        s = int(s)
    except:
        await ctx.send("タグは番号で指定してください！\n$tagを使えば，タグの番号を知ることができます．")
        return
    if 0 < s <= len(TagManager.TAG_DICT):
        del_id = list(TagManager.TAG_DICT.keys())[s-1]
        await ctx.send("タグ【{}】と計測記録を全て削除しますか？\n一度消えたタグはもとに戻すことが出来ません！".format(TagManager.TAG_DICT[del_id]))
        TagManager.DELETE_CONFIRM = True
        await ctx.send(view = DeleteTag(del_id))
    else:
        await ctx.send("タグは1～{}までの整数で指定してください！\n$tagを使えば，タグの番号を知ることができます．".format(len(TagManager.TAG_DICT)))
@del_tag.error
async def info_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("$del_tagには削除するタグの番号が必要です！\nタグ番号が分かりませんか？　$tagで知ることが出来ます！")

@bot.command()
async def merge_tag(ctx, s1, s2):
    try:
        s1 = int(s1)
        s2 = int(s2)
    except:
        await ctx.send("タグは番号で指定してください！\n$tagを使えば，タグの番号を知ることができます．")
        return
    if 0 < s1 <= len(TagManager.TAG_DICT) and 0 < s2 <= len(TagManager.TAG_DICT):
        base_id = list(TagManager.TAG_DICT.keys())[s1-1]
        minor_id = list(TagManager.TAG_DICT.keys())[s2-1]
        await ctx.send("タグ【{}】にタグ【{}】を併合しますか？\n併合されるタグは，もとに戻すことが出来ません！".format(
            TagManager.TAG_DICT[base_id], TagManager.TAG_DICT[minor_id]))
        TagManager.MERGE_CONFIRM = True
        await ctx.send(view = MergeTag(base_id, minor_id))
    else:
        await ctx.send("タグは1～{}までの整数で指定してください！\n$tagを使えば，タグの番号を知ることができます．".format(len(TagManager.TAG_DICT)))
@merge_tag.error
async def info_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("$merge_tagには併合先のタグ番号と併合元のタグ番号が必要です！\nタグ番号が分かりませんか？　$tagで知ることが出来ます！")

@bot.command()
async def rename_tag(ctx, s):
    try:
        s = int(s)
    except:
        await ctx.send("タグは番号で指定してください！\n$tagを使えば，タグの番号を知ることができます．")
        return
    if 0 < s <= len(TagManager.TAG_DICT):
        tag_id = list(TagManager.TAG_DICT.keys())[s-1]
        await ctx.send("タグ【{}】の名称を変更するには下のボタンを押してください．".format(TagManager.TAG_DICT[tag_id]))
        TagManager.RENAME_CONFIRM = True
        await ctx.send(view = RenameTag(tag_id))
@rename_tag.error
async def info_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("$rename_tagには名称を変更するタグの番号が必要です！\nタグ番号が分かりませんか？　$tagで知ることが出来ます！")

@bot.command()
async def report(ctx, *args):
    if TagManager.CURRENT_ID == "":
        await ctx.send("タグが設定されていません！\n$set_tagで設定できます．")
        return
    try:
        start_date = args[0]
        start_date = datetime.datetime.strptime(start_date, "%Y_%m_%d")
    except:
        start_date = None
    res = ""
    
    if start_date is None:
        total = Analyzer.total_tag_time(TagManager.CURRENT_ID)
        m, s = divmod(total, 60)
        h, m = divmod(m, 60)

        res += "【{}】に費やした総時間は{}時間{}分{}秒です！\n".format(
            TagManager.TAG_DICT[TagManager.CURRENT_ID], h, m, s)
        res += "最近の計測はこんな感じです．\n"
    else:
        res += "{}年{}月{}日以降の計測はこんな感じです．\n".format(
            start_date.year, start_date.month, start_date.day)
        
    time_data = Analyzer.tag_time_per_day(TagManager.CURRENT_ID)
    sidx = -5 if start_date is None else 0
    i = 0
    for row in time_data[sidx:]:
        if i >= 10:
            break
        dt = datetime.datetime.strptime(row[0], "%Y_%m_%d")
        if not start_date is None:
            if dt < start_date:
                continue
        total = row[1]
        m, s = divmod(total, 60)
        h, m = divmod(m, 60)
        res += "{:4}年{:2}月{:2}日: {}時間{}分{}秒\n".format(
            dt.year, dt.month, dt.day, h, m, s)
        i += 1

    await ctx.send(res)

@bot.command()
async def report_all(ctx, *args):
    try:
        start_date = args[0]
        start_date = datetime.datetime.strptime(start_date, "%Y_%m_%d")
    except:
        start_date = None
    try:
        end_date = args[1]
        end_date = datetime.datetime.strptime(end_date, "%Y_%m_%d")
    except:
        end_date = None
    res = ""
    if start_date is None:
        res += "各タグの計測総時間はこんな感じです！\n"
    elif end_date is None:
        res += "{}年{}月{}日以降の各タグの計測総時間はこんな感じです！\n".format(
            start_date.year, start_date.month, start_date.day)
    else:
        res += "{}年{}月{}日から{}年{}月{}日までの各タグの計測総時間はこんな感じです！\n".format(
            start_date.year, start_date.month, start_date.day, end_date.year, end_date.month, end_date.day)
        
    time_data = Analyzer.total_time_per_tag(start_date, end_date)
    for tag_id, total in time_data:
        m, s = divmod(total, 60)
        h, m = divmod(m, 60)
        res += "【{}】: {}時間{}分{}秒\n".format(
            TagManager.TAG_DICT[tag_id], h, m, s)
    await ctx.send(res)

@bot.command()
async def csv(ctx):
    if TagManager.CURRENT_ID == "":
        await ctx.send("タグが設定されていません！\n$set_tagで設定できます．")
        return
    stream = Analyzer.stream_csv_tag(TagManager.CURRENT_ID)
    await ctx.send(content = "【{}】の計測記録のCSVファイルをどうぞ！".format(TagManager.TAG_DICT[TagManager.CURRENT_ID]),
                   file = discord.File(stream, filename="output.csv"))

@bot.command()
async def csv_all(ctx):
    stream = Analyzer.stream_csv_all()
    await ctx.send(content = "全ての計測記録のCSVファイルをどうぞ！",
                   file = discord.File(stream, filename="output.csv"))
    
@bot.command()
async def plot(ctx, *args):
    if TagManager.CURRENT_ID == "":
        await ctx.send("タグが設定されていません！\n$set_tagで設定できます．")
        return
    try:
        start_date = args[0]
        start_date = datetime.datetime.strptime(start_date, "%Y_%m_%d")
    except:
        start_date = None
    try:
        end_date = args[1]
        end_date = datetime.datetime.strptime(end_date, "%Y_%m_%d")
    except:
        end_date = None

    res = ""
    if start_date is None:
        res += "【{}】に費やした時間をグラフにするとこんな感じです！\n".format(TagManager.TAG_DICT[TagManager.CURRENT_ID])
    elif end_date is None:
        res += "{}年{}月{}日以降で【{}】に費やした時間をグラフにするとこんな感じです！\n".format(
            start_date.year, start_date.month, start_date.day, TagManager.TAG_DICT[TagManager.CURRENT_ID])
    else:
        res += "{}年{}月{}日から{}年{}月{}日までで【{}】に費やした時間をグラフにするとこんな感じです！\n".format(
            start_date.year, start_date.month, start_date.day, end_date.year, end_date.month, end_date.day, TagManager.TAG_DICT[TagManager.CURRENT_ID])
        
    stream = Analyzer.stream_plot_tag_record(TagManager.CURRENT_ID, start_date, end_date)
    await ctx.send(content = res,
                   file = discord.File(stream, filename="figure.png"))
    
@bot.command()
async def delete_record(ctx, dt, *args):
    if TagManager.CURRENT_ID == "":
        await ctx.send("タグが設定されていません！\n$set_tagで設定できます．")
        return
    try:
        del_dt = datetime.datetime.strptime(dt, "%Y_%m_%d %H:%M:%S")
    except:
        try:
            dt = "{} {}".format(dt, args[0])
            del_dt = datetime.datetime.strptime(dt, "%Y_%m_%d %H:%M:%S")
        except:
            await ctx.send("日時は\"%Y_%m_%d %H:%M:%S\"の形式で入力してください！")
            return
    if not RecordFixer.exists_record(TagManager.CURRENT_ID, del_dt):
        await ctx.send("【{}】には{}の記録が存在しません！".format(
            TagManager.TAG_DICT[TagManager.CURRENT_ID], del_dt.strftime("%Y_%m_%d %H:%M:%S")))
        return
    await ctx.send("【{}】{}の記録を削除するには下のボタンを押して下さい．".format(
        TagManager.TAG_DICT[TagManager.CURRENT_ID], del_dt.strftime("%Y_%m_%d %H:%M:%S")))
    RecordFixer.DELETE_ROCORD_CONFIRM = True
    await ctx.send(view=DeleteRecord(TagManager.CURRENT_ID, del_dt))
@delete_record.error
async def info_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("$delete_recordには削除する記録が持つ日時の指定が必要です．\nこれは$csvなどから得ることが出来ます．")

@bot.command()
async def fix_record(ctx, dt, *args):
    if TagManager.CURRENT_ID == "":
        await ctx.send("タグが設定されていません！\n$set_tagで設定できます．")
        return
    try:
        fix_dt = datetime.datetime.strptime(dt, "%Y_%m_%d %H:%M:%S")
    except:
        try:
            dt = "{} {}".format(dt, args[0])
            fix_dt = datetime.datetime.strptime(dt, "%Y_%m_%d %H:%M:%S")
        except:
            await ctx.send("日時は\"%Y_%m_%d %H:%M:%S\"の形式で入力してください！")
            return
    if not RecordFixer.exists_record(TagManager.CURRENT_ID, fix_dt):
        await ctx.send("【{}】には{}の記録が存在しません！".format(
            TagManager.TAG_DICT[TagManager.CURRENT_ID], fix_dt.strftime("%Y_%m_%d %H:%M:%S")))
        return
    await ctx.send("【{}】{}の記録を編集するには下のボタンを押して下さい．".format(
        TagManager.TAG_DICT[TagManager.CURRENT_ID], fix_dt.strftime("%Y_%m_%d %H:%M:%S")))
    RecordFixer.FIX_ROCORD_CONFIRM = True
    await ctx.send(view=FixRecord(TagManager.CURRENT_ID, fix_dt))
@fix_record.error
async def info_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("$fix_recordには編集する記録が持つ日時の指定が必要です．\nこれは$csvなどから得ることが出来ます．")

    

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("ごめんなさい，そのコマンドは理解しかねます．")
    print("Error:", type(error), error)

bot

def reset_flag():
    Timer.REQUEST_CAPTION = False
    TagManager.DELETE_CONFIRM = False
    TagManager.MERGE_CONFIRM = False
    TagManager.RENAME_CONFIRM = False
    RecordFixer.DELETE_ROCORD_CONFIRM = False
    RecordFixer.FIX_ROCORD_CONFIRM = False

bot.run(token)
