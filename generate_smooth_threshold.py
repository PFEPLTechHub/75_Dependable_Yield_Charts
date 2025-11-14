import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import timedelta

# Read the Excel file
input_file = '251112 For Graphs (1).xlsx'
df_reduced = pd.read_excel(input_file, sheet_name='Reduced Flows')
df_base = pd.read_excel(input_file, sheet_name='Base Flows')

# Convert Date column to datetime
df_reduced['Date'] = pd.to_datetime(df_reduced['Date'], format='%d-%b')
df_base['Date'] = pd.to_datetime(df_base['Date'], format='%d-%b')

# For testing, use Nikhop
junction_name = 'Nikhop'

print(f"Generating smooth filled threshold chart for: {junction_name}")

# Prepare data
dates = df_reduced['Date']
values_reduced = df_reduced[junction_name]
values_base = df_base[junction_name]

# Cap reduced values at 3.0 for the fill area
values_capped = np.minimum(values_reduced, 3.0)

# Create figure
fig, ax = plt.subplots(figsize=(16, 8))

# 1. FILLED BLUE AREA (threshold) - fill from 0 to reduced flow (capped at 3.0)
ax.fill_between(dates, 0, values_capped, 
                color='#4169E1', alpha=0.4, 
                label='Threshold (Reduced Flow)', zorder=1)

# 2. SMOOTH ORANGE LINE (Base Flow)
ax.plot(dates, values_base, 
        linewidth=2.5, color='#FF6600', 
        label='Base Flow', zorder=3)

# 3. SMOOTH BLUE LINE (Reduced Flow) - on top of fill
ax.plot(dates, values_reduced, 
        linewidth=2.5, color='#0066CC', 
        label='Reduced Flow', zorder=4)

# 4. HORIZONTAL LINE at 3.0 (Maximum Pickup)
ax.axhline(y=3.0, color='#FF6F00', linewidth=2.5, 
           linestyle='-', label='Maximum Pickup (3.0 MCM)', zorder=2)

# Formatting
ax.set_xlabel('Date', fontsize=14, fontweight='bold')
ax.set_ylabel('Capacity Threshold (MCM)', fontsize=14, fontweight='bold')
ax.set_title(junction_name, fontsize=18, fontweight='bold', pad=20)

# Set X-axis limits with 1-day padding on right to prevent cutoff
x_min = dates.min()
x_max = dates.max() + timedelta(days=1)
ax.set_xlim(x_min, x_max)

# Set Y-axis limits - focus on threshold range (0-5)
# This makes the 0-3.0 threshold area more visible
ax.set_ylim(0, 5.0)

# Format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

# Format y-axis
ax.tick_params(axis='y', labelsize=11)

# Grid - only vertical lines
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x', zorder=0)

# Add shaded regions where reduced flow > 3.0
above_max = values_reduced > 3.0
if above_max.any():
    change_points = np.diff(above_max.astype(int))
    starts = np.where(change_points == 1)[0] + 1
    ends = np.where(change_points == -1)[0] + 1
    
    if above_max.iloc[0]:
        starts = np.insert(starts, 0, 0)
    if above_max.iloc[-1]:
        ends = np.append(ends, len(above_max) - 1)
    
    for start, end in zip(starts, ends):
        ax.axvspan(dates.iloc[start], dates.iloc[end], 
                   alpha=0.15, color='gray', zorder=0)

# Background
ax.set_facecolor('#FAFAFA')
fig.patch.set_facecolor('white')

# Legend
ax.legend(loc='upper right', fontsize=11, frameon=True, 
          fancybox=True, shadow=True, bbox_to_anchor=(0.98, 0.98))

plt.tight_layout()

# Save
output_file = f'availability_charts/{junction_name}_smooth.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[SUCCESS] Smooth threshold chart saved: {output_file}")
print("No overflow - filled area stops at last date with 1-day padding.")

