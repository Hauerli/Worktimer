import datetime as dt
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import sqlite3
import database as db
import xlsxwriter
from datetime import date


""" TO_DO LIST 
* Delete Button on Overview Frame + Opt in
* Settingspage - Move Weekhours on the Page 
* Settingspage - Autoclose option
* Overview - Sum Overtime 
* Bug Time field 

"""


class MainApp:
    def __init__(self, parent):
        self.parent = parent
        # create the parent window
        self.parent.title("Worktimer")
        # self.parent.geometry("250x200")
        # Define Tabs
        self.tab_parent = Autoresized_Notebook(self.parent)
        self.t_main = tk.Frame()
        self.t_overview = tk.Frame()
        self.t_customizing = tk.Frame()
        self.tab_parent.add(self.t_main, text="Stempeluhr")
        self.tab_parent.add(self.t_overview, text="Übersicht")
        self.tab_parent.add(self.t_customizing, text="Anpassung")
        self.tab_parent.grid(row=0, column=0, sticky="nsew")
        # createsub frames
        self.f_Input = tk.Frame(
            self.t_main,
        )
        self.f_Input.grid(row=0, column=0)
        self.f_Button = tk.Frame(self.t_main)
        self.f_Button.grid(row=1, column=0)
        ########################## MAIN FRAME #####################
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
        self.l_Break = tk.Label(self.f_Input, text="Standard Pause:")
        self.l_Break.grid(row=3, column=0)
        # Break Radiobutton
        self.varBreakInput = tk.StringVar()
        self.varBreakInput.set("01:00")
        self.varBreakInput.trace(
            "w",
            lambda name, index, mode, varTime=self.varBreakInput: entryUpdateEndHour(
                self.e_break
            ),
        )
        self.e_break = tk.Entry(self.f_Input, textvariable=self.varBreakInput, width=10)
        self.varBreak = tk.IntVar()
        self.b_BreakYes = tk.Radiobutton(
            self.f_Input,
            text="Ja",
            variable=self.varBreak,
            value=1,
            command=lambda: self.triggerBreakfieldVisibility(),
        )
        self.b_BreakYes.grid(row=3, column=1, sticky="w")
        self.b_BreakNo = tk.Radiobutton(
            self.f_Input,
            text="Nein",
            variable=self.varBreak,
            value=0,
            command=lambda: self.triggerBreakfieldVisibility(),
        )
        self.varBreak.set(1)
        self.b_BreakNo.grid(row=4, column=1, sticky="w")
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
                self.varDate.get(),
                self.varTime.get(),
                self.varBreak.get(),
                self.varBreakInput.get(),
            ),
        )
        self.b_Gehen.grid(row=0, column=1)
        ######### OVERVIEW FRAME ###############################
        # Build tableview
        self.l_overtime = tk.Label(self.t_overview, text="Ueberstd. gesamt: ")
        self.l_overtime.grid(column=0, row=0, sticky="w")
        self.varOverallOvertime = tk.StringVar()
        self.e_overtime = tk.Entry(
            self.t_overview, textvariable=self.varOverallOvertime
        )
        self.varOverallOvertime.set(calcOverallOvertime())
        self.e_overtime.configure(state="readonly")
        self.e_overtime.grid(column=1, row=0, sticky="w")
        # Refresh Button
        self.b_refresh = tk.Button(
            self.t_overview,
            text="Aktualisieren",
            command=lambda: [
                cleanTreeview(self.t_overview),
                buildTreeview(self.t_overview, view_columns, loadOverview()),
                self.varOverallOvertime.set(calcOverallOvertime()),
            ],
        )
        self.b_refresh.grid(column=0, row=2, sticky="we", columnspan=2)
        view_columns = ("DATUM", "VON", "BIS", "PAUSE", "ARBEITSZEIT", "UEBERSTD")
        buildTreeview(self.t_overview, view_columns, loadOverview())
        #########CUSTOMIZING FRAME ####################
        # TimeperWeek label
        self.l_TimePerWeek = tk.Label(self.t_customizing, text="Arbeitszeit/Woche:")
        self.l_TimePerWeek.grid(row=0, column=0)
        # TimeperWeek Inputfield
        self.varTimeWeek = tk.StringVar()
        self.workweeksetting = loadSetting("workweekhours")
        self.varTimeWeek.set(self.workweeksetting)
        self.e_TimePerWeek = tk.Entry(
            self.t_customizing, textvariable=self.varTimeWeek, width=10
        )
        self.e_TimePerWeek.grid(row=0, column=1)
        # TimeperWeek Button
        self.b_SaveTimeWeek = tk.Button(
            self.t_customizing,
            text="Speichern",
            width=7,
            command=lambda: insertWeekhours(self.varTimeWeek.get()),
        )
        self.b_SaveTimeWeek.grid(row=0, column=2)
        # Update Label
        self.l_deleteRow = tk.Label(self.t_customizing, text="Lösche Datum: ")
        self.l_deleteRow.grid(row=1, column=0)
        # update entry
        self.varDeleteRow = tk.StringVar()
        self.e_DeleteRow = tk.Entry(
            self.t_customizing, textvariable=self.varDeleteRow, width=10
        )
        self.e_DeleteRow.grid(row=1, column=1)
        # update button
        self.b_DeleteRow = tk.Button(
            self.t_customizing,
            text="Löschen",
            width=7,
            command=lambda: deleteDate(self.varDeleteRow.get()),
        )
        self.b_DeleteRow.grid(row=1, column=2)
        # export label
        self.l_export = tk.Label(self.t_customizing, text="Export Pfad: ")
        self.l_export.grid(row=2, column=0)
        # export entry
        self.varExport = tk.StringVar()
        self.e_export = tk.Entry(
            self.t_customizing, textvariable=self.varExport, width=10
        )
        self.e_export.grid(row=2, column=1)
        # export button
        self.b_export = tk.Button(
            self.t_customizing,
            text="Export",
            width=7,
            command=lambda: createExcelFile(self.varExport.get()),
        )
        self.b_export.grid(row=2, column=2)

    def run(self):
        self.parent.mainloop()

    def kill(self):
        self.parent.destroy()

    # trigger visibility of custom break field
    def triggerBreakfieldVisibility(self):
        if self.varBreak.get() == 1:
            self.e_break.grid_remove()
            self.b_BreakNo.grid(row=4, column=1, sticky="w")
        else:
            self.e_break.grid(row=4, column=1, sticky="w")
            self.b_BreakNo.grid_remove()


