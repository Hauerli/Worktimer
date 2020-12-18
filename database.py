import sqlite3
import os

DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), "database.sqlite3"
)  # define dfilepath to be identical to folder


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


def db_connect(db_path=DEFAULT_PATH):  # module to create hte db
    con = sqlite3.connect(db_path)
    return con
