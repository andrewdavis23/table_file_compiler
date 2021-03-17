from tkinter import *
from tkinter import filedialog
import pandas as pd
import glob
from time import sleep
from progress.bar import Bar

# pancake emoji
e = chr(129374)

# compilation
all_data = pd.DataFrame()

# select files and create display for window
def open_file():
    global files

    files = filedialog.askopenfilenames()

    print(e+' files loaded:')
    for i in files:
        print(i)

    # for label which shows user a list of files
    files_list = '\n'
    for i in files:
        files_list += i + '\n'

    lbl_files['text'] = files_list  

    # activate compile button
    check_ready()

def out_dir():
    global directory
    global out_flag

    directory = filedialog.askdirectory()
    print('{} output directory = {}'.format(e,directory))

    out_flag = True

    check_ready()

def compile():
    global files
    global directory

    print(e+' compiling...')
    global all_data

    for f in files:
        temp_df = pd.read_csv(f)
        # temp_df = temp_df.loc[temp_df.STORE_NUM==619]
        all_data = all_data.append(temp_df, ignore_index=True)
    
    out_path = str(directory) + r'/output.csv'
    print('{} out_path = {}'.format(e, out_path))
    print('{} all_data.head() = \n{}'.format(e, all_data.head()))
    all_data.to_csv(out_path,index=False)

def check_ready():
    global files

    if len(files) > 0:
        btn_compile["state"] = NORMAL

window = Tk()
window.title("CSV Compiler")
window.geometry('225x250')

lbl_msg = Label(window, text="\nSelect the files and output folder.\nAll files should contain the same headers.\n")
lbl_msg.grid(column=0, row=0)

btn_open_file = Button(window, text="Select Files", command=open_file)
btn_open_file.grid(column=0, row=1)

btn_out_dir = Button(window, text="Select Output Folder", command=out_dir)
btn_out_dir.grid(column=0, row=2)

btn_compile = Button(window, text="COMPILE",state=DISABLED, command=compile)
btn_compile.grid(column=0, row=3)

lbl_files = Label(window, text='')
lbl_files.grid(column=0, row=4)

window.mainloop()

