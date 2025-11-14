import pandas as pd

print('File: 251112 For Graphs (1).xlsx')
print('='*60)

df_r = pd.read_excel('251112 For Graphs (1).xlsx', sheet_name='Reduced Flows')
df_b = pd.read_excel('251112 For Graphs (1).xlsx', sheet_name='Base Flows')

print(f'Reduced Flows sheet: {len(df_r)} rows, {len(df_r.columns)} columns')
print(f'Columns: {list(df_r.columns)[:8]}')
print(f'\nBase Flows sheet: {len(df_b)} rows, {len(df_b.columns)} columns')
print(f'\nDate range: {df_r["Date"].iloc[0]} to {df_r["Date"].iloc[-1]}')
print(f'\nSample data for Nikhop (first 5 rows):')
print(df_r[['Date', 'Nikhop']].head())

