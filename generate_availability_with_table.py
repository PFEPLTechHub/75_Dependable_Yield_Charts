import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.patches import Rectangle

# Read the Excel file - both sheets
input_file = '251112 For Graphs (1).xlsx'
df_reduced = pd.read_excel(input_file, sheet_name='Reduced Flows')
df_base = pd.read_excel(input_file, sheet_name='Base Flows')

# Convert Date column to datetime for both
df_reduced['Date'] = pd.to_datetime(df_reduced['Date'], format='%d-%b')
df_base['Date'] = pd.to_datetime(df_base['Date'], format='%d-%b')

# For testing, use only Nikhop
junction_name = 'Nikhop'

print(f"Generating chart with table for: {junction_name}")

# Prepare data
dates = df_reduced['Date']
values_reduced = df_reduced[junction_name]
values_base = df_base[junction_name]

# Maximum Pickup threshold
max_pickup = 3.0

# Define ranges and colors (light blue at bottom to dark blue at top - REVERSED)
ranges = [
    (0.0, 0.5, '#ADD8E6', '0.5'),    # Light Blue (bottom)
    (0.5, 1.0, '#87CEEB', '1.0'),    # Sky Blue
    (1.0, 1.5, '#1E90FF', '1.5'),    # Dodger Blue
    (1.5, 2.0, '#4169E1', '2.0'),    # Royal Blue
    (2.0, 2.5, '#0000CD', '2.5'),    # Medium Blue
    (2.5, 3.0, '#00008B', '3.0'),    # Dark Blue (top)
]

# Create figure with GridSpec for chart and table
fig = plt.figure(figsize=(20, 8))
gs = fig.add_gridspec(1, 2, width_ratios=[4, 1], wspace=0.15)
ax_chart = fig.add_subplot(gs[0])
ax_table = fig.add_subplot(gs[1])

# === CHART SECTION ===
# Create stacked bars - bars should align with line
bar_width = 0.8  # Slightly thinner for better line visibility

# Plot stacked bars for each date (using reduced flows)
for date, value in zip(dates, values_reduced):
    bottom = 0
    capped_value = min(value, max_pickup)
    
    for start, end, color, _ in ranges:
        if capped_value > start:
            segment_height = min(capped_value - start, end - start)
            ax_chart.bar(date, segment_height, width=bar_width, 
                   bottom=bottom, color=color, 
                   edgecolor='none', alpha=0.7, zorder=1,
                   align='center')
            bottom += segment_height
        else:
            break

# Plot Reduced Flows line - should trace top of bars
ax_chart.plot(dates, values_reduced, 
        linewidth=2, 
        color='#0066CC',  # Darker blue for better visibility
        label='Availability',
        zorder=4,
        linestyle='-',
        marker='',  # No markers, just line
        drawstyle='default')  # Connect points directly

# Plot Base Flows line
ax_chart.plot(dates, values_base, 
        linewidth=2, 
        color='#FF6600',  # Darker orange
        label='Base Flows',
        zorder=4,
        linestyle='-',
        marker='',  # No markers
        drawstyle='default')

# Plot Maximum Pickup line
ax_chart.axhline(y=max_pickup, color='#FF6F00', linewidth=3, 
           linestyle='-', label='Maximum Pickup', zorder=2)

# Add shaded regions where REDUCED availability is above max_pickup
above_max = values_reduced > max_pickup
if above_max.any():
    change_points = np.diff(above_max.astype(int))
    starts = np.where(change_points == 1)[0] + 1
    ends = np.where(change_points == -1)[0] + 1
    
    if above_max.iloc[0]:
        starts = np.insert(starts, 0, 0)
    if above_max.iloc[-1]:
        ends = np.append(ends, len(above_max) - 1)
    
    for start, end in zip(starts, ends):
        ax_chart.axvspan(dates.iloc[start], dates.iloc[end], 
                   alpha=0.15, color='gray', zorder=0)

# Formatting for chart
ax_chart.set_xlabel('Date', fontsize=14, fontweight='bold')
ax_chart.set_ylabel('Availability', fontsize=14, fontweight='bold')
ax_chart.set_title(junction_name, fontsize=18, fontweight='bold', pad=20)

