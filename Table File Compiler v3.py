from tkinter import filedialog
from tkinter import Text
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import pandas as pd
from pandasql import sqldf
import os
from io import StringIO
import re

about_str = """
Flat File Database Analyzer
Version 3
Created by Andrew
https://github.com/andrewdavis23/table_file_compiler
"""

instructions_str = """
This is a Flat File Database Analyzer.
Use the left side to write SQL queries and the right side to compile flat files.
Select files using the "Select" button.
You can choose to include headers and specify a delimiter.
Compile the files by clicking the "Compile" button.
Once compiled, you can run SQL queries on the data.
You can save the compiled data to a file or export the results of your SQL queries.
"""

#initialize sql environment
pysqldf = lambda q: sqldf(q, globals())

# final dataframe, file paths, filename, SQL query directory, query results
all_data = pd.DataFrame()
file_directs = []
file_list = ''
query_file_dir = ''
result = pd.DataFrame()

# from oracle sql docs
SQL_KEYWORDS = {
    'ABORT','ACTION','ADD','AFTER','ALL','ALTER','ALWAYS','ANALYZE','AND','AS','ASC','ATTACH',
    'AUTOINCREMENT','BEFORE','BEGIN','BETWEEN','BY','CASCADE','CASE','CAST','CHECK','COLLATE',
    'COLUMN','COMMIT','CONFLICT','CONSTRAINT','CREATE','CROSS','CURRENT','CURRENT_DATE',
    'CURRENT_TIME','CURRENT_TIMESTAMP','DATABASE','DEFAULT','DEFERRABLE','DEFERRED','DELETE',
    'DESC','DETACH','DISTINCT','DO','DROP','EACH','ELSE','END','ESCAPE','EXCEPT','EXCLUDE',
    'EXCLUSIVE','EXISTS','EXPLAIN','FAIL','FILTER','FIRST','FOLLOWING','FOR','FOREIGN','FROM',
    'FULL','GENERATED','GLOB','GROUP','GROUPS','HAVING','IF','IGNORE','IMMEDIATE','IN','INDEX',
    'INDEXED','INITIALLY','INNER','INSERT','INSTEAD','INTERSECT','INTO','IS','ISNULL','JOIN',
    'KEY','LAST','LEFT','LIKE','LIMIT','MATCH','MATERIALIZED','NATURAL','NO','NOT','NOTHING',
    'NOTNULL','NULL','NULLS','OF','OFFSET','ON','OR','ORDER','OTHERS','OUTER','OVER','PARTITION',
    'PLAN','PRAGMA','PRECEDING','PRIMARY','QUERY','RAISE','RANGE','RECURSIVE','REFERENCES',
    'REGEXP','REINDEX','RELEASE','RENAME','REPLACE','RESTRICT','RETURNING','RIGHT','ROLLBACK',
    'ROW','ROWS','SAVEPOINT','SELECT','SET','TABLE','TEMP','TEMPORARY','THEN','TIES','TO',
    'TRANSACTION','TRIGGER','UNBOUNDED','UNION','UNIQUE','UPDATE','USING','VACUUM','VALUES',
    'VIEW','VIRTUAL','WHEN','WHERE','WINDOW','WITH','WITHOUT'
}

SQL_DATATYPES = {'INTEGER', 'REAL', 'TEXT', 'BLOB', 'NULL'}

SQL_SYSTEM_TABLES = {'SQLITE_MASTER'}

SQL_FUNCTIONS = {
    'ABS','CHANGES','CHAR','COALESCE','CONCAT','CONCAT_WS','FORMAT','GLOB','HEX','IF','IFNULL',
    'IIF','INSTR','LAST_INSERT_ROWID','LENGTH','LIKE','LIKE','LIKELIHOOD','LIKELY','LOAD_EXTENSION',
    'LOAD_EXTENSION','LOWER','LTRIM','LTRIM','MAX','MIN','NULLIF','OCTET_LENGTH','PRINTF','QUOTE',
    'RANDOM','RANDOMBLOB','REPLACE','ROUND','ROUND','RTRIM','RTRIM','SIGN','SOUNDEX',
    'SQLITE_COMPILEOPTION_GET','SQLITE_COMPILEOPTION_USED','SQLITE_OFFSET','SQLITE_SOURCE_ID',
    'SQLITE_VERSION','SUBSTR','SUBSTR','SUBSTRING','SUBSTRING','TOTAL_CHANGES','TRIM','TRIM',
    'TYPEOF','UNHEX','UNHEX','UNICODE','UNISTR','UNISTR_QUOTE','UNLIKELY','UPPER','ZEROBLOB',
    'AVG','COUNT','COUNT','GROUP_CONCAT','GROUP_CONCAT','MAX','MIN','STRING_AGG','SUM','TOTAL',
    'DATE','TIME','DATETIME','JULIANDAY','UNIXEPOCH','STRFTIME','DATETIME',
}

