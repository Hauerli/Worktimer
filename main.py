import tkinter as tk
from datetime import datetime

# Load current Time from system to preload field
def getCurrTime():
    currTime = str(datetime.now().time())
    currTime = currTime[:5]
    return currTime

# reload entryfield to format to time
def entryUpdateEndHour(entry):
    text = entry.get()
    if len(text) == 0:
        return
    elif len(text) == 2:
        entry.insert(tk.END, ':')
        entry.icursor(len(text)+1)
    elif len(text) != 3:
        if not text[-1].isdigit() :
            entry.delete(0, tk.END)
            entry.insert(0, text[:-1])
    if len(text) > 5:
        entry.delete(0, tk.END)
        entry.insert(0, text[:5])



# create the root window
root = tk.Tk()
root.title("Worktimer")

#createsub frames
f_Input = tk.Frame(root)
f_Button = tk.Frame(root)
f_Input.grid(row=0, column=0)
f_Button.grid(row=1, column=0)


# Time Label
l_Time = tk.Label(f_Input, text="Time:")
l_Time.grid(row=0, column=0)

# Time Inputfield
varTime = tk.StringVar()
varTime.set(getCurrTime())
e_Time = tk.Entry(f_Input, textvariable=varTime, width=10)
varTime.trace("w", lambda name, index, mode,
              varTime=varTime: entryUpdateEndHour(e_Time))

e_Time.grid(row=0,column=1)

print(varTime)
# Button Kommen
b_Kommen = tk.Button(f_Button, text="Kommen")
b_Kommen.grid(row=0, column=0)

# Button Gehen
b_Gehen = tk.Button(f_Button, text="Gehen")
b_Gehen.grid(row=0, column=1)

if __name__ == "__main__": 
    root.mainloop()


