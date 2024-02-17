import sqlite3
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import japanize_matplotlib
import io

class Analyzer:
    DB_NAME = ""

    def total_tag_time(tag_id):
        db = sqlite3.connect(Analyzer.DB_NAME)
        cur = db.cursor()
        sql = """
        SELECT SUM(time) FROM times WHERE id = "{}"
        """.format(tag_id)
        cur.execute(sql)
        total = cur.fetchone()[0]
        db.close()
        return total
    
    def tag_time_per_day(tag_id):
        db = sqlite3.connect(Analyzer.DB_NAME)
        cur = db.cursor()
        sql = """
        SELECT day, SUM(time) FROM times WHERE id = "{}" GROUP BY day
        """.format(tag_id)
        cur.execute(sql)
        time_data = cur.fetchall()
        db.close()
        return time_data
    
    def total_time_per_tag(s_dt=None, e_dt=None):
        db = sqlite3.connect(Analyzer.DB_NAME)
        cur = db.cursor()
        if s_dt is None:
            sql = """
            SELECT id, SUM(time) FROM times GROUP BY id
            """
            cur.execute(sql)
            time_data = cur.fetchall()
            db.close()
            return time_data
        
        sql = """
        SELECT id FROM tags
        """
        cur.execute(sql)
        tag_ids = [d[0] for d in cur.fetchall()]
        db.close()

        out_data = []
        for tag_id in tag_ids:
            time_data = Analyzer.tag_time_per_day(tag_id)
            total = 0
            for d, t in time_data:
                dt = datetime.datetime.strptime(d, "%Y_%m_%d")
                if dt < s_dt:
                    continue
                if not e_dt is None:
                    if dt > e_dt:
                        continue
                total += t
            out_data.append((tag_id, total))
        return out_data
    
    def stream_csv_tag(tag_id):
        db = sqlite3.connect(Analyzer.DB_NAME)
        cur = db.cursor()
        sql = """
        SELECT times.id, tags.tag_name, times.start_date, times.day, times.time, times.comment
        FROM times LEFT OUTER JOIN tags WHERE times.id = tags.id AND times.id = "{}"
        """.format(tag_id)
        cur.execute(sql)
        csv_data = cur.fetchall()
        db.close()

        s = ",".join(["id", "tag_name", "start_date", "day", "time", "comment"])
        s += ("\n")
        for d in csv_data:
            s += ",".join(map(str, d))
            s +="\n"
        return io.StringIO(s)
    
    def stream_csv_all():
        db = sqlite3.connect(Analyzer.DB_NAME)
        cur = db.cursor()
        sql = """
        SELECT times.id, tags.tag_name, times.start_date, times.day, times.time, times.comment
        FROM times LEFT OUTER JOIN tags WHERE times.id = tags.id
        """
        cur.execute(sql)
        csv_data = cur.fetchall()
        db.close()

        s = ",".join(["id", "tag_name", "start_date", "day", "time", "comment"])
        s += ("\n")
        for d in csv_data:
            s += ",".join(map(str, d))
            s +="\n"
        return io.StringIO(s)
    
    def stream_plot_tag_record(tag_id, s_dt=None, e_dt=None):
        db = sqlite3.connect(Analyzer.DB_NAME)
        cur = db.cursor()
        sql = """
        SELECT tag_name FROM tags WHERE id = "{}"
        """.format(tag_id)
        cur.execute(sql)
        tag_name = cur.fetchone()[0]
        db.close()
        time_data = Analyzer.tag_time_per_day(tag_id)
        
        time_data = list(map(lambda x: (
            datetime.datetime.strptime(x[0], "%Y_%m_%d"), x[1]), time_data))
        time_data = sorted(time_data, key=lambda x: x[0])

        X = [d[0] for d in time_data]
        Y = [d[1] for d in time_data]
        if s_dt is None:
            s_dt = min(X)
        if e_dt is None:
            e_dt = max(X)
        bottom = min(Y)
        top = max(Y)
        yticks = [h * 3600 for h in range(bottom // 3600, top // 3600 + 2)]
        yticklabels = ["{}h".format(h) for h in range(bottom // 3600, top // 3600 + 2)]

        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(X, Y)
        fig.autofmt_xdate(rotation=45)
        ax.set_title("【{}】".format(tag_name))
        locator = mdates.AutoDateLocator(minticks=5, maxticks=8)
        ax.xaxis.set_major_locator(locator)

        ax.set_xlim(s_dt, e_dt)
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)
        ax.set_ylim(min(Y)-(max(Y) - min(Y))*0.05, max(Y)+(max(Y) - min(Y))*0.05)

        sio = io.BytesIO()
        plt.savefig(sio, format="png")
        plt.close()

        sio.seek(0)
        return sio