# Resize Window based on active tab size
class Autoresized_Notebook(ttk.Notebook):
    def __init__(self, master=None, **kw):

        ttk.Notebook.__init__(self, master, **kw)
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        event.widget.update_idletasks()

        tab = event.widget.nametowidget(event.widget.select())
        event.widget.configure(height=tab.winfo_reqheight(), width=tab.winfo_reqwidth())


def deleteDate(date):
    try:
        con = db.db_connect()
        cur = con.cursor()
        cur.execute("DELETE FROM worktime WHERE DATUM=?", [date])
        con.commit()
        messagebox.showinfo("Info", date + " wurde erfolgreich gelöscht")
    except sqlite3.Error as error:
        print("Module deleteDate: ", error)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


# remove all entries from Treeview
def cleanTreeview(wid):
    for widget in wid.winfo_children():
        if isinstance(widget, ttk.Treeview):
            widget.delete(*widget.get_children())


# Create and insert values into treeview
def buildTreeview(parent, columnames, entrys):
    tree = ttk.Treeview(parent, columns=columnames, show="headings")
    for entry in entrys:
        tree.insert(
            "",
            "end",
            values=(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]),
        )
    for col in columnames:
        tree.heading(col, text=col)
        tree.column(col, width=80)
    tree.grid(row=1, column=0, columnspan=2)


# Load all db entries
def loadOverview():
    con = db.db_connect()
    cur = con.cursor()
    cur.row_factory = lambda cursor, row: row[0:6]
    worklist = cur.execute("SELECT * FROM worktime").fetchall()
    return worklist


# Load current Time from system to preload field
def getCurrTime():
    currTime = str(dt.datetime.now().time())
    currTime = currTime[:5]
    return currTime


# Load current Date from system to preload field
def getCurrDate():
    currDate = dt.date.today().strftime("%d.%m.%Y")
    return currDate


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
        con = db.db_connect()
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


def saveGehen(dat, tim, didbreak, custombreak):
    try:
        con = db.db_connect()
        cur = con.cursor()
        cur.execute("UPDATE worktime SET BIS=? WHERE DATUM=?", (tim, dat))

        calcWorktime(dat, didbreak, custombreak, con, cur)
    except sqlite3.Error as error:
        print("Module saveGehen: ", error)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def insertWeekhours(weekhours):
    try:
        con = db.db_connect()
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


def calcWorktime(date, didbreak, custombreak, con, cur):
    try:

        # select necessary data from db
        cur.execute(
            "SELECT VON FROM worktime WHERE DATUM=?", [date]
        )  # select von from row where date
        select_von = cur.fetchone()
        cur.execute(
            "SELECT BIS FROM worktime WHERE DATUM=?", [date]
        )  # select bis from row where date
        select_bis = cur.fetchone()

        vonInMinutes = convertTimetoMinutes(select_von)
        bisInMinutes = convertTimetoMinutes(select_bis)

        deltaInMinutes = bisInMinutes - vonInMinutes

        custombreak = convertTimetoMinutes(custombreak)

        if didbreak == True:
            if deltaInMinutes > 360:  # if worktime bigger than 6 hours
                custombreak = 60
                deltaInMinutes = deltaInMinutes - custombreak
            elif (
                deltaInMinutes <= 360 and deltaInMinutes > 270
            ):  # if worktime between 5:59 hours and 4:30 hours
                custombreak = 15
                deltaInMinutes = deltaInMinutes - custombreak
        else:
            deltaInMinutes = deltaInMinutes - custombreak

        strTime = convertMinutestoTimeString(deltaInMinutes)
        strBreak = convertMinutestoTimeString(custombreak)
        # insert break
        cur.execute("UPDATE worktime SET PAUSE=? WHERE DATUM=?", (strBreak, date))

        cur.execute("UPDATE worktime SET ARBEITSZEIT=? WHERE DATUM=?", (strTime, date))
        con.commit()
        CalcOvertime(date, con, cur)

    except sqlite3.Error as error:
        print("Module calcWorktime: ", error)


