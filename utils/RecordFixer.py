import discord
import sqlite3
import datetime

class RecordFixer:
    DB_NANE = ""
    DELETE_ROCORD_CONFIRM = False
    FIX_ROCORD_CONFIRM = False

    def exists_record(tag_id, dt):
        if isinstance(dt, datetime.datetime):
          dt = dt.strftime("%Y_%m_%d %H:%M:%S")
        db = sqlite3.connect(RecordFixer.DB_NANE)
        cur = db.cursor()
        sql = """
        SELECT * FROM times WHERE id = "{}" AND start_date = "{}"
        """.format(tag_id, dt)
        cur.execute(sql)
        result = not cur.fetchone() is None
        db.close()
        return result

class DeleteRecord(discord.ui.View):
    def __init__(self, tag_id, dt):
        self.tag_id = tag_id
        self.dt = dt.strftime("%Y_%m_%d %H:%M:%S")
        super().__init__()

    @discord.ui.button(label = "記録を削除する")
    async def delete_record(self, interaction, button):
        if not RecordFixer.DELETE_ROCORD_CONFIRM:
            await interaction.response.send_message("現在このボタンは使えません！　$delete_recordからやり直してください．")
            return
        
        db = sqlite3.connect(RecordFixer.DB_NANE)
        cur = db.cursor()
        sql = """
        DELETE FROM times WHERE id = "{}" AND start_date = "{}"
        """.format(self.tag_id, self.dt)
        cur.execute(sql)
        db.commit()
        db.close()

        RecordFixer.DELETE_ROCORD_CONFIRM = False
        await interaction.response.send_message("削除が完了しました！")

class FixRecord(discord.ui.View):
    def __init__(self, tag_id, dt):
        self.tag_id = tag_id
        self.dt = dt.strftime("%Y_%m_%d %H:%M:%S")
        super().__init__()

    @discord.ui.button(label = "記録を編集する")
    async def fix_record(self, interaction, button):
        if not RecordFixer.FIX_ROCORD_CONFIRM:
            await interaction.response.send_message("現在このボタンは使えません！　$fix_recordからやり直してください．")
            return
        await interaction.response.send_modal(_FixRecordModal(self.tag_id, self.dt))

class _FixRecordModal(discord.ui.Modal, title="記録の編集"):
    def __init__(self, tag_id, dt):
        super().__init__()
        self.prev_dt = dt

        db = sqlite3.connect(RecordFixer.DB_NANE)
        cur = db.cursor()
        sql = """
        SELECT * FROM times WHERE id = "{}" AND start_date = "{}"
        """.format(tag_id, dt)
        cur.execute(sql)
        self.tag_id, self.s_dt, _, time, comment = cur.fetchone()
        db.close()

        self.dt_in = discord.ui.TextInput(label = "日時",
                                           style = discord.TextStyle.short,
                                           default = self.s_dt,
                                           required = True)
        self.add_item(self.dt_in)
        self.time_in = discord.ui.TextInput(label = "計測時間",
                                           style = discord.TextStyle.short,
                                           default = time,
                                           required = True)
        self.add_item(self.time_in)
        self.caption_in = discord.ui.TextInput(label = "キャプション",
                                           style = discord.TextStyle.paragraph,
                                           default = comment,
                                           required = False)
        self.add_item(self.caption_in)

    async def on_submit(self, interaction):
        db = sqlite3.connect(RecordFixer.DB_NANE)
        cur = db.cursor()
        if self.prev_dt != self.dt_in.value and RecordFixer.exists_record(self.tag_id, self.dt_in.value):
            sql = "SELECT tag_name FROM tags WHERE id = \"{}\"".format(self.tag_id)
            cur.execute(sql)
            tag_name = cur.fetchone()[0]
            db.close()
            await interaction.response.send_message("【{}】には{}の記録がすでに存在しているため，修正を行えませんでした．".format(
                tag_name, self.dt_in.value))
            return
        try:
            dt = datetime.datetime.strptime(self.dt_in.value, "%Y_%m_%d %H:%M:%S")
        except:
            await interaction.response.send_messafe("日時の形式が正しくありません！\n日時は\"%Y_%m_%d %H:%M:%S\"に従って入力してください．")
            return
        day = dt.strftime("%Y_%m_%d")

        sql = """
        UPDATE times SET start_date = "{}", day = "{}", time = "{}", comment = "{}"
         WHERE id = "{}" AND start_date = "{}"
        """.format(self.dt_in.value, day, self.time_in.value, self.caption_in.value, self.tag_id, self.prev_dt)
        cur.execute(sql)
        db.commit()
        db.close()
        RecordFixer.FIX_ROCORD_CONFIRM = False
        await interaction.response.send_message("編集が完了しました！")