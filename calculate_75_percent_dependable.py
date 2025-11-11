import pandas as pd

# Load the Excel file
excel_file = "ALL MERGED 22 Points_09112025.xlsx"
xl = pd.ExcelFile(excel_file)

print(f"Processing {len(xl.sheet_names)} junctions...")
print(f"Sheet names: {xl.sheet_names}\n")

# Dictionary to store results for each junction
results = {}

# Process each sheet (junction)
for sheet_name in xl.sheet_names:
    print(f"Processing: {sheet_name}")
    
    # Read the sheet (only first 2 rows for testing)
    df = pd.read_excel(xl, sheet_name=sheet_name, nrows=2)
    
    # Get the first 3 year columns (assuming 1975, 1976, 1977)
    year_columns = [col for col in df.columns if col != 'Date']
    first_3_years = year_columns[:3]
    
    print(f"  Using years: {first_3_years}")
    
    # Select only Date and first 3 years
    data_3_years = df[first_3_years]
    
    # Calculate 75% dependable yield (25th percentile) for each row (each date)
    dependable_75 = data_3_years.quantile(q=0.25, axis=1)
    
    # Store results with junction name
    results[sheet_name] = dependable_75

# Create final output DataFrame
output_df = pd.DataFrame(results)

# Add Date column as the first column
output_df.insert(0, 'date', df['Date'])

# Display preview
print("\n" + "="*80)
print("OUTPUT PREVIEW:")
print("="*80)
print(output_df.head(10))
print(f"\n... (showing first 10 of {len(output_df)} rows)")
print("\nOutput shape:", output_df.shape)
print(f"Columns: date + {len(xl.sheet_names)} junctions")

# Save to Excel
output_file = "daily_75pct_dependable_all_junctions.xlsx"
output_df.to_excel(output_file, index=False)

print(f"\n✓ Results saved to: {output_file}")
print("\nColumn names in output file:")
for i, col in enumerate(output_df.columns):
    print(f"  {i+1}. {col}")

