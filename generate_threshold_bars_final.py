import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
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

print(f"Generating threshold bar chart for: {junction_name}")

# Prepare data
dates = df_reduced['Date']
values_reduced = df_reduced[junction_name]
values_base = df_base[junction_name]

# Define thresholds in 0.1 MCM increments (up to 3.0)
thresholds = np.arange(0.1, 3.01, 0.1)

# Color map
colors_map = {
    0.1: '#E6F3FF', 0.2: '#CCE7FF', 0.3: '#B3DBFF', 0.4: '#99CFFF', 0.5: '#80C3FF',
    0.6: '#66B7FF', 0.7: '#4DABFF', 0.8: '#339FFF', 0.9: '#1A93FF', 1.0: '#0087FF',
    1.1: '#007BE6', 1.2: '#006FCC', 1.3: '#0063B3', 1.4: '#005799', 1.5: '#004B80',
    1.6: '#003F66', 1.7: '#00334D', 1.8: '#002733', 1.9: '#001B1A', 2.0: '#000F00',
    2.1: '#000D1F', 2.2: '#000B1E', 2.3: '#00091D', 2.4: '#00071C', 2.5: '#00051B',
    2.6: '#00031A', 2.7: '#000119', 2.8: '#000018', 2.9: '#000017', 3.0: '#00008B'
}

# Create figure
fig, ax = plt.subplots(figsize=(16, 8))

# Track achieved thresholds
bar_height = 0.09
y_positions = {}

# Plot horizontal threshold bars
for i, threshold in enumerate(thresholds):
    if threshold > 3.0:
        continue
    
    # Find continuous periods where value >= threshold
    periods = []
    in_period = False
    start_idx = None
    
    for idx, value in enumerate(values_reduced):
        if value >= threshold and not in_period:
            start_idx = idx
            in_period = True
        elif value < threshold and in_period:
            periods.append((dates.iloc[start_idx], dates.iloc[idx-1]))
            in_period = False
    
    if in_period:
        periods.append((dates.iloc[start_idx], dates.iloc[-1]))
    
    # Only plot if threshold was achieved
    if len(periods) > 0:
        y_pos = threshold  # Y-position = actual threshold value
        y_positions[threshold] = y_pos
        color = colors_map.get(round(threshold, 1), '#87CEEB')
        
        for start_date, end_date in periods:
            width_days = (end_date - start_date).days + 1
            
            # Use rectangle for precise control
            rect = mpatches.Rectangle(
                (mdates.date2num(start_date), y_pos - bar_height/2),
                width_days, bar_height,
                facecolor=color, edgecolor='none',
                alpha=0.75, zorder=1
            )
            ax.add_patch(rect)

# Plot lines
ax.plot(dates, values_reduced, linewidth=2.5, color='#0066CC', 
        label='Reduced Flow', zorder=3)
ax.plot(dates, values_base, linewidth=2.5, color='#FF6600', 
        label='Base Flow', zorder=3)

# Maximum Pickup line
ax.axhline(y=3.0, color='#FF6F00', linewidth=2.5, 
           linestyle='-', label='Maximum Pickup', zorder=2)

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

# Formatting
ax.set_xlabel('Date', fontsize=14, fontweight='bold')
ax.set_ylabel('Capacity Threshold (MCM)', fontsize=14, fontweight='bold')
ax.set_title(junction_name, fontsize=18, fontweight='bold', pad=20)

# Set limits - add small padding on right to prevent cutoff
x_padding = 0.5  # 0.5 day padding
ax.set_xlim(mdates.date2num(dates.min()) - x_padding, 
            mdates.date2num(dates.max()) + x_padding)
ax.set_ylim(0, 3.2)  # Focus on threshold range 0-3.0

# Format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

# Format y-axis
ax.set_yticks(np.arange(0, 3.5, 0.5))
ax.tick_params(axis='y', labelsize=11)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x', zorder=0)

# Background
ax.set_facecolor('#FAFAFA')
fig.patch.set_facecolor('white')

# Legend
ax.legend(loc='upper right', fontsize=11, frameon=True, fancybox=True, shadow=True)

plt.tight_layout()

# Save
output_file = f'availability_charts/{junction_name}_threshold_final.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[SUCCESS] Final threshold bar chart saved: {output_file}")
print("Y-axis limited to 0-3.5 for better visibility of threshold bars.")

