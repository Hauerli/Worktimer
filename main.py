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
        # createsub frames
        self.f_Input = tk.Frame(self.parent)
        self.f_Input.grid(row=0, column=0)
        self.f_Button = tk.Frame(self.parent)
        self.f_Button.grid(row=1, column=0)
        # Date Label
        self.l_Date = tk.Label(self.f_Input, text="Date:")
        self.l_Date.grid(row=0, column=0)
        # Date Inputfield
        self.varDate = tk.StringVar()
        self.varDate.set(getCurrDate())
        self.e_Date = tk.Entry(self.f_Input, textvariable=self.varDate, width=10)
        self.e_Date.grid(row=0, column=1)
        # Time Label
        self.l_Time = tk.Label(self.f_Input, text="Time:")
        self.l_Time.grid(row=1, column=0)
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
        self.e_Time.grid(row=1, column=1)
        # Button Kommen
        self.b_Kommen = tk.Button(
            self.f_Button,
            text="Kommen",
            command=saveKommen(self.varDate.get(), self.varTime.get()),
        )
        self.b_Kommen.grid(row=0, column=0)
        # Button Gehen
        self.b_Gehen = tk.Button(
            self.f_Button,
            text="Gehen",
            command=saveGehen(self.varDate.get(), self.varTime.get()),
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
        worktime_sql = """
        CREATE TABLE IF NOT EXISTS worktime (
            Datum TEXT PRIMARY KEY,
            Von TEXT,
            Bis TEXT, 
            Pause TEXT,
            Gesamtzeit TEXT
        )"""
        cur.execute(worktime_sql)
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
        sql_insert_kommen = "INSERT OR IGNORE INTO worktime(Datum,Von) VALUES(?,?)"
        con = db_connect()
        cur = con.cursor()
        cur.execute(sql_insert_kommen, (dat, tim))
        con.commit()
        cur.close()
    except sqlite3.Error as error:
        print("Failed to insert Kommen", error)
    finally:
        if con:
            con.close()


def saveGehen(dat, tim):
    try:
        sql_insert_gehen = "UPDATE worktime SET Bis=? WHERE Datum=?"
        con = db_connect()
        cur = con.cursor()
        cur.execute(sql_insert_gehen, (tim, dat))
        # calcWorktime(dat)
        con.commit()
        cur.close()
    except sqlite3.Error as error:
        print("Failed to insert Kommen", error)
    finally:
        if con:
            con.close()


"""
def calcWorktime(date):
    sql_select_von = "SELECT Von FROM worktime WHERE Datum=? "
    sql_select_bis
"""

if __name__ == "__main__":
    createDB()
    root = tk.Tk()
    app = MainApp(root)
    app.run()