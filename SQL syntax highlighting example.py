import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
import re

# --- SQL syntax categories ---
SQL_KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL',
    'ON', 'GROUP', 'BY', 'ORDER', 'HAVING', 'INSERT', 'INTO', 'VALUES',
    'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE', 'DROP', 'AND', 'OR',
    'NOT', 'AS', 'IN', 'IS', 'NULL', 'DISTINCT', 'LIMIT', 'OFFSET', 'UNION',
    'ALL', 'LIKE', 'BETWEEN', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'ASC', 'DESC',
    'EXISTS', 'ANY', 'SOME', 'ALL', 'WITH', 'WITHIN', 'OVER', 'PARTITION', 'RANGE', 'ROWS', 'UNBOUNDED', 'CURRENT'
}

SQL_DATATYPES = {
    'INT', 'INTEGER', 'SMALLINT', 'BIGINT',
    'DECIMAL', 'NUMERIC', 'FLOAT', 'REAL', 'DOUBLE',
    'DATE', 'TIME', 'TIMESTAMP', 'CHAR', 'VARCHAR',
    'TEXT', 'BLOB', 'BOOLEAN'
}

SQL_SYSTEM_TABLES = {
    'INFORMATION_SCHEMA', 'SYS', 'PG_CATALOG', 'MYSQL', 'SQLITE_MASTER',
    'DUAL', 'SYSIBM', 'SYSFUN', 'SYSPROC', 'SYSSTAT'
}

SQL_FUNCTIONS = {
    # Aggregate functions
    'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'STDEV', 'VAR', 'GROUP_CONCAT',
    # String functions
    'CONCAT', 'SUBSTRING', 'TRIM', 'UPPER', 'LOWER', 'REPLACE',
    'LEFT', 'RIGHT', 'LENGTH', 'CHAR_LENGTH', 'ASCII', 'CHARINDEX',
    # Date and time functions
    'DATE_FORMAT', 'STR_TO_DATE', 'DATEPART', 'DATEDIFF', 'DATEADD',
    'EXTRACT', 'FORMAT', 'NOW', 'CURDATE', 'CURTIME',
    # Mathematical functions
    'ABS', 'CEIL', 'FLOOR', 'ROUND', 'POWER',
    'SQRT', 'RAND', 'LOG', 'EXP', 'SIGN',
    # Conditional functions
    'IF', 'CASE', 'COALESCE', 'NULLIF', 'ISNULL',
    # Window functions
    'ROW_NUMBER', 'RANK', 'DENSE_RANK', 'NTILE', 'LEAD', 'LAG',
    # System functions
    'GETDATE', 'CURRENT_TIMESTAMP', 'SYSDATE', 'NOW', 'ISNULL', 'COALESCE',
    'NEWID', 'CURRENT_DATE', 'CURRENT_TIME', 'DATEADD', 'DATEDIFF',
    'ROW_NUMBER', 'RANK', 'PARTITION', 'NTILE', 'LAG', 'LEAD'
}

def highlight_sql(text_widget):
    text = text_widget.get("1.0", "end-1c")

    # Clear existing tags
    for tag in ['keyword', 'string', 'comment', 'number', 'datatype', 'system', 'function']:
        text_widget.tag_remove(tag, "1.0", "end")

    # Match SQL comments
    for match in re.finditer(r'(?:--|//).*$', text, re.MULTILINE):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("comment", start, end)

    # Match single-quoted strings
    for match in re.finditer(r"'(?:''|[^'])*'", text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("string", start, end)

    # Match numeric literals (integers, decimals, negatives)
    for match in re.finditer(r'\b-?\d+(\.\d+)?\b', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("number", start, end)

    # Match keywords
    for match in re.finditer(r'\b\w+\b', text):
        word = match.group(0).upper()
        if word in SQL_KEYWORDS:
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("keyword", start, end)

    # Match function names followed by (
    for match in re.finditer(r'\b\w+\b(?=\s*\()', text):
        word = match.group(0).upper()
        if word in SQL_FUNCTIONS:
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("function", start, end)

    # Match data types
    for match in re.finditer(r'\b\w+\b', text):
        word = match.group(0).upper()
        if word in SQL_DATATYPES:
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("datatype", start, end)

    # Match system table names
    for match in re.finditer(r'\b\w+\b', text):
        word = match.group(0).upper()
        if word in SQL_SYSTEM_TABLES:
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("system", start, end)

# --- GUI setup ---
root = tb.Window(themename="darkly")
root.title("Manual SQL Highlighter")
root.geometry("800x500")

sql_box = tk.Text(root, wrap="word", font=("Consolas", 12), padx=5, pady=5)
sql_box.pack(fill="both", expand=True, padx=10, pady=10)

# Configure tag colors
sql_box.tag_configure("keyword", foreground="#CC7832")
sql_box.tag_configure("function", foreground="#FFC66D")
sql_box.tag_configure("string", foreground="#96CC00")
sql_box.tag_configure("comment", foreground="#339966")
sql_box.tag_configure("number", foreground="#6897BB")
sql_box.tag_configure("datatype", foreground="#9876AA")
sql_box.tag_configure("system", foreground="#A9B7C6")

# Example SQL
qry1 = """
-- Example 1
SELECT name, CAST(age as INT), LEFT(name, 1) AS initial
FROM users
LEFT JOIN orders ON users.id = orders.user_id
WHERE age > 21
AND name LIKE 'A%'
ORDER BY age DESC;
"""

qry2 = """
// Example 2
SELECT table_name, COUNT(*)
FROM information_schema.columns
"""
sql_box.insert("1.0", qry1 + "\n" + qry2)
highlight_sql(sql_box)

# Bind key event
sql_box.bind("<KeyRelease>", lambda e: highlight_sql(sql_box))

root.mainloop()
