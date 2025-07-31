import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Generate weekly timestamps for 2024
date_range = pd.date_range(start='2024-01-01', end='2024-12-31', freq='7D')

# Simulate random coverage values (0% to 100%)
np.random.seed(42)
coverage = np.random.uniform(0, 1, size=len(date_range))

# Create DataFrame
df = pd.DataFrame({
    'Date': date_range,
    'Coverage': coverage
})

# Duplicate last row to extend to end of time (so we can "fill" till end of year)
df = pd.concat([
    df,
    pd.DataFrame({'Date': [pd.Timestamp('2025-01-01')], 'Coverage': [coverage[-1]]})
], ignore_index=True)

# Create a step-like filled area plot
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Coverage'] * 100,  # convert to percent
    mode='lines',
    line=dict(shape='hv', width=0),  # horizontal-vertical (step)
    fill='tozeroy',
    fillcolor='rgba(0, 128, 0, 0.6)',
    name='Sensor A',
    hovertemplate='Date: %{x}<br>Coverage: %{y:.1f}%<extra></extra>'
))

# Optional: Add a line on top of fill
fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Coverage'] * 100,
    mode='lines',
    line=dict(shape='hv', color='darkgreen', width=2),
    name='',
    hoverinfo='skip',
    showlegend=False
))

# Layout
fig.update_layout(
    title='Sensor A Coverage Over Time (Weekly)',
    yaxis_title='Coverage (%)',
    xaxis_title='Date',
    yaxis_range=[0, 100],
    height=400,
    plot_bgcolor='white'
)

fig.show()
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
