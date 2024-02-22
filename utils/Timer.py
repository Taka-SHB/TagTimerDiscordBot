import discord
from discord.ext import commands

import datetime
import sqlite3

class Timer():
    IS_RUNNING = False
    START_DATE = datetime.datetime.now()
    END_DATE = datetime.datetime.now()
    CURRENT_ID = ""
    DB_NAME = ""
    REQUEST_CAPTION = False

class TimerRunningError(commands.errors.CommandError):
    """
    時間計測中に他のコマンドを入力したときに返すためのエラー
    """
    def __init__(self):
        super().__init__()

class StartButton(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="START!!", style=discord.ButtonStyle.success)
    async def start_timer(self, interaction, button):
        if not Timer.IS_RUNNING:
          await interaction.response.send_message("時間の計測を開始しました！\n終了するには$stopを利用してください．")
          timerStart()
        else:
            await interaction.response.send_message("安心してください，現在計測中です！\n終了したいですか？　下のボタンで終了できます！")
            await interaction.channel.send(view = StopButton())

class StopButton(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="STOP", style=discord.ButtonStyle.gray)
    async def stop_timer(self, interaction, button):
        total = timerStop()
        m, s = divmod(total, 60)
        h, m = divmod(m, 60)
        await interaction.response.send_message("計測を終了します．時間は{}時間{}分{}秒でした．\nお疲れさまでした！".format(h, m, s))
        if not Timer.CURRENT_ID == "":
            record_time(total)
            Timer.REQUEST_CAPTION = True
            await interaction.channel.send(view = CaptionButton())

class CaptionButton(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="キャプションを追加", style=discord.ButtonStyle.gray)
    async def add_caption(self, interaction, button):
        if not Timer.REQUEST_CAPTION:
            await interaction.response.send_message("現在はキャプションを必要としていません！")
            return
        await interaction.response.send_modal(_CaptionModal())

class _CaptionModal(discord.ui.Modal, title = "キャプションの追加"):
    caption = discord.ui.TextInput(label = "キャプション",
                                   placeholder = "何でも書いてください！",
                                   style = discord.TextStyle.paragraph,
                                   required = True
                                   )
    async def on_submit(self, interaction):
        cap = self.caption.value
        date = Timer.START_DATE.strftime("%Y_%m_%d %H:%M:%S")

        db = sqlite3.connect(Timer.DB_NAME)
        cur = db.cursor()
        sql = "UPDATE times SET comment = \"{}\" WHERE id = \"{}\" AND start_date = \"{}\"".format(
            cap, Timer.CURRENT_ID, date)
        cur.execute(sql)
        db.commit()
        db.close()

        Timer.REQUEST_CAPTION = False
        await interaction.response.send_message("キャプションを追加しました！")

def timerStart():
    Timer.IS_RUNNING = True
    Timer.START_DATE = datetime.datetime.now()

def timerStop():
    Timer.IS_RUNNING = False
    Timer.END_DATE = datetime.datetime.now()
    time_delta = Timer.END_DATE - Timer.START_DATE
    return time_delta.seconds

def record_time(time):
    tag_id = Timer.CURRENT_ID
    start_date = Timer.START_DATE.strftime("%Y_%m_%d %H:%M:%S")
    day = Timer.START_DATE.strftime("%Y_%m_%d")

    db = sqlite3.connect(Timer.DB_NAME)
    cur = db.cursor()
    sql = "INSERT INTO times VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"\")".format(
        tag_id, start_date, day, time)
    cur.execute(sql)
    db.commit()
    db.close()
