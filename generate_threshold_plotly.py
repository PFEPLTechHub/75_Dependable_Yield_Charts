import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
import numpy as np

# Read the Excel file
input_file = '251112 For Graphs (1).xlsx'
df_reduced = pd.read_excel(input_file, sheet_name='Reduced Flows')
df_base = pd.read_excel(input_file, sheet_name='Base Flows')

# Convert Date column to datetime
df_reduced['Date'] = pd.to_datetime(df_reduced['Date'], format='%d-%b')
df_base['Date'] = pd.to_datetime(df_base['Date'], format='%d-%b')

# Get all junction names (excluding Date column)
all_junctions = [col for col in df_reduced.columns if col != 'Date']

print(f"Found {len(all_junctions)} junctions to process")
print(f"Junctions: {', '.join(all_junctions[:5])}..." if len(all_junctions) > 5 else f"Junctions: {', '.join(all_junctions)}")

# Process all junctions
for junction_idx, junction_name in enumerate(all_junctions, 1):
    print(f"\n[{junction_idx}/{len(all_junctions)}] Generating chart for: {junction_name}")
    
    # Prepare data
    dates = df_reduced['Date']
    values_reduced = df_reduced[junction_name]
    values_base = df_base[junction_name]

# Calculate max value for Y-axis range
max_value = max(values_reduced.max(), values_base.max())
y_max = max(6.0, max_value * 1.1)  # At least 6.0, or 110% of max value

# Define thresholds in 0.1 MCM increments (up to 3.0)
thresholds = np.arange(0.1, 3.01, 0.1)

# Define color ranges for legend (matching the reference image)
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
    """Return First/Mid/Last based on day of month"""
    day = date.day
    if day <= 10:
        return "First"
    elif day <= 20:
        return "Mid"
    else:
        return "Last"

# Calculate capacity statistics for legend table
capacity_stats = []
key_thresholds = [3.0, 2.5, 2.0, 1.5, 1.0, 0.5]

