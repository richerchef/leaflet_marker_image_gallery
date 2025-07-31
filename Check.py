quality_checks = [
    {
        "id": "completeness",
        "title": "Completeness",
        "metric_label": "Completeness %",
        "data": [{"column": "id", "value": 98.5}, {"column": "region", "value": 95.2}],
        "icon": "📏"
    },
    {
        "id": "uniqueness",
        "title": "Uniqueness",
        "metric_label": "Uniqueness %",
        "data": [{"column": "id", "value": 99.7}, {"column": "order_id", "value": 100}],
        "icon": "🔐"
    }
]

html = template.render(
    params=params,
    quality_checks=quality_checks,
    plotly_json=plot_json,
    ag_data=json.dumps(ag_data)
)


import pandas as pd
import plotly.express as px

# Input data
df = pd.DataFrame({
    'Sensor': ['Sensor A', 'Sensor A', 'Sensor B', 'Sensor B', 'Sensor C'],
    'Start': pd.to_datetime([
        '2025-01-01', '2025-01-08',
        '2025-01-02', '2025-01-12',
        '2025-01-05'
    ]),
    'End': pd.to_datetime([
        '2025-01-07', '2025-01-14',
        '2025-01-10', '2025-01-18',
        '2025-01-20'
    ]),
    'Coverage': [0.4, 0.9, 0.6, 0.85, 0.95]
})

# Assign color based on thresholds
def coverage_color(c):
    if c < 0.5:
        return 'red'
    elif c < 0.7:
        return 'orange'
    elif c < 0.9:
        return 'yellowgreen'
    else:
        return 'green'

df['Color'] = df['Coverage'].apply(coverage_color)

# Calculate average per sensor
avg_cov = df.groupby('Sensor')['Coverage'].mean().reset_index()
avg_cov['CoverageLabel'] = avg_cov['Coverage'].apply(lambda c: f"{c * 100:.1f}%")

# Merge back so we can use in legend names
df = df.merge(avg_cov[['Sensor', 'CoverageLabel']], on='Sensor', how='left')

# Add overall row
overall_start = df['Start'].min()
overall_end = df['End'].max()
overall_coverage = df['Coverage'].mean()
overall_label = f"{overall_coverage * 100:.1f}%"
df = pd.concat([
    pd.DataFrame({
        'Sensor': ['All Sensors'],
        'Start': [overall_start],
        'End': [overall_end],
        'Coverage': [overall_coverage],
        'Color': [coverage_color(overall_coverage)],
        'CoverageLabel': [overall_label]
    }),
    df
], ignore_index=True)

# Plot
fig = px.timeline(
    df,
    x_start='Start',
    x_end='End',
    y='Sensor',
    color='Color',
    color_discrete_map='identity',
    hover_data={'Coverage': ':.0%'},
)

fig.update_yaxes(autorange='reversed')
fig.update_layout(height=500, title='Sensor Coverage Timeline')

# Assign legend labels and grouping
seen = set()
for trace in fig.data:
    sensor_name = trace.y[0]
    label = df[df['Sensor'] == sensor_name]['CoverageLabel'].iloc[0]
    legend_name = f"{sensor_name} ({label})"
    trace.name = legend_name
    trace.legendgroup = legend_name

    # Only show legend once per sensor
    if legend_name not in seen:
        trace.showlegend = True
        seen.add(legend_name)
    else:
        trace.showlegend = False

fig.show()
