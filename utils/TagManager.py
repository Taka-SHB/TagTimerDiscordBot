import discord

import sqlite3
import uuid


class TagManager:
    DB_NAME = ""
    TAG_DICT = dict()
    CURRENT_ID = ""
    DELETE_CONFIRM = False
    MERGE_CONFIRM = False
    RENAME_CONFIRM = False
        
class AddTag(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label = "タグを追加する")
    async def open_add_tag_modal(self, interaction, button):
        await interaction.response.send_modal(_AddTagModal())

class _AddTagModal(discord.ui.Modal, title="新しいタグの追加"):
    new_tag = discord.ui.TextInput(label="タグの名称", 
                                   placeholder='新しいタグの名称',
                                   required=True)

    async def on_submit(self, interaction):
        try:
            db = sqlite3.connect(TagManager.DB_NAME)
            cur = db.cursor()
            tag_id = str(uuid.uuid4())
            sql = "INSERT INTO tags VALUES(\"{}\", \"{}\")".format(tag_id, self.new_tag.value)
            cur.execute(sql)
            db.commit()
            db.close()

            TagManager.TAG_DICT[tag_id] = self.new_tag.value
            TagManager.CURRENT_ID = tag_id
            await interaction.response.send_message("【{}】を追加しました！\nおまけで，現在のタグに設定しておきました．".format(self.new_tag.value))
        except Exception as e:
            print(e)
            await interaction.response.send_message("申し訳ありません，【{}】は追加できませんでした．".format(self.new_tag.value))

class DeleteTag(discord.ui.View):
    def __init__(self, in_id):
        self.del_id = in_id
        super().__init__()

    @discord.ui.button(label = "削除する")
    async def delete_tag(self, interaction, button):
        if not TagManager.DELETE_CONFIRM:
            await interaction.response.send_message("現在このボタンは使えません！　$del_tagからやり直してください．")
            return
        if TagManager.CURRENT_ID == self.del_id:
            TagManager.CURRENT_ID = ""

        db = sqlite3.connect(TagManager.DB_NAME)
        cur = db.cursor()
        sql = """
        DELETE FROM times WHERE id = "{}"
        """.format(self.del_id)
        cur.execute(sql)
        sql = """
        DELETE FROM tags WHERE id = "{}"
        """.format(self.del_id)
        cur.execute(sql)
        db.commit()
        db.close()

        TagManager.DELETE_CONFIRM = False
        TagManager.TAG_DICT = load_tag_dict_from_db()
        await interaction.response.send_message("削除が完了しました！")

class MergeTag(discord.ui.View):
    def __init__(self, in_id1, in_id2):
        self.base_id = in_id1
        self.minor_id = in_id2
        super().__init__()

    @discord.ui.button(label = "併合する")
    async def merge(self, interaction, button):
        if not TagManager.MERGE_CONFIRM:
            await interaction.response.send_message("現在このボタンは使えません！　$merge_tagからやり直してください．")
            return
        if TagManager.CURRENT_ID == self.minor_id:
            TagManager.CURRENT_ID = ""

        db = sqlite3.connect(TagManager.DB_NAME)
        cur = db.cursor()
        sql = """
        UPDATE times SET id = "{}" WHERE id = "{}"
        """.format(self.base_id, self.minor_id)
        cur.execute(sql)
        sql = """
        DELETE FROM tags WHERE id = "{}"
        """.format(self.minor_id)
        cur.execute(sql)
        db.commit()
        db.close()

        TagManager.MERGE_CONFIRM = False
        TagManager.TAG_DICT = load_tag_dict_from_db()
        await interaction.response.send_message("併合が完了しました！")

class RenameTag(discord.ui.View):
    def __init__(self, in_id):
        self.tag_id = in_id
        super().__init__()

    @discord.ui.button(label="名称の変更")
    async def rename(self, interaction, button):
        if not TagManager.RENAME_CONFIRM:
            await interaction.response.send_message("現在このボタンは使えません！　$rename_tagからやり直してください．")
            return
        await interaction.response.send_modal(_RenameTagModal(self.tag_id))

class _RenameTagModal(discord.ui.Modal, title="タグの名称変更"):
    def __init__(self, in_id):
        super().__init__()
        self.new_name = discord.ui.TextInput(label = "タグの新しい名称",
                                        placeholder = "新しい名称",
                                        style = discord.TextStyle.short,
                                        default = TagManager.TAG_DICT[in_id],
                                        required = True
                                        )
        self.add_item(self.new_name)
        self.tag_id = in_id
        
    async def on_submit(self, interaction):
        name = self.new_name.value

        db = sqlite3.connect(TagManager.DB_NAME)
        cur = db.cursor()
        sql = "UPDATE tags SET tag_name = \"{}\" WHERE id = \"{}\"".format(name, self.tag_id)
        cur.execute(sql)
        db.commit()
        db.close()

        TagManager.RENAME_CONFIRM = False
        TagManager.TAG_DICT = load_tag_dict_from_db()
        await interaction.response.send_message("名称が【{}】に変更されました！".format(name))

def load_tag_dict_from_db():
    db = sqlite3.connect(TagManager.DB_NAME)
    cur = db.cursor()
    sql = """
    SELECT id, tag_name FROM tags
    """
    cur.execute(sql)
    tags = dict(t for t in cur.fetchall())
    db.close()
    return tags

