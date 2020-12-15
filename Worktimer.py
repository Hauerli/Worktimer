import datetime as dt
import tkinter as tk
import sqlite3
import os

DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), "database.sqlite3"
)  # define dfilepath to be identical to folder


class MainApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        # create the parent window
        self.parent.title("Worktimer")
        self.parent.geometry("250x150")

        # createsub frames
        self.f_Input = tk.Frame(self.parent)
        self.f_Input.grid(row=0, column=0)
        self.f_Button = tk.Frame(self.parent)
        self.f_Button.grid(row=1, column=0)
        # TimeperWeek label
        self.l_TimePerWeek = tk.Label(self.f_Input, text="Arbeitszeit/Woche:")
        self.l_TimePerWeek.grid(row=0, column=0)
        # TimeperWeek Inputfield
        self.varTimeWeek = tk.StringVar()
        self.workweeksetting = loadSetting("workweekhours")
        self.varTimeWeek.set(self.workweeksetting)
        self.e_TimePerWeek = tk.Entry(
            self.f_Input, textvariable=self.varTimeWeek, width=10
        )
        self.e_TimePerWeek.grid(row=0, column=1)
        # TimeperWeek Button
        self.b_SaveTimeWeek = tk.Button(
            self.f_Input,
            text="Save",
            command=lambda: insertWeekhours(self.varTimeWeek.get()),
        )
        self.b_SaveTimeWeek.grid(row=0, column=3)
        # Date Label
        self.l_Date = tk.Label(self.f_Input, text="Datum:")
        self.l_Date.grid(row=1, column=0)
        # Date Inputfield
        self.varDate = tk.StringVar()
        self.varDate.set(getCurrDate())
        self.e_Date = tk.Entry(self.f_Input, textvariable=self.varDate, width=10)
        self.e_Date.grid(row=1, column=1)
        # Time Label
        self.l_Time = tk.Label(self.f_Input, text="Uhrzeit:")
        self.l_Time.grid(row=2, column=0)
        # Time Inputfield
        self.varTime = tk.StringVar()
        self.varTime.set(getCurrTime())
        self.e_Time = tk.Entry(self.f_Input, textvariable=self.varTime, width=10)
        self.varTime.trace(
            "w",
            lambda name, index, mode, varTime=self.varTime: entryUpdateEndHour(
                self.e_Time
            ),
        )
        self.e_Time.grid(row=2, column=1)
        # Break label
        self.l_Break = tk.Label(self.f_Input, text="Pause:")
        self.l_Break.grid(row=3, column=0)
        # Break Radiobutton
        self.varBreak = tk.IntVar()
        self.b_BreakYes = tk.Radiobutton(
            self.f_Input, text="Ja", variable=self.varBreak, value=1
        )
        self.b_BreakYes.grid(row=4, column=0)
        self.b_BreakNo = tk.Radiobutton(
            self.f_Input, text="Nein", variable=self.varBreak, value=0
        )
        self.varBreak.set(1)
        self.b_BreakNo.grid(row=4, column=1)
        # Button Kommen
        self.b_Kommen = tk.Button(
            self.f_Button,
            text="Kommen",
            command=lambda: saveKommen(self.varDate.get(), self.varTime.get()),
        )
        self.b_Kommen.grid(row=0, column=0)
        # Button Gehen
        self.b_Gehen = tk.Button(
            self.f_Button,
            text="Gehen",
            command=lambda: saveGehen(
                self.varDate.get(), self.varTime.get(), self.varBreak.get()
            ),
        )
        self.b_Gehen.grid(row=0, column=1)

    def run(self):
        self.parent.mainloop()

    def kill(self):
        self.parent.destroy()


def db_connect(db_path=DEFAULT_PATH):  # module to create hte db
    con = sqlite3.connect(db_path)
    return con