dark_theme_colors = {
    "keyword": "#CC7832",
    "function": "#FFC66D",
    "string": "#96CC00",
    "comment": "#339966",
    "number": "#6897BB",
    "datatype": "#9876AA",
    "system": "#A9B7C6"
}

light_theme_colors = {
    "keyword": "#0000FF",
    "function": "#009B37",
    "string": "#FF0000",
    "comment": "#808080",
    "number": "#FF00FF",
    "datatype": "#8000FF",
    "system": "#009B37"
}

def highlight_sql(text_widget):
    text = text_widget.get("1.0", "end-1c")

    def is_in_comment(pos):
        return any(start <= pos < end for start, end in comment_spans)

    # Clear existing tags
    for tag in ['keyword', 'string', 'comment', 'number', 'datatype', 'system', 'function']:
        text_widget.tag_remove(tag, "1.0", "end")

    # Match SQL comments
    comment_spans = []
    comment_pattern = re.compile(r'--.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE) #re.DOTALL allows . to match newlines
    for match in comment_pattern.finditer(text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("comment", start, end)
        comment_spans.append((match.start(), match.end()))

    # Match single-quoted strings
    for match in re.finditer(r"'(?:''|[^'])*'", text):
        if is_in_comment(match.start()):
            continue
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("string", start, end)

    # Match numeric literals (integers, decimals, negatives)
    for match in re.finditer(r'\b-?\d+(\.\d+)?\b', text):
        if is_in_comment(match.start()):
            continue
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("number", start, end)

    # Match keywords
    for match in re.finditer(r'\b\w+\b', text):
        if is_in_comment(match.start()):
            continue
        word = match.group(0).upper()
        if word in SQL_KEYWORDS:
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("keyword", start, end)

    # Match function names followed by (
    for match in re.finditer(r'\b\w+\b(?=\s*\()', text):
        if is_in_comment(match.start()):
            continue
        word = match.group(0).upper()
        if word in SQL_FUNCTIONS:
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("function", start, end)

    # Match data types
    for match in re.finditer(r'\b\w+\b', text):
        if is_in_comment(match.start()):
            continue
        word = match.group(0).upper()
        if word in SQL_DATATYPES:
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("datatype", start, end)

    # Match system table names
    for match in re.finditer(r'\b\w+\b', text):
        if is_in_comment(match.start()):
            continue
        word = match.group(0).upper()
        if word in SQL_SYSTEM_TABLES:
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("system", start, end)

def apply_syntax_colors(theme_name):
    colors = dark_theme_colors if theme_name == "darkly" else light_theme_colors
    for tag, color in colors.items():
        query_box.tag_configure(tag, foreground=color)

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
      
    txt_list.config(state=NORMAL)
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
    try:
        if header_bool.get():
            value = header_row.get().strip()
            header_rn = int(value) - 1 if value else 0
        else:
            header_rn = None
    except ValueError:
        header_rn = 0  # Default to first row if invalid input

    # delimiter boolean and delimiter character
    if delim_bool.get():
        delim = delim_char.get("1.0", END)[:-1]
    else:
        delim = '\t'   

    # filename and column count
    file_col_msg = '\n FILES LOADED (col count / filename):\n'
    col_count = [] # for checking that all files have the same number of columns

    for f in file_directs:
        file_name = f.split('/')[-1]
        file_ext = file_name.split('.')[-1]

        # load, count column, create showing column count, filename, create list of column count
        if file_ext == 'txt' : 
            temp_df = pd.read_csv(f, sep=delim, header=header_rn, engine='python', encoding='ISO-8859-1')
            cc = temp_df.shape[1]
            file_col_msg += str(cc) + ' ' + file_name + '\n'
            col_count.append(cc)
            temp_df['filename'] = file_name  # Add filename column
            all_data = pd.concat([all_data, temp_df], ignore_index=True)
        elif file_ext == 'xlsx' : 
            temp_df = pd.read_excel(f, header=header_rn)
            cc = temp_df.shape[1]
            file_col_msg += str(cc) + ' ' + file_name + '\n'
            col_count.append(cc)
            temp_df['filename'] = file_name            
            all_data = pd.concat([all_data, temp_df], ignore_index=True)
        elif file_ext == 'csv' : 
            temp_df = pd.read_csv(f, header=header_rn, engine='python', encoding='ISO-8859-1')
            cc = temp_df.shape[1]
            file_col_msg += str(cc) + ' ' + file_name + '\n'
            col_count.append(cc)    
            temp_df['filename'] = file_name        
            all_data = pd.concat([all_data, temp_df], ignore_index=True)
        else: msg += '\nError reading {}\n   File extension not .txt, .xlsx or .csv\n'.format(file_name)

    if len(query_box.get("1.0", END)) <= 1:
        query_box.insert(END, 'SELECT *\nFROM all_data a')

    highlight_sql(query_box)

    # check that columns are all the same, then list data for message output
    # PLAN: check for matching column names or data types
    all_same = all(x == col_count[0] for x in col_count)
    if not all_same:
        file_col_msg = '** COLUMN COUNT MISMATCH **\n' + file_col_msg
    
    # buf:  writable buffer, defaults to sys.stdout
    buffer = StringIO()
    all_data.info(buf=buffer)
    msg += buffer.getvalue()

    msg += file_col_msg

    check_ready()

    txt_list.config(state=NORMAL)
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
        header_row.config(state = NORMAL)
    else:
        header_row.config(state = DISABLED)

    if delim_bool.get():
        delim_char.config(state = NORMAL)
    else:
        delim_char.config(state = DISABLED)

def save_file():
    global all_data

    out_path = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    if out_path is None:
        return
    all_data.to_csv(out_path, index=False, lineterminator='\n', sep='\t')
    out_path.close()

def run_SQL():
    global all_data, result

    try:
        query = query_box.selection_get()
    except:
        query = query_box.get("1.0", END)

    try:
        result = pysqldf(query)
    except BaseException as em:
        result = pd.DataFrame([{"Error": str(em)}])

    # Clear previous content
    result_table.delete(*result_table.get_children())
    result_table["columns"] = list(result.columns)

    # Setup headers
    for col in result.columns:
        result_table.heading(col, text=col)
        result_table.column(col, width=100, anchor='w')

    # Insert data
    for _, row in result.iterrows():
        result_table.insert("", "end", values=list(row))
   
def load_SQL():
    global query_file_dir
    clear_SQL()
    query_file_dir = filedialog.askopenfilename(initialdir=r"C:\Python Programs\Table Compiler\SQLite Queries")

    with open(query_file_dir, "r") as myfile:
        query=myfile.read()

    query_box.insert(END, query)

    highlight_sql(query_box)

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
    # query_file_label['text'] = new_save.name

    try:
        new_save.write(query.rstrip())
    except:
        pass

def clear_SQL():
    query_box.delete('1.0', END)
    # query_file_label['text']=''

def export_results():
    global result
    fn = filedialog.asksaveasfilename(defaultextension=".xlsx")
    result.to_excel(fn, index=False)
    os.system('start EXCEL.EXE "{}""'.format(fn))

def load_theme():
    try:
        with open("theme_config.txt", "r") as f:
            theme = f.read().strip()
            if theme in ["darkly", "yeti"]:
                return theme
    except:
        pass
    return "darkly"  # default if not found or corrupted

def toggle_theme():
    if current_theme["name"] == "darkly":
        root.style.theme_use("yeti")
        current_theme["name"] = "yeti"
    else:
        root.style.theme_use("darkly")
        current_theme["name"] = "darkly"

    apply_syntax_colors(current_theme["name"])

    with open("theme_config.txt", "w") as f:
        f.write(current_theme["name"])

#---------------------#
#        window       #
#---------------------#

current_theme = {'name': load_theme()}

root = tb.Window(themename=current_theme['name'])
root.title("Flat File Database Analyzer")
root.geometry("1400x800")
root.state('zoomed')  # Maximizes the window

# file menu
menu = tb.Menu(root)
root.config(menu=menu)
file_menu = tb.Menu(menu, tearoff=0)
options_menu = tb.Menu(menu, tearoff=0)
help_menu = tb.Menu(menu, tearoff=0)
menu.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label="Load SQL", command=load_SQL)
file_menu.add_command(label="Save SQL", command=save_SQL)
file_menu.add_command(label="Save As SQL", command=save_as_SQL)
file_menu.add_command(label="Clear SQL", command=clear_SQL)
file_menu.add_separator()
file_menu.add_command(label='Exit', command=root.quit)
menu.add_cascade(label='Options', menu=options_menu)
options_menu.add_command(label='Toggle Theme', command=toggle_theme)
menu.add_cascade(label='Help', menu=help_menu)
help_menu.add_command(label='About', command=lambda: messagebox.showinfo("About",about_str))
help_menu.add_separator()
help_menu.add_command(label='Instructions', command=lambda: messagebox.showinfo("Instructions",instructions_str))

# right side
compiler_frame = tb.Frame(root, bootstyle=SECONDARY)
compiler_frame.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)