# Grid only on x-axis (vertical lines), no horizontal lines through bars
ax_chart.grid(True, alpha=0.3, linestyle='--', linewidth=0.8, axis='x', zorder=0)

ax_chart.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax_chart.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax_chart.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

max_val = max(values_reduced.max(), values_base.max())
ax_chart.set_ylim(0, max(max_val + 0.5, max_pickup + 0.5))
y_ticks = np.arange(0, ax_chart.get_ylim()[1] + 0.5, 0.5)
ax_chart.set_yticks(y_ticks)
ax_chart.tick_params(axis='y', labelsize=11)

ax_chart.legend(loc='lower right', fontsize=11, frameon=True, 
          fancybox=True, shadow=True)

ax_chart.set_facecolor('#FAFAFA')

# === TABLE SECTION ===
ax_table.axis('off')

# Helper function to convert date to period description
def get_period_description(date):
    """Convert date to period like 'Mid June', 'Late Sep'"""
    month = date.strftime('%b')
    day = date.day
    
    if day <= 10:
        return f"Early {month}"
    elif day <= 20:
        return f"Mid {month}"
    else:
        return f"Late {month}"

# Calculate table data - Days and Period for each capacity level
table_data = []
for range_start, range_end, color, capacity in reversed(ranges):  # Reverse to show 3.0 at top
    # Find dates in this range
    dates_in_range = []
    for i, (date, value) in enumerate(zip(dates, values_reduced)):
        capped_value = min(value, max_pickup)
        if capped_value >= range_end:  # At or above this capacity
            dates_in_range.append((i, date))
    
    if len(dates_in_range) > 0:
        first_date = dates_in_range[0][1]
        last_date = dates_in_range[-1][1]
        total_days = len(dates_in_range)
        
        # Format period in human-readable form
        first_period = get_period_description(first_date)
        last_period = get_period_description(last_date)
        
        if first_period == last_period:
            period = first_period
        else:
            period = f"{first_period} –\n{last_period}"
        
        table_data.append([capacity, total_days, period, color])
    else:
        table_data.append([capacity, 0, 'N/A', color])

# Create table content
table_content = []
colors_list = []
for row in table_data:
    table_content.append([row[0], row[1], row[2]])
    colors_list.append(row[3])

# Draw table with better positioning
table = ax_table.table(cellText=table_content,
                       colLabels=['Capacity', 'Days', 'Period'],
                       cellLoc='center',
                       loc='center',
                       bbox=[0.05, 0.25, 0.9, 0.65])

# Style the table
table.auto_set_font_size(False)
table.set_fontsize(11)

# Set column widths
for i in range(len(table_data) + 1):
    table[(i, 0)].set_width(0.25)  # Capacity column
    table[(i, 1)].set_width(0.25)  # Days column
    table[(i, 2)].set_width(0.5)   # Period column (wider)

# Color the capacity cells with matching bar colors
for i, color in enumerate(colors_list):
    cell = table[(i+1, 0)]
    cell.set_facecolor(color)
    cell.set_text_props(weight='bold', color='white', size=11)
    cell.set_height(0.08)

# Style header row
for j in range(3):
    cell = table[(0, j)]
    cell.set_facecolor('#2C3E50')
    cell.set_text_props(weight='bold', color='white', size=12)
    cell.set_height(0.1)
    cell.set_edgecolor('#1A252F')

# Style data cells (Days and Period columns)
for i in range(1, len(table_data) + 1):
    for j in range(1, 3):
        cell = table[(i, j)]
        cell.set_facecolor('#FFFFFF')
        cell.set_edgecolor('#D0D0D0')
        cell.set_text_props(size=10)
        cell.set_height(0.08)

# Add table title
ax_table.text(0.5, 0.95, 'Capacity Summary', 
             ha='center', va='top', fontsize=14, fontweight='bold',
             transform=ax_table.transAxes)

fig.patch.set_facecolor('white')
plt.tight_layout()

# Save the chart
output_file = f'availability_charts/{junction_name}_availability.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[SUCCESS] Chart with table saved: {output_file}")
print("\nPlease review this chart before generating all junctions!")

