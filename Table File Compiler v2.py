from tkinter import *
from tkinter import filedialog
import pandas as pd
from pandasql import sqldf
import os
from io import StringIO

#initialize sql environment
pysqldf = lambda q: sqldf(q, globals())

# final dataframe, file paths, filename, SQL query directory, query results
all_data = pd.DataFrame()
file_directs = []
file_list = ''
query_file_dir = ''
result = pd.DataFrame()

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

    # add filenames to the GUI list box
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
    all_data = pd.DataFrame()
    msg = ''

    # User selected header boolean and header row number
    if header_bool.get():
        if int(header_bool.get()) <= 0:
            header_rn = 1
        else:
            header_rn = int(header_row.get("1.0", END)) - 1
    else:
        header_rn = None

    # delimiter boolean and delimiter character
    if delim_bool.get():
        delim = delim_char.get("1.0", END)[:-1]
    else:
        delim = '\t'   

    # filename and column count
    file_col_msg = '\n FILES LOADED:'
    col_count = []

    for f in file_directs:
        file_name = f.split('/')[-1]
        file_ext = file_name.split('.')[-1]

        # load, count column, create showing column count, filename, create list of column count
        if file_ext == 'txt' : 
            temp_df = pd.read_csv(f, sep=delim, header=header_rn, engine='python')
            cc = temp_df.shape[1]
            file_col_msg += str(cc) + ' ' + file_name + '\n'
            col_count.append(cc)
            all_data = all_data.append(temp_df, ignore_index=True)
        elif file_ext == 'xlsx' : 
            temp_df = pd.read_excel(f)
            cc = temp_df.shape[1]
            file_col_msg += str(cc) + ' ' + file_name + '\n'
            col_count.append(cc)            
            all_data = all_data.append(temp_df, ignore_index=True)
        elif file_ext == 'csv' : 
            temp_df = pd.read_csv(f, engine='python')
            cc = temp_df.shape[1]
            file_col_msg += str(cc) + ' ' + file_name + '\n'
            col_count.append(cc)            
            all_data = all_data.append(temp_df, ignore_index=True)
        else: msg += '\nError reading {}\n   File extension not .txt, .xlsx or .csv\n'.format(file_name)

    if len(query_box.get("1.0", END)) <= 1:
        query_box.insert(END, 'SELECT *\nFROM all_data a')

    # check that columns are all the same, then list data for message output
    # PLAN: check for matching column names or data types
    all_same = all(x == col_count[0] for x in col_count)
    if not all_same:
        file_col_msg = '** COLUMN COUNT MISMATCH **\n' + file_col_msg
    
    # buf:  writable buffer, defaults to sys.stdout
    buffer = StringIO()
    all_data.info(buf=buffer)
    msg += '\n'+buffer.getvalue()

    msg += file_col_msg

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
        
    if header_bool.get():
        header_row.config(state = NORMAL, fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt)
        header_row_label.config(fg=theme.btntxt)
    else:
        header_row.config(state = DISABLED, fg='black', bg='black', foreground='black')
        header_row_label.config(fg='gray12')

    if delim_bool.get():
        delim_char.config(state = NORMAL, fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt)
    else:
        delim_char.config(state = DISABLED, fg='black', bg='black', foreground='black')

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

    try:
        query = query_box.selection_get()
    except:
        query = query_box.get("1.0", END)

    try:
        result = pysqldf(query)
    except BaseException as em:
        result = em

    result_box.config(state=NORMAL)
    result_box.delete("1.0", END)
    result_box.insert(END, result)
    result_box.config(state=DISABLED)
   
def load_SQL():
    global query_file_dir
    clear_SQL()
    query_file_dir = filedialog.askopenfilename(initialdir=r"C:\Python Programs\Table Compiler\SQLite Queries")
    query_file_label['text'] = query_file_dir

    with open(query_file_dir, "r") as myfile:
        query=myfile.read()

    btn_save_as_SQL['state'] = NORMAL

    query_box.insert(END, query)

def save_SQL():
    global query_file_dir

    try:
        query = query_box.selection_get()
    except:
        query = query_box.get("1.0", END)

    if query_file_dir == '':
        save_as_SQL()
    else:
        with open(query_file_dir, 'w') as output_file:
            output_file.write(query)

def save_as_SQL():
    try:
        query = query_box.selection_get()
    except:
        query = query_box.get("1.0", END)
    
    new_save = filedialog.asksaveasfile(defaultextension='.txt')
    query_file_label['text'] = new_save.name

    try:
        new_save.write(query.rstrip())
    except:
        pass

def clear_SQL():
    query_box.delete('1.0', END)
    query_file_label['text']=''

def export_results():
    global result
    fn = filedialog.asksaveasfilename(defaultextension=".xlsx")
    result.to_excel(fn, index=False)
    os.system('start EXCEL.EXE "{}""'.format(fn))

# window
root = Tk()
root.title("Flat File Database Analyzer")
root.geometry('1200x600')
root.configure(bg=theme.winbg)
root.attributes('-alpha', 0.90)

