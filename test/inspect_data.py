import pandas as pd
import glob
import os
import sys

# Ensure UTF-8 output if printed
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

folder_path = r"c:\Users\user\Desktop\test folder\자살률_삶만족도"
files = glob.glob(os.path.join(folder_path, "*.xlsx"))

out_path = r"C:\Users\user\.gemini\antigravity\brain\249a9ade-e931-4e78-a47f-45eb16e7a859\scratch\inspect_output.txt"

with open(out_path, "w", encoding="utf-8") as out:
    for f in files:
        out.write("="*80 + "\n")
        out.write(f"File: {os.path.basename(f)}\n")
        out.write("="*80 + "\n")
        try:
            # Read all sheets if there are multiple, or just the first one
            xl = pd.ExcelFile(f)
            out.write(f"Sheets: {xl.sheet_names}\n")
            
            # Read first sheet
            df = pd.read_excel(f)
            out.write(f"Shape: {df.shape}\n")
            out.write("First 15 rows:\n")
            out.write(df.head(15).to_string() + "\n\n")
            out.write("Columns:\n")
            out.write(str(df.columns.tolist()) + "\n")
            
            # Print unique values in categorization columns
            # Usually the first 3 columns are categorization columns
            cat_cols = df.columns[:3]
            for col in cat_cols:
                out.write(f"\nUnique values in column '{col}':\n")
                out.write(str(df[col].dropna().unique().tolist()[:20]) + "\n")
                
        except Exception as e:
            out.write(f"Error reading file: {e}\n")
        out.write("\n\n")

print("Inspection completed. Written to scratch/inspect_output.txt")
