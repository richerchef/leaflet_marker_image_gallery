import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import random

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

# Parameters
sensors = [f"Sensor {chr(65+i)}" for i in range(10)]  # Sensor A to J
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
num_periods_per_sensor = 5

data = []

for sensor in sensors:
    for _ in range(num_periods_per_sensor):
        # Random start between Jan and Dec
        period_start = start_date + timedelta(days=random.randint(0, 330))
        # Random duration (5–30 days)
        duration = timedelta(days=random.randint(5, 30))
        period_end = period_start + duration
        # Clip to max year end
        period_end = min(period_end, end_date)
        # Random coverage between 30% and 100%
        coverage = round(np.random.uniform(0.3, 1.0), 2)

        data.append({
            'Sensor': sensor,
            'Start': period_start,
            'End': period_end,
            'Coverage': coverage
        })

df = pd.DataFrame(data)

# Assign color by threshold
def coverage_color(cov):
    if cov < 0.5:
        return 'red'
    elif cov < 0.7:
        return 'orange'
    elif cov < 0.9:
        return 'yellowgreen'
    else:
        return 'green'

df['Color'] = df['Coverage'].apply(coverage_color)

# Compute average coverage per sensor for legend label
avg_cov = df.groupby('Sensor')['Coverage'].mean().reset_index()
avg_cov['CoverageLabel'] = avg_cov['Coverage'].apply(lambda c: f"{c*100:.1f}%")
df = df.merge(avg_cov[['Sensor', 'CoverageLabel']], on='Sensor', how='left')
df['LegendLabel'] = df.apply(lambda row: f"{row['Sensor']} ({row['CoverageLabel']})", axis=1)

# Sort y-axis alphabetically or by avg coverage
df['Sensor'] = pd.Categorical(df['Sensor'], categories=sorted(df['Sensor'].unique()), ordered=True)

# Plot
fig = px.timeline(
    df,
    x_start='Start',
    x_end='End',
    y='Sensor',
    color='Color',
    color_discrete_map='identity',
    hover_data={'Coverage': ':.0%'}
)

fig.update_yaxes(autorange='reversed')
fig.update_layout(
    title="Sensor Coverage Timeline - 2024",
    height=700,
    margin=dict(t=60, b=20),
    legend_title_text='Sensors (Avg Coverage)'
)

# Update legend labels and groupings to avoid duplicates
seen = set()
for trace in fig.data:
    sensor_name = trace.y[0]
    label = df[df['Sensor'] == sensor_name]['LegendLabel'].iloc[0]
    trace.name = label
    trace.legendgroup = label
    if label not in seen:
        trace.showlegend = True
        seen.add(label)
    else:
        trace.showlegend = False

fig.show()
