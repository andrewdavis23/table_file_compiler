## Program:
This tool compiles text, Excel, and CSV files containing similar tables into one file.

## Notes:
There was a bug within the pd.read_excel function:  "Workbook contains no default style, apply openpyxl's default." Openpyxl is the engine that reads .xlxs files.  This seems to be working now.

## Future adds:
SQL query window
Append tables on matching column names. exclude excess columns
