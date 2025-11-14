import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime, timedelta

# Read the Excel file
input_file = '251112 For Graphs (1).xlsx'
df_reduced = pd.read_excel(input_file, sheet_name='Reduced Flows')
df_base = pd.read_excel(input_file, sheet_name='Base Flows')

# Convert Date column to datetime
df_reduced['Date'] = pd.to_datetime(df_reduced['Date'], format='%d-%b')
df_base['Date'] = pd.to_datetime(df_base['Date'], format='%d-%b')

# For testing, use Nikhop
junction_name = 'Nikhop'

print(f"Generating final threshold chart for: {junction_name}")

# Prepare data
dates = df_reduced['Date']
values_reduced = df_reduced[junction_name]
values_base = df_base[junction_name]

# Define thresholds in 0.1 MCM increments (up to 3.0)
thresholds = np.arange(0.1, 3.01, 0.1)

# Color gradient from light blue to dark blue
colors_map = {
    0.1: '#ADD8E6', 0.2: '#9FD3E6', 0.3: '#91CBE6', 0.4: '#83C3E6', 0.5: '#75BBE6',
    0.6: '#67B3E6', 0.7: '#59ABE6', 0.8: '#4BA3E6', 0.9: '#3D9BE6', 1.0: '#2F93E6',
    1.1: '#218BE6', 1.2: '#1383E6', 1.3: '#1375D6', 1.4: '#1367C6', 1.5: '#1359B6',
    1.6: '#134BA6', 1.7: '#133D96', 1.8: '#132F86', 1.9: '#132176', 2.0: '#131366',
    2.1: '#100F5E', 2.2: '#0E0B56', 2.3: '#0C074E', 2.4: '#0A0446', 2.5: '#08003E',
    2.6: '#060036', 2.7: '#04002E', 2.8: '#020026', 2.9: '#00001E', 3.0: '#00008B'
}

# Create figure
fig, ax = plt.subplots(figsize=(16, 8))

# Track achieved thresholds and their Y positions
achieved_data = []
bar_height = 0.08
y_position = 0

# Plot horizontal bars for each threshold
for threshold in thresholds:
    if threshold > 3.0:
        continue
    
    # Find continuous periods where value >= threshold
    periods = []
    in_period = False
    start_idx = None
    
    for i, value in enumerate(values_reduced):
        if value >= threshold and not in_period:
            start_idx = i
            in_period = True
        elif value < threshold and in_period:
            periods.append((dates.iloc[start_idx], dates.iloc[i-1]))
            in_period = False
    
    if in_period:
        periods.append((dates.iloc[start_idx], dates.iloc[-1]))
    
    # Only plot if threshold was achieved
    if len(periods) > 0:
        color = colors_map.get(round(threshold, 1), '#87CEEB')
        
        for start_date, end_date in periods:
            # Calculate width carefully to avoid overflow
            width_days = (end_date - start_date).days + 1
            
            # Draw rectangle instead of bar for precise control
            rect = mpatches.Rectangle((mdates.date2num(start_date), y_position - bar_height/2),
                                     width_days, bar_height,
                                     facecolor=color, edgecolor='none',
                                     alpha=0.85, zorder=1)
            ax.add_patch(rect)
        
        achieved_data.append((threshold, y_position))
        y_position += 0.1

# Formatting
ax.set_xlabel('Date', fontsize=14, fontweight='bold')
ax.set_ylabel('Capacity Threshold (MCM)', fontsize=14, fontweight='bold')
ax.set_title(junction_name, fontsize=18, fontweight='bold', pad=20)

# Set X-axis limits precisely
ax.set_xlim(mdates.date2num(dates.min()), mdates.date2num(dates.max()))

# Set Y-axis limits
ax.set_ylim(-0.1, y_position + 0.05)

# Format x-axis as dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

# Format y-axis with threshold labels
y_ticks = [data[1] for data in achieved_data]
y_labels = [f'{data[0]:.1f}' for data in achieved_data]
ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels, fontsize=10)

# Add Maximum Pickup reference line
max_pickup_threshold = 3.0
if any(t == max_pickup_threshold for t, _ in achieved_data):
    max_y = [pos for thresh, pos in achieved_data if thresh == max_pickup_threshold][0]
    ax.axhline(y=max_y, color='#FF6F00', linewidth=2.5, 
               linestyle='-', label='Maximum Pickup', zorder=5)
    ax.legend(loc='upper right', fontsize=11, frameon=True, fancybox=True, shadow=True)

# Grid - only vertical lines
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x', zorder=0)

# Background
ax.set_facecolor('#FAFAFA')
fig.patch.set_facecolor('white')

# Set axis spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

# Save
output_file = f'availability_charts/{junction_name}_threshold.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[SUCCESS] Final clean threshold chart saved: {output_file}")
print(f"Achieved thresholds: {len(achieved_data)} out of {len(thresholds)}")
print("Bars are constrained within plot boundaries using Rectangle patches.")

