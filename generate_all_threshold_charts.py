import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
import numpy as np
import os

# Create output directory
os.makedirs('availability_charts', exist_ok=True)

# Read the Excel file
input_file = '251112 For Graphs (1).xlsx'
df_reduced = pd.read_excel(input_file, sheet_name='Reduced Flows')
df_base = pd.read_excel(input_file, sheet_name='Base Flows')

# Convert Date column to datetime (force year to 2024 for proper display)
df_reduced['Date'] = pd.to_datetime('2024-' + df_reduced['Date'].astype(str), format='%Y-%d-%b')
df_base['Date'] = pd.to_datetime('2024-' + df_base['Date'].astype(str), format='%Y-%d-%b')

# Get all junction names (excluding Date column and unnamed columns)
all_junctions = [col for col in df_reduced.columns if col != 'Date' and not col.startswith('Unnamed')]

print(f"Found {len(all_junctions)} junctions to process")
print(f"Junctions: {', '.join(all_junctions)}\n")

# Define color ranges for legend
CAPACITY_COLORS = {
    '2.5-3.0 MCM': '#00008B',  # Dark Blue
    '2.0-2.5 MCM': '#0047AB',  # Medium-Dark Blue
    '1.5-2.0 MCM': '#0066CC',  # Medium Blue
    '1.0-1.5 MCM': '#4D94DB',  # Light-Medium Blue
    '0.5-1.0 MCM': '#87CEEB',  # Light Blue
    '0.0-0.5 MCM': '#ADD8E6'   # Very Light Blue
}

# Color gradient function
def get_color_for_threshold(threshold, max_threshold=3.0):
    """Get hex color from light blue to dark blue"""
    if threshold >= 2.5:
        return '#00008B'
    elif threshold >= 2.0:
        return '#0047AB'
    elif threshold >= 1.5:
        return '#0066CC'
    elif threshold >= 1.0:
        return '#4D94DB'
    elif threshold >= 0.5:
        return '#87CEEB'
    else:
        return '#ADD8E6'

# Helper function to get month position
def get_month_position(date):
    """Return Early/Mid/Late based on day of month"""
    day = date.day
    if day <= 10:
        return "Early"
    elif day <= 20:
        return "Mid"
    else:
        return "Late"