def CalcOvertime(date, con, cur):
    try:
        cur.execute("SELECT VALUE FROM settings WHERE NAME='workweekhours'")
        weekworktime = cur.fetchone()
        dayworktimeInMinutes = (int(weekworktime[0]) * 60) / 5

        cur.execute("SELECT ARBEITSZEIT FROM worktime WHERE DATUM=?", [date])
        select_worktime = cur.fetchone()

        workTimeInMinutes = convertTimetoMinutes(select_worktime)

        if dayworktimeInMinutes < workTimeInMinutes:
            overtime = workTimeInMinutes - dayworktimeInMinutes
            overtime = convertMinutestoTimeString(overtime)
            overtimerfinal = "+" + overtime
        else:
            overtime = dayworktimeInMinutes - workTimeInMinutes
            overtime = convertMinutestoTimeString(overtime)
            overtimerfinal = "-" + overtime

        cur.execute(
            "UPDATE worktime SET UEBERSTUNDEN=? WHERE DATUM=?", (overtimerfinal, date)
        )
        con.commit()
    except sqlite3.Error as error:
        print("Module CalcOvertime: ", error)


def calcOverallOvertime():
    positivOvertime = 0
    negativeOvertime = 0
    overallPrefix = ""

    try:
        con = db.db_connect()
        cur = con.cursor()
        cur.execute("SELECT UEBERSTUNDEN FROM worktime")
        listOvertimes = cur.fetchall()

        for time in listOvertimes:
            if time[0] is not None:
                strTime = time[0]
                prefix = strTime[0:1]
                newTime = strTime[1:]
                if prefix == "+":
                    timeInMinutes = convertTimetoMinutes(newTime)
                    positivOvertime = positivOvertime + timeInMinutes
                else:
                    timeInMinutes = convertTimetoMinutes(newTime)
                    negativeOvertime = negativeOvertime + timeInMinutes

        if positivOvertime > negativeOvertime:
            intSum = positivOvertime - negativeOvertime
            overallPrefix = "+"
        elif negativeOvertime > positivOvertime:
            intSum = negativeOvertime - positivOvertime
            overallPrefix = "-"
        else:
            intSum = 0

        strOverallOvertime = convertMinutestoTimeString(intSum)

        return overallPrefix + str(strOverallOvertime)

    except sqlite3.Error as error:
        print("Module calcOverallOvertime: ", error)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def loadSetting(name):
    try:
        con = db.db_connect()
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


def convertTimetoMinutes(time):

    if isinstance(time, tuple):
        listTime = time[0].split(":")
    else:
        listTime = time.split(":")

    hoursToMinutes = int(listTime[0]) * 60
    overallMinutes = hoursToMinutes + int(listTime[1])

    return overallMinutes


def convertMinutestoTimeString(timeInMinutes):

    minutes = int(timeInMinutes) % 60
    hours = int((timeInMinutes - minutes) / 60)

    # add 0 in front of number smaller than 10
    if hours < 10:
        hours = "0" + str(hours)
    else:
        hours = str(hours)

    # add 0 in front of number smaller than 10
    if minutes < 10:
        minutes = "0" + str(minutes)
    else:
        minutes = str(minutes)

    time = hours + ":" + minutes
    return time


# Export all data form file into Excel
def createExcelFile(path):
    try:

        con = db.db_connect()
        cur = con.cursor()

        cur.execute("SELECT * FROM worktime")
        data = cur.fetchall()

        path = path.replace("\\", "/")

        if path[:-1] != "/":
            path = path + "/"

        today = date.today()
        workbook = xlsxwriter.Workbook(
            path + "Worktimer_Export_" + today.strftime("%d_%m_%Y") + ".xlsx"
        )
        worksheet = workbook.add_worksheet("Arbeitszeiten")

        row = 1

        for entry in data:
            for column, value in enumerate(entry):
                worksheet.write(row, column, value)
            row += 1

        workbook.close()
        messagebox.showinfo(
            "Info", "Arbeitszeiten erfolgreich exportiert nach " + path[:-1]
        )
    except sqlite3.Error as error:
        messagebox.showerror("Module createExcelFile", error)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


if __name__ == "__main__":

    db.createDB()
    root = tk.Tk()
    app = MainApp(root)
    app.run()