compiler_frame = Frame(root, bg=theme.frm, bd=5)
compiler_frame.place(relx=0.55, rely=0, relwidth=0.45, relheight=1)

SQL_frame = Frame(root, bg=theme.frm, bd=5)
SQL_frame.place(relx=0, rely=0, relwidth=0.55, relheight=1)

# SQL (left side)
query_file_label = Label(SQL_frame, text='', anchor='w', fg=theme.btntxt, bg=theme.btnbg, foreground=theme.btntxt)
query_file_label.place(relx=0, rely=0, relwidth=1, relheight=0.03)

query_box = Text(SQL_frame, insertbackground=theme.courser, fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt, padx=5, pady=3)
query_box.place(relx=0, rely=0.03, relwidth=1, relheight=0.37)

SQL_button_frame = Frame(SQL_frame, bg=theme.frm, bd=5)
SQL_button_frame.place(relx=0, rely=0.4, relwidth=1, relheight=0.1)

result_box = Text(SQL_frame, state=DISABLED, wrap='none', fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt, padx=5, pady=3)
result_box.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)

btn_run_SQL = Button(SQL_button_frame, text="Run SQL", state=DISABLED, command=run_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_run_SQL.pack(side='left', expand=True)

btn_load_SQL = Button(SQL_button_frame, text="Load", state=NORMAL, command=load_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_load_SQL.pack(side='left', expand=True)

btn_save_SQL = Button(SQL_button_frame, text="Save", state=NORMAL, command=save_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_save_SQL.pack(side='left', expand=True)

btn_save_as_SQL = Button(SQL_button_frame, text="Save As", state=DISABLED, command=save_as_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_save_as_SQL.pack(side='left', expand=True)

btn_clear_SQL = Button(SQL_button_frame, text="Clear SQL", state=NORMAL, command=clear_SQL, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_clear_SQL.pack(side='left', expand=True)

btn_export_results = Button(SQL_button_frame, text="Export Results", state=DISABLED, command=export_results, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_export_results.pack(side='left', expand=True)

# compiler (right side)
upper_frame = Frame(compiler_frame, bg=theme.frm, bd=5)
upper_frame.place(relx=0, rely=0, relwidth=1, relheight=0.13)

lower_frame = Frame(compiler_frame, bg=theme.frm, bd=5)
lower_frame.place(relx=0, rely=0.13, relwidth=1, relheight=0.87)

btn_open_file = Button(upper_frame, text="Select", command=open_file, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_open_file.pack(side='left', expand=True)

header_frame = Frame(upper_frame, bg=theme.btnbg, bd=5)
header_frame.pack(side='left', expand=True)

header_bool = BooleanVar()
header_check = Checkbutton(header_frame, text="Header", variable=header_bool, command=check_ready, onvalue=True, offvalue=False, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
header_check.select()
header_check.pack(side='top')

header_row_frame = Frame(header_frame, bg=theme.btnbg)
header_row_frame.pack(side='bottom')

header_row_label = Label(header_row_frame, text = 'Row:', fg=theme.btntxt, bg=theme.btnbg, foreground=theme.btntxt)
header_row_label.pack(side='left')

header_row = Text(header_row_frame, insertbackground=theme.courser, height=1, width=2, fg=theme.txtfg, bg=theme.txtbg, foreground=theme.txt)
header_row.pack(side='left')
header_row.insert(END, '1')

delim_frame = Frame(upper_frame, bg=theme.btnbg, bd=5)
delim_frame.pack(side='left')

delim_bool = BooleanVar()
delim_check = Checkbutton(delim_frame, text="Delim.", variable=delim_bool, command=check_ready, onvalue=True, offvalue=False, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
delim_check.pack(side='top')

delim_char = Text(delim_frame, height=1, width=2, insertbackground=theme.courser, fg='black', bg='black', foreground='black')
delim_char.pack(side='bottom')

btn_compile = Button(upper_frame, text="Compile", state=DISABLED, command=compile, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_compile.pack(side='left', expand=True)

btn_save = Button(upper_frame, text="Save", state=DISABLED, command=save_file, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_save.pack(side='left', expand=True)

btn_clear = Button(upper_frame, text="Clear", state=DISABLED, command=clear_files, bg=theme.btnbg, fg=theme.btntxt, font=theme.btn_font, activebackground=theme.btnactbg, activeforeground=theme.btnactfnt)
btn_clear.pack(side='left', expand=True)

txt_list = Text(lower_frame, bg=theme.txtbg)
txt_list.pack(expand=True, fill='both')

# # scrollbars
# hbar=Scrollbar(result_box, orient=HORIZONTAL, bg=theme.scrllbg)
# hbar.pack(side=BOTTOM, fill=X)
# hbar.config(command=txt_list.xview)
# vbar=Scrollbar(result_box, orient=VERTICAL, bg=theme.scrllbg)
# vbar.pack(side=RIGHT, fill=Y)
# vbar.config(command=txt_list.yview)

root.mainloop()