# left side
SQL_frame = tb.Frame(root, bootstyle=PRIMARY)
SQL_frame.place(relx=0, rely=0, relwidth=0.7, relheight=1)

#---------------------#
#   SQL (left side)   #
#---------------------#

query_box = Text(SQL_frame, wrap='word', font=("Consolas", 12), padx=5, pady=3)
query_box.place(relx=0, rely=0, relwidth=1, relheight=0.4)

apply_syntax_colors(current_theme["name"])

SQL_button_frame = tb.Frame(SQL_frame, bootstyle=SECONDARY)
SQL_button_frame.place(relx=0, rely=0.4, relwidth=1, relheight=0.1)

# RESULTS TABLE WITH SCROLLBARS
result_frame = tb.Frame(SQL_frame)
result_frame.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)

result_table = tb.Treeview(result_frame, show='headings')

result_scrollbar = tb.Scrollbar(result_frame, orient='vertical', command=result_table.yview)
result_scrollbar.pack(side='right', fill='y')

h_scroll = tb.Scrollbar(result_frame, orient='horizontal', command=result_table.xview)
h_scroll.pack(side='bottom', fill='x')

result_table.configure(yscrollcommand=result_scrollbar.set, xscrollcommand=h_scroll.set)

result_table.pack(side='left', fill='both', expand=True)

