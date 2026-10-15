import openpyxl
import pandas as pd
import json

file_path = "SnackRush_Complete_Dataset.xlsx"
wb = openpyxl.load_workbook(file_path, read_only=True)
sheet_names = wb.sheetnames
print(f"Sheet names: {sheet_names}")

sheets_info = {}
for sheet in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    sheets_info[sheet] = {
        "rows": len(df),
        "cols": len(df.columns),
        "columns": list(df.columns),
        "head": df.head(3).to_dict(orient="records"),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum())
    }
    print(f"\n--- SHEET: {sheet} ---")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Duplicate rows: {sheets_info[sheet]['duplicate_rows']}")
    print("Null summary:")
    nulls = df.isnull().sum()
    print(nulls[nulls > 0])
    
    # Check for target candidates
    target_candidates = [c for c in df.columns if any(w in c.lower() for w in ['attrit', 'status', 'left', 'exit', 'turnover', 'terminated', 'active'])]
    print(f"Potential target columns: {target_candidates}")
    for c in target_candidates:
        print(f"Value counts for {c}:")
        print(df[c].value_counts(dropna=False))

with open("dataset_profile_raw.json", "w") as f:
    json.dump(sheets_info, f, indent=2, default=str)
print("\nProfile saved to dataset_profile_raw.json")
