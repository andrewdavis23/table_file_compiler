## Program:
This tool compiles text, Excel, and CSV files containing similar tables into one file.

## Versions:
1: Basic compilier: open, compile, export compilation
2: Run SQLite Lite on compilation, choice to export SQL results or compilation
3: Replaced tkinter with ttkbootstrap GUI

## Notes:
There was a bug within the pd.read_excel function:  "Workbook contains no default style, apply openpyxl's default." Openpyxl is the engine that reads .xlxs files.  This seems to be working now.

## Future adds:
Append tables on matching column names. exclude excess columns
