from tkinter import *
from tkinter import filedialog
import pandas as pd
from pandasql import sqldf
import os

#initialize sql environment
pysqldf = lambda q: sqldf(q, globals())

# final dataframe, file paths
all_data = pd.DataFrame()
result = pd.DataFrame()
file_directs = []
file_list = ''

color_mode = 1

class theme():
    btn_font = 'bold'
    winbg = 'black'
    btn = 'orange'
    frm = 'gray15'
    txtfg = 'pink'
    txtbg = 'gray6'
    txt = '#44D62C' #neon green
    btntxt = '#4D4DFF' #neon blue
    btnbg = 'gray12'
    btnactbg = 'gray12'
    btnactfnt = '#FFAD00' #neon orange
    scrllbg = 'pink'

# select files and display file names in window
def open_file():
    global file_directs
    global file_list

    new_files = list(filedialog.askopenfilenames())
    file_directs.extend(new_files)

    # add filenames to the tk list box
    for i in new_files:
        fl = i.split('/')[-1] + '\n'
        file_list += fl
      
    txt_list.config(state=NORMAL, fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt)
    txt_list.delete('1.0', END)
    txt_list.insert(END, file_list)
    txt_list.config(state=DISABLED)

    # activate compile button
    check_ready()

def clear_files():
    global file_directs
    global file_list
    global all_data

    file_directs = []
    file_list = ''
    all_data = pd.DataFrame()

    txt_list.config(state=NORMAL)
    txt_list.delete('1.0', END)
    txt_list.config(state=DISABLED)

    check_ready()

def compile():
    # plan: make it append on matching column names. exclude excess columns
    global file_directs
    global all_data
    msg = 'Compiled\n'   

    for f in file_directs:
        file_name = f.split('/')[-1]
        file_ext = file_name.split('.')[-1]

        if file_ext == 'txt' : 
            temp_df = pd.read_csv(f, delimiter='\t')
            s = temp_df.shape
            msg += '{}\n  {} rows    {} cols\n'.format(file_name,s[0],s[1])
        elif file_ext == 'xlsx' : 
            temp_df = pd.read_excel(f)
            s = temp_df.shape
            msg += '{}\n  {} rows    {} cols\n'.format(file_name,s[0],s[1])
        elif file_ext == 'csv' : 
            temp_df = pd.read_csv(f)
            s = temp_df.shape
            msg += '{}\n  {} rows    {} cols\n'.format(file_name,s[0],s[1])
        else: msg += '\nError reading {}\n   File extension not .txt, .xlsx or .csv'

        all_data = all_data.append(temp_df, ignore_index=True)

    if len(query_box.get("1.0", END)) <= 1:
        query_box.insert(END, 'SELECT *\nFROM all_data')
    
    ads = all_data.shape
    msg += 'Compilation\n   {} rows    {} cols\n'.format(ads[0],ads[1])

    check_ready()

    txt_list.config(state=NORMAL, fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt)
    txt_list.delete('1.0', END)
    txt_list.insert(END, msg)
    txt_list.config(state=DISABLED)

def check_ready():
    global file_directs
    global all_data

    if len(file_directs) > 0:
        btn_compile['state'] = NORMAL
        btn_clear['state'] = NORMAL
        if all_data.shape[0] > 0:
            btn_save['state'] = NORMAL
            btn_run_SQL['state'] = NORMAL
            btn_clear_SQL['state'] = NORMAL
            btn_export_results['state'] = NORMAL
        else:
            btn_save['state'] = DISABLED
            btn_run_SQL['state'] = DISABLED
            btn_clear_SQL['state'] = DISABLED
            btn_export_results['state'] = DISABLED

    else:
        btn_compile['state'] = DISABLED
        btn_clear['state'] = DISABLED
        btn_save['state'] = DISABLED
        btn_run_SQL['state'] = DISABLED
        btn_clear_SQL['state'] = DISABLED
        btn_export_results['state'] = DISABLED

def save_file():
    global all_data

    out_path = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    if out_path is None:
        return
    all_data.to_csv(out_path, index=False, line_terminator='\n', sep='\t')
    out_path.close()

def run_SQL():
    global all_data
    global result

    query = query_box.get("1.0", END)
    result = pysqldf(query)

    result_box.insert(END, result)
   
def clear_SQL():
    query_box.config(state=NORMAL)
    query_box.delete('1.0', END)
    query_box.config(state=DISABLED)

def export_results():
    global result
    fn = filedialog.asksaveasfilename(defaultextension=".xlsx")
    result.to_excel(fn, index=False)
    os.system('start EXCEL.EXE "{}""'.format(fn))

# window
root = Tk()
root.title("Flat File Database Analyzer")
root.geometry('700x377')
root.configure(bg=theme.winbg)
root.attributes('-alpha', 0.90)

compiler_frame = Frame(root, bg='red', bd=5)
compiler_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# SQL
SQL_frame = Frame(root, bg='blue', bd=5)
SQL_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

query_box = Text(SQL_frame, padx=5, pady=3)
query_box.place(relx=0, rely=0, relwidth=1, relheight=0.4)

SQL_button_frame = Frame(SQL_frame, bg='green', bd=5)
SQL_button_frame.place(relx=0, rely=0.4, relwidth=1, relheight=0.1)

result_box = Text(SQL_frame, padx=5, pady=3)
result_box.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)

btn_run_SQL = Button(SQL_button_frame, text="Run", state=DISABLED, command=run_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_run_SQL.pack(side='left', expand=True)

btn_clear_SQL = Button(SQL_button_frame, text="Clear", state=DISABLED, command=clear_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_clear_SQL.pack(side='left', expand=True)

btn_export_results = Button(SQL_button_frame, text="Export", state=DISABLED, command=export_results, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_export_results.pack(side='left', expand=True)

# compiler
upper_frame = Frame(compiler_frame, bg=theme.frm, bd=5)
upper_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

lower_frame = Frame(compiler_frame, bg=theme.frm, bd=5)
lower_frame.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)

btn_open_file = Button(upper_frame, text="Select", command=open_file, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_open_file.pack(side='left', expand=True)

btn_compile = Button(upper_frame, text="Compile", state=DISABLED, command=compile, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_compile.pack(side='left', expand=True)

btn_save = Button(upper_frame, text="Save", state=DISABLED, command=save_file, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_save.pack(side='left', expand=True)

btn_clear = Button(upper_frame, text="Clear", state=DISABLED, command=clear_files, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_clear.pack(side='left', expand=True)

txt_list = Text(lower_frame, bg=theme.txtbg)
txt_list.pack(expand=True, fill='both')

# # scrollbars
# hbar=Scrollbar(root, orient=HORIZONTAL, bg=theme.scrllbg)
# hbar.pack(side=BOTTOM, fill=X)
# hbar.config(command=txt_list.xview)
# vbar=Scrollbar(root, orient=VERTICAL, bg=theme.scrllbg)
# vbar.pack(side=RIGHT, fill=Y)
# vbar.config(command=txt_list.yview)

root.mainloop()