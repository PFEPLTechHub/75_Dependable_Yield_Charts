import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the output Excel file
df = pd.read_excel('daily_75pct_dependable_all_junctions.xlsx')

print(f"Creating chart with {len(df)} data points and {len(df.columns)-1} junctions...")

# Get junction columns
junction_columns = [col for col in df.columns if col != 'date']

# Create a single figure
plt.figure(figsize=(16, 9))

# Generate distinct colors for each line
colors = plt.cm.tab20(np.linspace(0, 1, len(junction_columns)))

# Plot each junction as a separate line
for idx, junction in enumerate(junction_columns):
    plt.plot(df['date'], df[junction], 
             marker='o', 
             label=junction, 
             linewidth=2.5, 
             markersize=5,
             color=colors[idx],
             alpha=0.8)

# Formatting
plt.xlabel('Date', fontsize=14, fontweight='bold')
plt.ylabel('75% Dependable Yield (in units)', fontsize=14, fontweight='bold')
plt.title('75% Dependable Yield - All Junctions (First 3 Years: 1975-1977)', 
          fontsize=16, fontweight='bold', pad=20)

# Add grid
plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right', fontsize=11)
plt.yticks(fontsize=11)

# Add legend outside the plot area
plt.legend(bbox_to_anchor=(1.02, 1), 
           loc='upper left', 
           fontsize=9, 
           frameon=True,
           fancybox=True,
           shadow=True)

# Set background color
plt.gca().set_facecolor('#FAFAFA')

# Tight layout to prevent label cutoff
plt.tight_layout()

# Save the chart
output_file = '75_percent_dependable_chart.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\nChart saved as: {output_file}")

# Display the chart
plt.show()

print("\nChart created successfully!")
print(f"Single chart with all {len(junction_columns)} junctions plotted together")

