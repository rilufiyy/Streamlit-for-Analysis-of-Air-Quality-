import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Importing graph_objects for custom heatmap

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("air_quality_clean.csv")
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df['season'] = pd.cut(df['month'], bins=[0, 3, 6, 9, 12], labels=['Winter', 'Spring', 'Summer', 'Autumn'])
    df['day_name'] = df['datetime'].dt.day_name()
    return df

# Function to create time series plot
def create_time_series_plot(df, parameter, granularity):
    if granularity == "Hourly":
        df_grouped = df.groupby('datetime')[parameter].mean().reset_index()
        x = 'datetime'
    elif granularity == "Daily":
        df_grouped = df.groupby(df['datetime'].dt.date)[parameter].mean().reset_index()
        x = 'datetime'
    elif granularity == "Monthly":
        df_grouped = df.groupby([df['datetime'].dt.year, df['datetime'].dt.month])[parameter].mean().reset_index()
        df_grouped['date'] = pd.to_datetime(df_grouped[['datetime', 'month']].rename(columns={'datetime': 'year'}))
        x = 'date'
    elif granularity == "Yearly":
        df_grouped = df.groupby(df['datetime'].dt.year)[parameter].mean().reset_index()
        x = 'datetime'
    else:  # Seasonal
        df_grouped = df.groupby('season')[parameter].mean().reset_index()
        x = 'season'

    fig = px.line(df_grouped, x=x, y=parameter, title=f"{parameter} vs {granularity}")
    return fig

# Function to create box plot
def create_box_plot(df, parameter, granularity):
    if granularity == "Hourly":
        x = df['datetime'].dt.hour
        title = f"{parameter} Distribution by Hour"
    elif granularity == "Daily":
        x = df['datetime'].dt.day_name()
        title = f"{parameter} Distribution by Day of Week"
    elif granularity == "Monthly":
        x = df['datetime'].dt.month_name()
        title = f"{parameter} Distribution by Month"
    elif granularity == "Yearly":
        x = df['datetime'].dt.year
        title = f"{parameter} Distribution by Year"
    else:  # Seasonal
        x = df['season']
        title = f"{parameter} Distribution by Season"

    fig = px.box(df, x=x, y=parameter, title=title)
    return fig

# Load data
df = load_data()

# Streamlit app
st.title("Air Quality Dashboard")
st.subheader('By. Sri Lutfiya Dwiyeni')

# Sidebar for selecting parameters
st.sidebar.header("Select Parameters")
parameter = st.sidebar.selectbox("Choose Parameter", ["TEMP", "DEWP", "PRES"], key="parameter_select")
time_granularity = st.sidebar.selectbox("Choose Time Granularity", ["Hourly", "Daily", "Monthly", "Yearly", "Seasonal"], key="granularity_select")

# Main content
st.header(f"{parameter} Analysis")

# Time series plot
st.subheader(f"{parameter} Trend ({time_granularity})")
time_series_fig = create_time_series_plot(df, parameter, time_granularity)
st.plotly_chart(time_series_fig)

# Box plot
st.subheader(f"{parameter} Distribution ({time_granularity})")
box_fig = create_box_plot(df, parameter, time_granularity)
st.plotly_chart(box_fig)

# Heatmap for each category
st.subheader(f"Heatmap: Average {parameter} by Day of Week and Season")
heatmap_data = df.pivot_table(values=parameter, index='day_name', columns='season', aggfunc='mean')

# Create a heatmap with annotations
fig_heatmap_category = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale='Cividis',  # Updated color scale
    colorbar=dict(title=f'Average {parameter}'),
    text=heatmap_data.values,  # Adding text annotations
    hoverinfo='text'  # Show text on hover
))

# Add text annotations to the heatmap
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        fig_heatmap_category.add_annotation(
            x=heatmap_data.columns[j],
            y=heatmap_data.index[i],
            text=f"{heatmap_data.values[i][j]:.2f}",  # Format number to 2 decimal places
            showarrow=False,
            font=dict(color='white')  # Change the color if needed for better visibility
        )

fig_heatmap_category.update_layout(
    title=f"Average {parameter} by Day of Week and Season",
    xaxis_title="Season",
    yaxis_title="Day of Week"
)
st.plotly_chart(fig_heatmap_category)

# Histograms
st.subheader("Histograms")
col1, col2, col3 = st.columns(3)
with col1:
    fig_hist_temp = px.histogram(df, x="TEMP", title="Temperature Distribution")
    st.plotly_chart(fig_hist_temp)
with col2:
    fig_hist_dewp = px.histogram(df, x="DEWP", title="Dew Point Distribution")
    st.plotly_chart(fig_hist_dewp)
with col3:
    fig_hist_pres = px.histogram(df, x="PRES", title="Pressure Distribution")
    st.plotly_chart(fig_hist_pres)

# Bar Chart
st.subheader(f"Average {parameter} by Season")
season_avg = df.groupby('season')[parameter].mean().reset_index()
fig_bar = px.bar(season_avg, x='season', y=parameter, title=f"Average {parameter} by Season")
st.plotly_chart(fig_bar)