for threshold in key_thresholds:
    above_threshold = values_reduced >= threshold
    days_count = above_threshold.sum()
    
    if days_count > 0:
        indices = above_threshold[above_threshold].index
        first_date = dates.iloc[indices[0]]
        last_date = dates.iloc[indices[-1]]
        
        # Format as "First/Mid/Last Mon - First/Mid/Last Mon"
        start_pos = get_month_position(first_date)
        end_pos = get_month_position(last_date)
        start_month = first_date.strftime('%b')
        end_month = last_date.strftime('%b')
        
        period = f"{start_pos} {start_month} - {end_pos} {end_month}"
    else:
        period = "N/A"
    
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
        
        # Add Y-axis label
        fig.add_annotation(
            x=dates.min() - timedelta(days=2),
            y=y_position,
            text=f'{threshold:.1f}',
            showarrow=False,
            xanchor='right',
            font=dict(size=10)
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

# Create beautiful table-style legend
table_x = 0.02
table_y = 0.96
row_height = 0.028
col_widths = [0.055, 0.035, 0.115]  # Capacity, Days, Period

total_width = sum(col_widths)
total_height = row_height * 7  # Header + 6 rows

# Draw table background
fig.add_shape(
    type="rect",
    x0=table_x,
    y0=table_y - total_height,
    x1=table_x + total_width,
    y1=table_y,
    xref='paper',
    yref='paper',
    fillcolor='white',
    line=dict(color='#2C3E50', width=2),
    layer='below'
)

# Draw header background
fig.add_shape(
    type="rect",
    x0=table_x,
    y0=table_y - row_height,
    x1=table_x + total_width,
    y1=table_y,
    xref='paper',
    yref='paper',
    fillcolor='#34495E',
    line_width=0,
    layer='below'
)

# Add vertical dividers
x_pos = table_x + col_widths[0]
for i in range(2):
    fig.add_shape(
        type="line",
        x0=x_pos,
        y0=table_y - total_height,
        x1=x_pos,
        y1=table_y,
        xref='paper',
        yref='paper',
        line=dict(color='#BDC3C7', width=1),
        layer='below'
    )
    x_pos += col_widths[i + 1]

# Add table header text
fig.add_annotation(
    text='<b>Capacity</b>',
    x=table_x + col_widths[0]/2,
    y=table_y - row_height/2,
    xref='paper',
    yref='paper',
    showarrow=False,
    font=dict(size=10, family='Arial', color='white'),
    xanchor='center',
    yanchor='middle'
)

fig.add_annotation(
    text='<b>Days</b>',
    x=table_x + col_widths[0] + col_widths[1]/2,
    y=table_y - row_height/2,
    xref='paper',
    yref='paper',
    showarrow=False,
    font=dict(size=10, family='Arial', color='white'),
    xanchor='center',
    yanchor='middle'
)

fig.add_annotation(
    text='<b>Period</b>',
    x=table_x + col_widths[0] + col_widths[1] + col_widths[2]/2,
    y=table_y - row_height/2,
    xref='paper',
    yref='paper',
    showarrow=False,
    font=dict(size=10, family='Arial', color='white'),
    xanchor='center',
    yanchor='middle'
)

# Add table rows
for i, stat in enumerate(capacity_stats):
    row_y = table_y - (i + 1.5) * row_height
    
    # Capacity cell (with colored background) - draw background shape
    fig.add_shape(
        type="rect",
        x0=table_x,
        y0=row_y - row_height/2.2,
        x1=table_x + col_widths[0],
        y1=row_y + row_height/2.2,
        xref='paper',
        yref='paper',
        fillcolor=stat['color'],
        line_width=0,
        layer='below'
    )
    
    # Capacity text
    fig.add_annotation(
        text=f"<b>{stat['capacity']:.1f}</b>",
        x=table_x + col_widths[0]/2,
        y=row_y,
        xref='paper',
        yref='paper',
        showarrow=False,
        font=dict(size=10, family='Arial', color='white'),
        xanchor='center',
        yanchor='middle'
    )
    
    # Days cell
    fig.add_annotation(
        text=f"<b>{stat['days']}</b>",
        x=table_x + col_widths[0] + col_widths[1]/2,
        y=row_y,
        xref='paper',
        yref='paper',
        showarrow=False,
        font=dict(size=9, family='Arial', color='#2C3E50'),
        xanchor='center',
        yanchor='middle'
    )
    
    # Period cell
    fig.add_annotation(
        text=stat['period'],
        x=table_x + col_widths[0] + col_widths[1] + col_widths[2]/2,
        y=row_y,
        xref='paper',
        yref='paper',
        showarrow=False,
        font=dict(size=8.5, family='Arial', color='#2C3E50'),
        xanchor='center',
        yanchor='middle'
    )
    
    # Add subtle horizontal line after each row (except last)
    if i < len(capacity_stats) - 1:
        fig.add_shape(
            type="line",
            x0=table_x,
            y0=table_y - (i + 2) * row_height,
            x1=table_x + total_width,
            y1=table_y - (i + 2) * row_height,
            xref='paper',
            yref='paper',
            line=dict(color='#ECF0F1', width=1),
            layer='below'
        )

# Update layout
x_min = dates.min() - timedelta(days=3)
x_max = dates.max() + timedelta(days=1)

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
        gridwidth=0.5
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
        dtick=0.5
    ),
    plot_bgcolor='#FAFAFA',
    paper_bgcolor='white',
    hovermode='x unified',
    height=700,
    margin=dict(l=80, r=100, t=80, b=60),
    showlegend=False  # Using custom table-style legend instead
)

# Save as HTML and PNG
output_html = f'availability_charts/{junction_name}_plotly.html'
output_png = f'availability_charts/{junction_name}_plotly.png'

fig.write_html(output_html)
fig.write_image(output_png, width=1600, height=700, scale=2)

print(f"[SUCCESS] Plotly chart saved:")
print(f"  HTML: {output_html}")
print(f"  PNG: {output_png}")
print("No overflow - bars aligned with proper padding.")

