# csv_compiler
This tool compiles a folder of CSV files into a single file.  Query optional.

# Was originally intended to append Excel files, but there is a bug within the pd.read_excel function
# "Workbook contains no default style, apply openpyxl's default"
# Openpyxl is the engine that reads .xlxs files
# Solution was to convert to another Excel file type (one that uses a different engine) or CSV

This uses a module called progressbar2 to display a loading bar, percentage and estimated time for compiling CSV files
