from tkinter import *
from tkinter import filedialog
import pandas as pd
from time import sleep

# pancake emoji
e = chr(129374)

# compilation
all_data = pd.DataFrame()

# select files and display file names in window
def open_file():
    global files

    files = filedialog.askopenfilenames()

    file_list.delete('0','end')

    print(e+' files loaded:')
    for i in files:
        print(i)

    # create string for the tk label
    for i in range(len(files)):
        file_list.insert(i, files[i].split('/')[-1])

    # lbl_files['text'] = files_list  

    # activate compile button
    check_ready()

def compile():
    global files

    print(e+' compiling...')
    global all_data

    for f in files:
        temp_df = pd.read_csv(f)
        # temp_df = temp_df.loc[temp_df.STORE_NUM==619]
        all_data = all_data.append(temp_df, ignore_index=True)
    
    print('{} all_data.head() = \n{}'.format(e, all_data.head()))

    save_file(all_data)

def check_ready():
    global files

    if len(files) > 0:
        btn_compile["state"] = NORMAL

def save_file(all_data):
    out_path = filedialog.asksaveasfile(mode='w', defaultextension=".csv", filetypes=(("Excel Files", "*.xlsx"), ("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")))
    if out_path is None:
        return
    all_data.to_csv(out_path, index=False, line_terminator='\n')
    out_path.close()

# window
root = Tk()
root.title("CSV Compiler")
root.geometry('500x250')

# frame
upper_frame = Frame(root, bd=5)
upper_frame.place(relx=0.5, rely=0.1, relwidth=0.9, relheight=0.1, anchor="n")

lower_frame = Frame(root, bg='gray', bd=5)
lower_frame.place(relx=0.5, rely=0.25, relwidth=0.9, relheight=0.6, anchor="n")

# objects - create/place
lbl_msg = Label(upper_frame, text="Select the files and output folder. All files should contain the same headers.")
lbl_msg.grid(column=0, row=0)

btn_open_file = Button(lower_frame, text="Select Files", command=open_file)
btn_open_file.grid(column=0, row=0)

btn_compile = Button(lower_frame, text="COMPILE", state=DISABLED, command=compile)
btn_compile.grid(column=0, row=1)

# lbl_files = Label(lower_frame, text='')
# lbl_files.grid(column=1, row=2)

# thang
scrollbar = Scrollbar(root)
scrollbar.pack( side = RIGHT, fill = Y )

file_list = Listbox(root, yscrollcommand = scrollbar.set )
file_list.pack( side = RIGHT, fill = BOTH )
scrollbar.config( command = file_list.yview )

root.mainloop()

