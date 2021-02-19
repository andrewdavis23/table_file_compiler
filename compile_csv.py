# Creates CSV from appended all CSV files in folder
# Andrew Davis - Feb 2021

# Was originally intended to append Excel files, but there is a bug within the pd.read_excel function
# "Workbook contains no default style, apply openpyxl's default"
# Openpyxl is the engine that reads .xlxs files
# Solution was to convert to another Excel file type (one that uses a different engine) or CSV

import pandas as pd
import glob
from time import sleep
from progress.bar import Bar

path = r'C:\Users\nuajd15\Desktop\Alerts_Sep2020_Feb2021\csv'
files = glob.glob(path + "/*.csv")

out_path = r'C:\Users\nuajd15\Desktop\Alerts_Sep2020_Feb2021\csv\output.csv'

all_data = pd.DataFrame()

with Bar('Loading data...',suffix='%(percent).1f%% - %(eta)ds') as bar:
    for f in files:
        temp_df = pd.read_csv(f)
        temp_df = temp_df.loc[temp_df.STORE_NUM==619]
        all_data = all_data.append(temp_df, ignore_index=True)
        bar.next()

print("Creating CSV...")
all_data.to_csv(out_path,index=False)

print("Complete!")