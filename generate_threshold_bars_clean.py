import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta

# Read the Excel file
input_file = '251112 For Graphs (1).xlsx'
df_reduced = pd.read_excel(input_file, sheet_name='Reduced Flows')

# Convert Date column to datetime
df_reduced['Date'] = pd.to_datetime(df_reduced['Date'], format='%d-%b')

# For testing, use Nikhop
junction_name = 'Nikhop'

print(f"Generating clean threshold bar chart for: {junction_name}")

# Prepare data
dates = df_reduced['Date']
values = df_reduced[junction_name]

# Define thresholds in 0.1 MCM increments (up to 3.0)
thresholds = np.arange(0.1, 3.01, 0.1)

# Color gradient from light blue to dark blue
def get_color_for_threshold(threshold, max_threshold=3.0):
    """Get color from light blue (low) to dark blue (high)"""
    normalized = threshold / max_threshold
    light_blue = np.array([173, 216, 230]) / 255
    dark_blue = np.array([0, 0, 139]) / 255
    color = light_blue + normalized * (dark_blue - light_blue)
    color = np.clip(color, 0, 1)
    return tuple(color)

# Create figure
fig, ax = plt.subplots(figsize=(16, 8))

# Track achieved thresholds
achieved_thresholds = []
bar_height = 0.09
y_position = 0

# For each threshold, create horizontal bars showing when it was achieved
for threshold in thresholds:
    if threshold > 3.0:
        continue
    
    # Find continuous periods where value >= threshold
    periods = []
    in_period = False
    start_idx = None
    
    for i, (date, value) in enumerate(zip(dates, values)):
        if value >= threshold and not in_period:
            start_idx = i
            in_period = True
        elif value < threshold and in_period:
            periods.append((dates.iloc[start_idx], dates.iloc[i-1]))
            in_period = False
    
    if in_period:  # Handle if still in period at end
        periods.append((dates.iloc[start_idx], dates.iloc[-1]))
    
    # Only plot if threshold was achieved
    if len(periods) > 0:
        achieved_thresholds.append(threshold)
        color = get_color_for_threshold(threshold)
        
        for start_date, end_date in periods:
            width = (end_date - start_date).days + 1
            ax.barh(y_position, width, left=start_date, height=bar_height,
                   color=color, alpha=0.85, edgecolor='none')
        
        y_position += 0.1

# Formatting
ax.set_xlabel('Date', fontsize=14, fontweight='bold')
ax.set_ylabel('Capacity Threshold (MCM)', fontsize=14, fontweight='bold')
ax.set_title(junction_name, fontsize=18, fontweight='bold', pad=20)

# Set limits
ax.set_xlim(dates.min(), dates.max())
ax.set_ylim(-0.05, y_position + 0.05)

# Format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

# Format y-axis
y_tick_positions = [i * 0.1 + 0.045 for i in range(len(achieved_thresholds))]
y_tick_labels = [f'{t:.1f}' for t in achieved_thresholds]
ax.set_yticks(y_tick_positions)
ax.set_yticklabels(y_tick_labels, fontsize=10)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x', zorder=0)

# Add Maximum Pickup reference line at 3.0 on Y-axis
max_pickup_y = achieved_thresholds.index(3.0) * 0.1 + 0.045 if 3.0 in achieved_thresholds else None
if max_pickup_y:
    ax.axhline(y=max_pickup_y, color='#FF6F00', linewidth=2.5, 
               linestyle='-', label='Maximum Pickup (3.0 MCM)', zorder=5)

# Background
ax.set_facecolor('#FAFAFA')
fig.patch.set_facecolor('white')

# Legend
ax.legend(loc='upper right', fontsize=11, frameon=True, fancybox=True, shadow=True)

plt.tight_layout()

# Save
output_file = f'availability_charts/{junction_name}_threshold.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[SUCCESS] Clean threshold chart saved: {output_file}")
print(f"Achieved thresholds: {len(achieved_thresholds)}")

