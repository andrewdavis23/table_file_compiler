from tkinter import *
from tkinter import filedialog
import pandas as pd

# pancake emoji
e = chr(129374)

# compilation
all_data = pd.DataFrame()

files = []

# select files and display file names in window
def open_file():
    global files
    file_list = ''

    files.extend(list( filedialog.askopenfilenames() ))
    print(e + ' files loaded')

    # add filenames to the tk list box
    for i in files:
        file_list += i.split('/')[-1] + '\n'

    txt_list.insert(END, file_list)

    # activate compile button
    check_ready()

def clear_files():
    global file_list

    file_list = ''
    txt_list.delete('1.0', END)

def compile_csv():
    # plan: make it append on matching column names. exclude excess columns
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
    else:
        btn_compile["state"] = DISABLED

def save_file(all_data):
    out_path = filedialog.asksaveasfile(mode='w', defaultextension=".csv", filetypes=(("Excel Files", "*.xlsx"), ("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")))
    if out_path is None:
        return
    all_data.to_csv(out_path, index=False, line_terminator='\n')
    out_path.close()

# window
root = Tk()
root.title("CSV Compiler")
root.geometry('610x377')

# frame
upper_frame = Frame(root, bd=5)
upper_frame.place(relx=0.5, rely=0.1, relwidth=0.9, relheight=0.2, anchor="n")

lower_frame = Frame(root, bg='peach puff', bd=5)
lower_frame.place(relx=0.5, rely=0.25, relwidth=0.9, relheight=0.6, anchor="n")

btn_open_file = Button(upper_frame, text="Select Files", command=open_file)
btn_open_file.grid(column=0, row=1)

btn_compile = Button(upper_frame, text="Compile", state=DISABLED, command=compile_csv)
btn_compile.grid(column=1, row=1)

txt_list = Text(lower_frame)
txt_list.place(relwidth=0.9, relheight=0.9)

# scrollbars
hbar=Scrollbar(root, orient=HORIZONTAL)
hbar.pack(side=BOTTOM, fill=X)
hbar.config(command=txt_list.xview)
vbar=Scrollbar(root, orient=VERTICAL)
vbar.pack(side=RIGHT, fill=Y)
vbar.config(command=txt_list.yview)

root.mainloop()