import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta

# Read the Excel file - both sheets
input_file = '251112 For Graphs (1).xlsx'
df_reduced = pd.read_excel(input_file, sheet_name='Reduced Flows')
df_base = pd.read_excel(input_file, sheet_name='Base Flows')

# Convert Date column to datetime
df_reduced['Date'] = pd.to_datetime(df_reduced['Date'], format='%d-%b')
df_base['Date'] = pd.to_datetime(df_base['Date'], format='%d-%b')

# For testing, use Nikhop
junction_name = 'Nikhop'

print(f"Generating threshold-based bar chart for: {junction_name}")

# Prepare data
dates = df_reduced['Date']
values_reduced = df_reduced[junction_name]
values_base = df_base[junction_name]

# Define thresholds in 0.1 MCM increments (up to 3.0 only)
thresholds = np.arange(0.1, 3.01, 0.1)  # 0.1, 0.2, 0.3 ... 3.0 (inclusive)

# Color gradient from light blue to dark blue
def get_color_for_threshold(threshold, max_threshold=3.0):
    """Get color from light blue (low) to dark blue (high)"""
    normalized = threshold / max_threshold
    # Light blue to dark blue gradient
    light_blue = np.array([173, 216, 230]) / 255  # Light blue
    dark_blue = np.array([0, 0, 139]) / 255       # Dark blue
    color = light_blue + normalized * (dark_blue - light_blue)
    # Clamp values to [0, 1] range to avoid floating point errors
    color = np.clip(color, 0, 1)
    return tuple(color)

# Create figure
fig, ax = plt.subplots(figsize=(16, 10))

# For each threshold, find the date ranges where value >= threshold
bar_height = 0.08  # Height of each horizontal bar
y_position = 0

# Track which thresholds were actually achieved
achieved_thresholds = []

for threshold in thresholds:
    # Only process thresholds up to 3.0 (Maximum Pickup)
    if threshold > 3.0:
        continue
        
    # Find dates where reduced flows >= threshold (but only count if <= 3.0 for bar display)
    dates_above = []
    for i, (date, value) in enumerate(zip(dates, values_reduced)):
        if value >= threshold:
            dates_above.append(date)
    
    if len(dates_above) > 0:  # Only plot if threshold was achieved
        achieved_thresholds.append(threshold)
        
        # Find continuous periods
        periods = []
        if len(dates_above) > 0:
            current_start = dates_above[0]
            prev_date = dates_above[0]
            
            for date in dates_above[1:]:
                if (date - prev_date).days > 1:  # Gap detected
                    periods.append((current_start, prev_date))
                    current_start = date
                prev_date = date
            periods.append((current_start, prev_date))
        
        # Plot horizontal bars for each period
        color = get_color_for_threshold(threshold)
        for start_date, end_date in periods:
            duration = (end_date - start_date).days + 1
            
            # Draw horizontal bar
            ax.barh(y_position, duration, left=start_date, height=bar_height,
                   color=color, alpha=0.85, edgecolor='none', linewidth=0)
        
        y_position += 0.1  # Move to next bar position

# Plot the line graphs on secondary axis (sharing same Y scale)
ax2 = ax.twinx()  # Create twin Y-axis for lines on the right
ax2.plot(dates, values_reduced, linewidth=2.5, color='#0066CC', 
        label='Reduced Flows', zorder=10, clip_on=True)
ax2.plot(dates, values_base, linewidth=2.5, color='#FF6600', 
        label='Base Flows', zorder=10, clip_on=True)
ax2.axhline(y=3.0, color='#FF6F00', linewidth=2.5, 
           linestyle='-', label='Maximum Pickup', zorder=9)

# Format axes
ax.set_xlabel('Date', fontsize=14, fontweight='bold')
ax.set_ylabel('Capacity Threshold (MCM)', fontsize=14, fontweight='bold')
ax.set_title(junction_name, fontsize=18, fontweight='bold', pad=20)

# Set limits - align exactly with data range
ax.set_xlim(dates.min(), dates.max())
ax.set_ylim(-0.05, y_position + 0.05)

# Format x-axis dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

# Format y-axis
y_tick_positions = np.arange(0.04, y_position, 0.1)
y_tick_labels = [f'{t:.1f}' for t in achieved_thresholds]
ax.set_yticks(y_tick_positions)
ax.set_yticklabels(y_tick_labels, fontsize=10)

# Configure secondary axis for lines
max_val = max(values_reduced.max(), values_base.max())
ax2.set_ylim(0, max_val + 0.5)
ax2.set_ylabel('Availability (MCM)', fontsize=14, fontweight='bold', rotation=270, labelpad=20)
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position('right')
ax2.tick_params(axis='y', labelsize=10)

# Ensure lines are clipped to the plot area
ax2.set_clip_on(True)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x')

# Legend for lines
ax2.legend(loc='upper right', fontsize=11, frameon=True, fancybox=True, shadow=True)

ax.set_facecolor('#FAFAFA')
ax2.set_facecolor('#FAFAFA')
fig.patch.set_facecolor('white')

# Ensure bars don't extend beyond axis spines
ax.spines['left'].set_position(('outward', 0))
ax.spines['bottom'].set_position(('outward', 0))
ax.spines['right'].set_visible(True)
ax.spines['top'].set_visible(False)

# Clip bars to axis boundaries
for patch in ax.patches:
    patch.set_clip_on(True)

plt.tight_layout()

# Save
output_file = f'availability_charts/{junction_name}_threshold_bars.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[SUCCESS] Threshold bar chart saved: {output_file}")
print(f"Achieved thresholds: {len(achieved_thresholds)} out of {len(thresholds)}")