# Process all junctions
for junction_idx, junction_name in enumerate(all_junctions, 1):
    print(f"[{junction_idx}/{len(all_junctions)}] Generating chart for: {junction_name}")
    
    try:
        # Prepare data
        dates = df_reduced['Date']
        values_reduced = df_reduced[junction_name]
        values_base = df_base[junction_name]
        
        # Calculate max value for Y-axis range
        max_value = max(values_reduced.max(), values_base.max())
        y_max = max(6.0, max_value * 1.1)  # At least 6.0, or 110% of max value
        
        # Define thresholds in 0.1 MCM increments (up to 3.0)
        thresholds = np.arange(0.1, 3.01, 0.1)
        
        # Calculate capacity statistics for legend table
        capacity_stats = []
        # Use 0.1 increments from 3.0 down to 0.1 (matching horizontal bars)
        key_thresholds = np.arange(3.0, 0.0, -0.1).round(1).tolist()
        
        for threshold in key_thresholds:
            above_threshold = values_reduced >= threshold
            days_count = above_threshold.sum()
            
            # Only include rows that have data (skip N/A rows)
            if days_count > 0:
                # Find all continuous periods (for comma-separated periods)
                periods_list = []
                in_period = False
                start_idx = None
                
                for idx, is_above in enumerate(above_threshold):
                    if is_above and not in_period:
                        start_idx = idx
                        in_period = True
                    elif not is_above and in_period:
                        # End of period
                        first_date = dates.iloc[start_idx]
                        last_date = dates.iloc[idx - 1]
                        
                        start_pos = get_month_position(first_date)
                        end_pos = get_month_position(last_date)
                        start_month = first_date.strftime('%b')
                        end_month = last_date.strftime('%b')
                        
                        periods_list.append(f"{start_pos} {start_month} - {end_pos} {end_month}")
                        in_period = False
                
                # Check if still in period at end
                if in_period:
                    first_date = dates.iloc[start_idx]
                    last_date = dates.iloc[len(above_threshold) - 1]
                    
                    start_pos = get_month_position(first_date)
                    end_pos = get_month_position(last_date)
                    start_month = first_date.strftime('%b')
                    end_month = last_date.strftime('%b')
                    
                    periods_list.append(f"{start_pos} {start_month} - {end_pos} {end_month}")
                
                # Join all periods with comma
                period = ", ".join(periods_list)
                
                capacity_stats.append({
                    'capacity': threshold,
                    'days': days_count,
                    'period': period,
                    'color': get_color_for_threshold(threshold)
                })
        
        # Create figure
        fig = go.Figure()
        
        # Track Y positions
        y_position = 0.05
        bar_height = 0.08
        
        # Create horizontal bars for each threshold
        for threshold in thresholds:
            if threshold > 3.0:
                continue
            
            # Find continuous periods where value >= threshold
            above_threshold = values_reduced >= threshold
            
            # Find start and end indices of continuous periods
            periods = []
            in_period = False
            start_idx = None
            
            for idx, is_above in enumerate(above_threshold):
                if is_above and not in_period:
                    start_idx = idx
                    in_period = True
                elif not is_above and in_period:
                    periods.append((start_idx, idx - 1))
                    in_period = False
            
            if in_period:
                periods.append((start_idx, len(above_threshold) - 1))
            
            # Create bars for each period
            if len(periods) > 0:
                color = get_color_for_threshold(threshold)
                
                for start_idx, end_idx in periods:
                    start_date = dates.iloc[start_idx]
                    end_date = dates.iloc[end_idx]
                    
                    # Create shape for horizontal bar
                    fig.add_shape(
                        type="rect",
                        x0=start_date,
                        x1=end_date,
                        y0=y_position - bar_height/2,
                        y1=y_position + bar_height/2,
                        fillcolor=color,
                        line_width=0,
                    opacity=0.85,
                    layer='below'
                )
            
            y_position += 0.1
        
        # Add lines first (so they appear in front)
        # Maximum Pickup line
        fig.add_trace(go.Scatter(
            x=dates,
            y=[3.0] * len(dates),
            mode='lines',
            line=dict(color='#FF6600', width=2.5, dash='solid'),
            name='Maximum Pickup',
            showlegend=False,
            hovertemplate='<b>Maximum Pickup:</b> 3.0 MCM<extra></extra>'
        ))
        
        # Base Flow line
        fig.add_trace(go.Scatter(
            x=dates,
            y=values_base,
            mode='lines+markers',
            line=dict(color='#FF6600', width=2.5, dash='dash'),
            marker=dict(size=4, symbol='square', color='#FF6600'),
            name='Base Flows',
            showlegend=False,
            hovertemplate='<b>Date:</b> %{x|%d-%b}<br><b>Base:</b> %{y:.2f} MCM<extra></extra>'
        ))
        
        # Reduced Flow line
        fig.add_trace(go.Scatter(
            x=dates,
            y=values_reduced,
            mode='lines+markers',
            line=dict(color='#00008B', width=2.5),
            marker=dict(size=4, symbol='circle', color='#00008B'),
            name='Reduced Flows',
            showlegend=False,
            hovertemplate='<b>Date:</b> %{x|%d-%b}<br><b>Reduced:</b> %{y:.2f} MCM<extra></extra>'
        ))
        
        # Create clean table with proper formatting
        # Make capacity values bold, use lighter shades for capacity backgrounds
        capacity_values = [f'<b>{stat["capacity"]:.1f}</b>' for stat in capacity_stats]
        days_values = [f'<b>{stat["days"]}</b>' for stat in capacity_stats]
        period_values = [stat['period'] for stat in capacity_stats]
        
        # Use lighter versions of colors for capacity column so dark text is visible
        def lighten_color(hex_color):
            """Convert hex color to a lighter shade"""
            # Remove # if present
            hex_color = hex_color.replace('#', '')
            # Convert to RGB
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            # Lighten by mixing with white (70% color, 30% white)
            r = int(r * 0.7 + 255 * 0.3)
            g = int(g * 0.7 + 255 * 0.3)
            b = int(b * 0.7 + 255 * 0.3)
            return f'#{r:02x}{g:02x}{b:02x}'
        
        capacity_colors = [lighten_color(stat['color']) for stat in capacity_stats]
        other_colors = ['#FAFAFA' if i % 2 == 0 else 'white' for i in range(len(capacity_stats))]
        
        table_trace = go.Table(
            domain=dict(x=[0.72, 0.99], y=[0.05, 0.98]),
            header=dict(
                values=['<b>Capacity</b>', '<b>Days</b>', '<b>Period</b>'],
                fill_color='#2C3E50',
                align='center',
                font=dict(color='white', size=10, family='Arial'),
                height=25,
                line=dict(color='#34495E', width=2)
            ),
            cells=dict(
                values=[capacity_values, days_values, period_values],
                fill_color=[capacity_colors, other_colors, other_colors],
                align='center',
                font=dict(size=9, family='Arial', color='#1a1a1a'),
                height=20,
                line=dict(color='#D5D8DC', width=0.8)
            ),
            columnwidth=[0.28, 0.22, 0.50]
        )
        
        fig.add_trace(table_trace)
        
        # Update layout - exact date range from Excel (1-Jun to 31-Oct)
        x_min = dates.min()
        x_max = dates.max()
        
        fig.update_layout(
            title=dict(
                text=junction_name,
                x=0.5,
                xanchor='center',
                font=dict(size=18, family='Arial Black')
            ),
            xaxis=dict(
                title='Date',
                range=[x_min, x_max],
                showgrid=True,
                gridcolor='#E8E8E8',
                gridwidth=0.5,
                tickformat='%-d-%b',  # No leading zero for day
                dtick=86400000*3,  # Show tick every 3 days (like reference: 1-Jun, 4-Jun, 7-Jun)
                domain=[0, 0.70]  # Graph takes 70% width, leaving 30% for table on right
            ),
            yaxis=dict(
                title=dict(
                    text='Flow (MCM)',
                    font=dict(size=14, family='Arial')
                ),
                range=[0, y_max],
                showgrid=True,
                gridcolor='#E8E8E8',
                gridwidth=0.5,
                tick0=0,
                dtick=0.5,
                domain=[0, 1.0]  # Full height
            ),
            plot_bgcolor='#FAFAFA',
            paper_bgcolor='white',
            hovermode='x unified',
            height=700,
            margin=dict(l=80, r=20, t=80, b=60),
            showlegend=False  # Using custom table on right side
        )
        
        # Save as HTML and PNG
        output_html = f'availability_charts/{junction_name}_plotly.html'
        output_png = f'availability_charts/{junction_name}_plotly.png'
        
        fig.write_html(output_html)
        fig.write_image(output_png, width=1800, height=700, scale=2)
        
        print(f"  [OK] Saved: {output_html}")
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")

print(f"\n{'='*60}")
print(f"[SUCCESS] Generated {len(all_junctions)} charts")
print(f"{'='*60}")
print(f"\nAll charts saved in: availability_charts/")
print(f"HTML files: {len(all_junctions)} interactive charts")
print(f"PNG files: {len(all_junctions)} static images")

