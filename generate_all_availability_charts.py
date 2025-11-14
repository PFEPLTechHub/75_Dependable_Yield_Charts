import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

# Read the Excel file - both sheets
input_file = '251112 For Graphs (1).xlsx'
df_reduced = pd.read_excel(input_file, sheet_name='Reduced Flows')
df_base = pd.read_excel(input_file, sheet_name='Base Flows')

# Convert Date column to datetime for both
df_reduced['Date'] = pd.to_datetime(df_reduced['Date'], format='%d-%b')
df_base['Date'] = pd.to_datetime(df_base['Date'], format='%d-%b')

# Get junction columns that exist in BOTH sheets
junction_columns_reduced = set(col for col in df_reduced.columns if col != 'Date')
junction_columns_base = set(col for col in df_base.columns if col != 'Date')
junction_columns = list(junction_columns_reduced & junction_columns_base)  # Intersection

print(f"Found {len(junction_columns)} junctions")
print(f"Total dates: {len(df_reduced)}")

# Create output directory
output_dir = "availability_charts"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}\n")

# Maximum Pickup threshold
max_pickup = 3.0

# Define ranges and colors (from dark blue to light blue)
ranges = [
    (0.0, 0.5, '#00008B'),    # Dark Blue
    (0.5, 1.0, '#0000CD'),    # Medium Blue
    (1.0, 1.5, '#4169E1'),    # Royal Blue
    (1.5, 2.0, '#1E90FF'),    # Dodger Blue
    (2.0, 2.5, '#87CEEB'),    # Sky Blue
    (2.5, 3.0, '#ADD8E6'),    # Light Blue
]

# Function to generate chart for one junction
def generate_chart(junction_name):
    print(f"Generating chart for: {junction_name}")
    
    # Prepare data from REDUCED FLOWS for bars (using reduced as base for bars)
    dates = df_reduced['Date']
    values_reduced = df_reduced[junction_name]
    values_base = df_base[junction_name]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Create stacked bars - discrete bars with small gaps
    bar_width = 0.9  # Slightly less than 1 day for visible gaps
    
    # Plot stacked bars for each date (using reduced flows)
    for date, value in zip(dates, values_reduced):
        bottom = 0
        capped_value = min(value, max_pickup)
        
        for start, end, color in ranges:
            if capped_value > start:
                segment_height = min(capped_value - start, end - start)
                ax.bar(date, segment_height, width=bar_width, 
                       bottom=bottom, color=color, 
                       edgecolor='none', alpha=0.8, zorder=1,
                       align='center')
                bottom += segment_height
            else:
                break
    
    # Add text labels for each range (based on reduced flows)
    for range_start, range_end, color in ranges:
        dates_in_range = []
        
        for i, (date, value) in enumerate(zip(dates, values_reduced)):
            capped_value = min(value, max_pickup)
            if range_start <= capped_value < range_end or (range_end == 3.0 and range_start <= capped_value <= 3.0):
                dates_in_range.append(i)
        
        if len(dates_in_range) > 0:
            first_idx = dates_in_range[0]
            last_idx = dates_in_range[-1]
            
            first_date = dates.iloc[first_idx]
            last_date = dates.iloc[last_idx]
            
            total_days = (last_date - first_date).days + 1
            
            time_delta = (last_date - first_date) / 2
            mid_date = first_date + time_delta
            
            y_pos = (range_start + range_end) / 2
            
            range_values = [values_reduced.iloc[i] for i in dates_in_range]
            avg_value = sum(range_values) / len(range_values)
            
            def format_date(date):
                day = date.day
                if day == 1 or day == 21 or day == 31:
                    suffix = 'st'
                elif day == 2 or day == 22:
                    suffix = 'nd'
                elif day == 3 or day == 23:
                    suffix = 'rd'
                else:
                    suffix = 'th'
                return date.strftime(f'%d{suffix} %b')
            
            start_str = format_date(first_date)
            end_str = format_date(last_date)
            
            text = f"{avg_value:.2f} MCM ({start_str} - {end_str}) = {total_days} days"
            text_color = 'white' if range_start < 1.5 else 'black'
            
            if total_days >= 10:
                ax.text(mid_date, y_pos, text,
                        ha='center', va='center',
                        fontsize=6, fontweight='bold',
                        color=text_color, zorder=4)
    
    # Plot BOTH lines - Reduced Flows and Base Flows
    ax.plot(dates, values_reduced, 
            linewidth=2.5, 
            color='#1E88E5',  # Blue
            label='Reduced Flows',
            zorder=3,
            marker='o',
            markersize=3)
    
    ax.plot(dates, values_base, 
            linewidth=2.5, 
            color='#FF9800',  # Orange
            label='Base Flows',
            zorder=3,
            marker='s',
            markersize=3)
    
    # Plot Maximum Pickup line
    ax.axhline(y=max_pickup, color='#FF6F00', linewidth=2.5, 
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
            ax.axvspan(dates.iloc[start], dates.iloc[end], 
                       alpha=0.15, color='gray', zorder=0)
    
    # Formatting
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Availability', fontsize=14, fontweight='bold')
    ax.set_title(junction_name, fontsize=18, fontweight='bold', pad=20)
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8, zorder=0)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)
    
    # Set Y limit based on max of both datasets
    max_val = max(values_reduced.max(), values_base.max())
    ax.set_ylim(0, max(max_val + 0.5, max_pickup + 0.5))
    y_ticks = np.arange(0, ax.get_ylim()[1] + 0.5, 0.5)
    ax.set_yticks(y_ticks)
    ax.tick_params(axis='y', labelsize=11)
    
    ax.legend(loc='upper right', fontsize=12, frameon=True, 
              fancybox=True, shadow=True)
    
    ax.set_facecolor('#FAFAFA')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    
    # Save chart
    safe_filename = junction_name.replace('/', '_').replace('\\', '_').replace(':', '_')
    output_file = os.path.join(output_dir, f"{safe_filename}_availability.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  Saved: {output_file}")

# Generate charts for all junctions
print("\n" + "="*80)
print("GENERATING AVAILABILITY CHARTS FOR ALL JUNCTIONS")
print("="*80 + "\n")

for idx, junction in enumerate(junction_columns, 1):
    print(f"[{idx}/{len(junction_columns)}]", end=" ")
    generate_chart(junction)

print("\n" + "="*80)
print("[SUCCESS] ALL CHARTS GENERATED!")
print("="*80)
print(f"\nTotal charts: {len(junction_columns)}")
print(f"Location: ./{output_dir}/")
print("\n" + "="*80 + "\n")

