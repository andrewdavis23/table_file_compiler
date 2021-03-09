from tkinter import *
from tkinter import filedialog
import pandas as pd

load_flag = False
out_flag = False

all_data = pd.DataFrame()

# select files and create display for window
def open_file():
    files = filedialog.askopenfilenames()

    load_flag = True

    print('files loaded:')
    for i in files:
        print(i)

def out_dir():
    directory = filedialog.askdirectory()
    print('\noutput directory:\n'+directory)

def compile(files):
    pass

window = Tk()
window.title("CSV Compiler")
window.geometry('300x300')

lbl_msg = Label(window, text="Select the files that you wish to compile.\nAll files should contain the same headers.")
lbl_sts = Label(window, text="files loaded {}\noutput folder {}".format(load_flag,out_flag))

btn_open_file = Button(window, text="Select Files", command=open_file)
btn_out_dir = Button(window, text="Select Output Folder", command=out_dir)
btn_compile = Button(window, text="COMPILE", comman=compile)

lbl_msg.grid(column=0, row=0)

btn_open_file.grid(column=0, row=1)
btn_out_dir.grid(column=0, row=2)

lbl_sts.grid(column=0, row=3)

window.mainloop()