def createDB():
    try:
        con = db_connect()  # connect to the database
        cur = con.cursor()  # initiate the obj cursor
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS worktime (
            DATUM TEXT PRIMARY KEY,
            VON TEXT,
            BIS TEXT, 
            PAUSE TEXT,
            ARBEITSZEIT TEXT,
            UEBERSTUNDEN TEXT
        )"""
        )
        cur.execute(
            """

        CREATE TABLE IF NOT EXISTS settings (
            NAME TEXT PRIMARY KEY,
            VALUE INTEGER 
        )"""
        )

        cur.execute("SELECT * FROM settings WHERE NAME='workweekhours'")
        entry = cur.fetchone()
        if entry is None:
            cur.execute(
                "INSERT OR REPLACE INTO settings(NAME,VALUE) VALUES(?,?)",
                ("workweekhours", 35),
            )

        con.commit()
        cur.close()
    except sqlite3.Error as error:
        print("Failed to create database", error)
    finally:
        if con:
            con.close()


# Load current Date from system to preload field
def getCurrDate():
    currDate = dt.date.today().strftime("%d.%m.%Y")
    return currDate


# Load current Time from system to preload field
def getCurrTime():
    currTime = str(dt.datetime.now().time())
    currTime = currTime[:5]
    return currTime


# reload entryfield to format to time
def entryUpdateEndHour(entry):
    text = entry.get()
    if len(text) == 0:
        return
    elif len(text) == 2:
        entry.insert(tk.END, ":")
        entry.icursor(len(text) + 1)
    elif len(text) != 3:
        if not text[-1].isdigit():
            entry.delete(0, tk.END)
            entry.insert(0, text[:-1])
    if len(text) > 5:
        entry.delete(0, tk.END)
        entry.insert(0, text[:5])


def saveKommen(dat, tim):
    try:
        con = db_connect()
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO worktime(DATUM,VON) VALUES(?,?)", (dat, tim))
        con.commit()
    except sqlite3.Error as error:
        print("Module saveKommen: ", error)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def saveGehen(dat, tim, didbreak):
    try:
        con = db_connect()
        cur = con.cursor()
        cur.execute("UPDATE worktime SET BIS=? WHERE DATUM=?", (tim, dat))

        insertBreak(dat, didbreak, con, cur)
    except sqlite3.Error as error:
        print("Module saveGehen: ", error)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def insertBreak(dat, didbreak, con, cur):
    try:
        cur.execute("UPDATE worktime SET PAUSE=? WHERE DATUM=?", (didbreak, dat))
        con.commit()
        calcWorktime(dat, didbreak, con, cur)  # call calcWorktime
    except sqlite3.Error as error:
        print("Module insertBreak: ", error)


def insertWeekhours(weekhours):
    try:
        con = db_connect()
        cur = con.cursor()
        cur.execute(
            "UPDATE settings SET VALUE=? WHERE NAME=?",
            (weekhours, "workweekhours"),
        )
        con.commit()
    except sqlite3.Error as error:
        print("Module insertWeekhours: ", error)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def calcWorktime(date, didbreak, con, cur):
    try:
        cur.execute(
            "SELECT VON FROM worktime WHERE DATUM=?", [date]
        )  # select von from row where date
        select_von = cur.fetchone()
        cur.execute(
            "SELECT BIS FROM worktime WHERE DATUM=?", [date]
        )  # select bis from row where date
        select_bis = cur.fetchone()
        delta = dt.datetime.strptime(select_bis[0], "%H:%M") - dt.datetime.strptime(
            select_von[0], "%H:%M"
        )
        if didbreak == 1:
            if delta > dt.timedelta(hours=6):
                delta = delta - dt.timedelta(hours=1)
            elif delta <= dt.timedelta(hours=6) and delta > dt.timedelta(
                hours=4, minutes=30
            ):
                delta = delta - dt.timedelta(hours=0, minutes=15)

        strdelta = str(delta)
        if strdelta[1] == ":":
            strdelta = strdelta[:4]
            strdelta = "0" + strdelta
        else:
            strdelta = strdelta[:5]
        cur.execute("UPDATE worktime SET ARBEITSZEIT=? WHERE DATUM=?", (strdelta, date))
        con.commit()
        CalcOvertime(date, con, cur)

    except sqlite3.Error as error:
        print("Module calcWorktime: ", error)


def CalcOvertime(date, con, cur):
    try:
        cur.execute("SELECT VALUE FROM settings WHERE NAME='workweekhours'")
        weekworktime = cur.fetchone()
        dayworktime = weekworktime[0] / 5
        dayworktime = dt.timedelta(hours=dayworktime)
        cur.execute("SELECT ARBEITSZEIT FROM worktime WHERE DATUM=?", [date])
        select_worktime = cur.fetchone()
        worktime = dt.datetime.strptime(select_worktime[0], "%H:%M")
        secworktime = (worktime.hour * 60 + worktime.minute) * 60

        # else statement geht nicht, falsche convertierung
        if dayworktime.total_seconds() < secworktime:
            overtime = worktime - dayworktime
            strovertime = dt.datetime.strptime(str(overtime)[11:16], "%H:%M")
            overtimefinal = "+" + str(strovertime)[11:16]
        else:
            oneday = dt.datetime.strptime(
                str(dt.timedelta(seconds=86341))[0:5], "%H:%M"
            )
            overtime = oneday - (worktime - dayworktime)
            overtime = overtime + dt.timedelta(seconds=60)
            strovertime = dt.datetime.strptime(str(overtime)[7:11], "%H:%M")
            overtimefinal = "-" + str(strovertime)[11:16]

        cur.execute(
            "UPDATE worktime SET UEBERSTUNDEN=? WHERE DATUM=?", (overtimefinal, date)
        )
        con.commit()
    except sqlite3.Error as error:
        print("Module CalcOvertime: ", error)


def loadSetting(name):
    try:
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT VALUE FROM settings WHERE NAME=?", [name])
        value = cur.fetchone()
        cur.close()
        return value
    except sqlite3.Error as error:
        print("Module loadSetting: ", error)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


if __name__ == "__main__":
    createDB()

    root = tk.Tk()
    app = MainApp(root)
    app.run()
