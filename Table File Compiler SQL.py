from tkinter import *
from tkinter import filedialog
import pandas as pd
from pandasql import sqldf
import os
from io import StringIO

#initialize sql environment
pysqldf = lambda q: sqldf(q, globals())

# final dataframe, file paths
all_data = pd.DataFrame()
result = pd.DataFrame()
file_directs = []
file_list = ''
headers_bool = True

class theme():
    btn_font = 'bold'
    winbg = 'black'
    btn = 'orange'
    frm = 'gray15'
    txtfg = 'pink'
    txtbg = 'gray12'
    txt = '#44D62C' #neon green
    btntxt = '#4D4DFF' #neon blue
    btnbg = 'gray12'
    btnactbg = 'gray12'
    btnactfnt = '#FFAD00' #neon orange
    scrllbg = 'pink'
    courser = '#D22730'

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
    global headers_bool
    all_data = pd.DataFrame()

    msg = 'Compiled\n'   

    for f in file_directs:
        file_name = f.split('/')[-1]
        file_ext = file_name.split('.')[-1]

        if file_ext == 'txt' : 
            temp_df = pd.read_csv(f, delimiter='\t')
            all_data = all_data.append(temp_df, ignore_index=True)
        elif file_ext == 'xlsx' : 
            temp_df = pd.read_excel(f)
            all_data = all_data.append(temp_df, ignore_index=True)
        elif file_ext == 'csv' : 
            temp_df = pd.read_csv(f)
            all_data = all_data.append(temp_df, ignore_index=True)
        else: msg += '\nError reading {}\n   File extension not .txt, .xlsx or .csv\n'

    if len(query_box.get("1.0", END)) <= 1:
        query_box.insert(END, 'SELECT *\nFROM all_data')
    
    buffer = StringIO()
    all_data.info(buf=buffer)
    msg += '\n'+buffer.getvalue()

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
            btn_export_results['state'] = NORMAL
            btn_clear_SQL['state'] = NORMAL
        else:
            btn_save['state'] = DISABLED
            btn_run_SQL['state'] = DISABLED
            btn_export_results['state'] = DISABLED

    else:
        btn_compile['state'] = DISABLED
        btn_clear['state'] = DISABLED
        btn_save['state'] = DISABLED
        btn_run_SQL['state'] = DISABLED
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
    try:
        result = pysqldf(query)
    except BaseException as em:
        result = em

    result_box.config(state=NORMAL)
    result_box.delete("1.0", END)
    result_box.insert(END, result)
    result_box.config(state=DISABLED)
   
def clear_SQL():
    query_box.delete('1.0', END)

def export_results():
    global result
    fn = filedialog.asksaveasfilename(defaultextension=".xlsx")
    result.to_excel(fn, index=False)
    os.system('start EXCEL.EXE "{}""'.format(fn))

# window
root = Tk()
root.title("Flat File Database Analyzer")
root.geometry('987x610')
root.configure(bg=theme.winbg)
root.attributes('-alpha', 0.90)

compiler_frame = Frame(root, bg=theme.frm, bd=5)
compiler_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

SQL_frame = Frame(root, bg=theme.frm, bd=5)
SQL_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

# SQL (left side)
query_box = Text(SQL_frame, insertbackground=theme.courser, fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt, padx=5, pady=3)
query_box.place(relx=0, rely=0, relwidth=1, relheight=0.4)

SQL_button_frame = Frame(SQL_frame, bg=theme.frm, bd=5)
SQL_button_frame.place(relx=0, rely=0.4, relwidth=1, relheight=0.1)

result_box = Text(SQL_frame, state=DISABLED, fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt, padx=5, pady=3)
result_box.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)

btn_run_SQL = Button(SQL_button_frame, text="Run SQL", state=DISABLED, command=run_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_run_SQL.pack(side='left', expand=True)

btn_clear_SQL = Button(SQL_button_frame, text="Clear SQL", state=DISABLED, command=clear_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_clear_SQL.pack(side='left', expand=True)

btn_export_results = Button(SQL_button_frame, text="Export Output", state=DISABLED, command=export_results, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_export_results.pack(side='left', expand=True)

# compiler (right side)
upper_frame = Frame(compiler_frame, bg=theme.frm, bd=5)
upper_frame.place(relx=0, rely=0, relwidth=1, relheight=0.1)

lower_frame = Frame(compiler_frame, bg=theme.frm, bd=5)
lower_frame.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

btn_open_file = Button(upper_frame, text="Select", command=open_file, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_open_file.pack(side='left', expand=True)

check_header = Checkbutton(upper_frame, text="Contains\nHeaders", variable=headers_bool, onvalue=True, offvalue=False, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
check_header.select()
check_header.pack(side='left')

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