btn_run_SQL = tb.Button(SQL_button_frame, text="Run SQL", state=DISABLED, command=run_SQL, bootstyle=PRIMARY)
btn_run_SQL.pack(side='left', expand=True)

btn_export_results = tb.Button(SQL_button_frame, text="Export Results", state=DISABLED, command=export_results, bootstyle=PRIMARY)
btn_export_results.pack(side='left', expand=True)

#-----------------------#
# compiler (right side) #
#-----------------------#

# frames
upper_frame = tb.Frame(compiler_frame, bootstyle=SECONDARY)
upper_frame.place(relx=0, rely=0, relwidth=1, relheight=0.13)

lower_frame = tb.Frame(compiler_frame, bootstyle=PRIMARY)
lower_frame.place(relx=0, rely=0.13, relwidth=1, relheight=0.87)

# upper frame (controls)
btn_open_file = tb.Button(upper_frame, text="Select", command=open_file, bootstyle=PRIMARY)
btn_open_file.pack(side='left', expand=True)

header_frame = tb.Frame(upper_frame, bootstyle=PRIMARY)
header_frame.pack(side='left', expand=True)

header_bool = tb.BooleanVar(value=True)
header_check = tb.Checkbutton(header_frame, text="Header", variable=header_bool, command=check_ready, bootstyle=SUCCESS)
header_check.pack(side='top')

header_row_frame = tb.Frame(header_frame, bootstyle=SECONDARY)
header_row_frame.pack(side='bottom')

header_row_label = tb.Label(header_row_frame, text = 'Row:', bootstyle=SUCCESS)
header_row_label.pack(side='left')

header_row = tb.Entry(header_row_frame, bootstyle=SUCCESS, width=3)
header_row.pack(side='left')
header_row.insert(END, '1')

delim_frame = tb.Frame(upper_frame, bootstyle=SECONDARY)
delim_frame.pack(side='left')

delim_bool = tb.BooleanVar()
delim_check = tb.Checkbutton(delim_frame, text="Delim.", variable=delim_bool, command=check_ready, onvalue=True, offvalue=False, bootstyle=SUCCESS)
delim_check.pack(side='top')

delim_char = tb.Entry(delim_frame, bootstyle=SUCCESS, width=3)
delim_char.pack(side='bottom')

btn_compile = tb.Button(upper_frame, text="Compile", state=DISABLED, command=compile, bootstyle=PRIMARY)
btn_compile.pack(side='left', expand=True)

btn_save = tb.Button(upper_frame, text="Save", state=DISABLED, command=save_file, bootstyle=PRIMARY)
btn_save.pack(side='left', expand=True)

btn_clear = tb.Button(upper_frame, text="Clear", state=DISABLED, command=clear_files, bootstyle=PRIMARY)
btn_clear.pack(side='left', expand=True)

scrollbar = tb.Scrollbar(lower_frame, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)

txt_list = Text(lower_frame, yscrollcommand=scrollbar.set)
txt_list.pack(side=LEFT, expand=True, fill='both')

scrollbar.config(command=txt_list.yview)

# Reevaluates SQL highlighting while typing
query_box.bind("<KeyRelease>", lambda e: highlight_sql(query_box))

root.mainloop()
