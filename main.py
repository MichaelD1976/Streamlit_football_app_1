# https://docs.streamlit.io/
# https://docs.streamlit.io/develop/api-reference

import streamlit as st
import pandas as pd
import altair as alt


# Path to your downloaded image (assuming it's a JPEG format)
image_path = 'C:/Users/MikeD/Streamlit_football-app_1/images/football_bw.jpg'

# Custom CSS style to position image
css = """
<style>
.top-left {
    position: absolute;
    top: 10px;
    left: 10px;
}
</style>
"""

# Display the image using Markdown with CSS
st.markdown(css, unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="top-left">
        <img src="{image_path}" width="100" alt="Top Left Image">
    </div>
    """,
    unsafe_allow_html=True
)


# Function to load data based on selected league
@st.cache_data
def load_data(league):
    filename_mapping = {
        'Germany Bundesliga': 'ger1_2022-23.csv',
        'England Premier League': 'eng1_2022-23.csv',
        'France Ligue 1': 'fra1_2022-23.csv',
        'Italy Serie A': 'italy1_2022-23.csv',
        'Spain La Liga': 'spain1_2022-23.csv'
    }
    file_path = filename_mapping.get(league)
    if file_path:
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            st.error(f"File {file_path} not found.")
            return pd.DataFrame()  # Return an empty DataFrame on error
    else:
        st.error(f"League '{league}' not found in filename mapping.")
        return pd.DataFrame()  # Return an empty DataFrame if league not found

# # Page title and header
# st.markdown(
#     """
#     <style>
#     .reportview-container {
#         background: #f0f0f0; /* Light grey background */
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # Displaying an image
# st.image('football_img.webp', caption='', width=300)

# Streamlit app title
st.markdown("<h1 style='text-align: center; color: blue;'>Football Stats by League</h1>", unsafe_allow_html=True)

# Dropdown selection for league
league = st.selectbox('Select League', [
    'Germany Bundesliga',
    'England Premier League',
    'France Ligue 1',
    'Italy Serie A',
    'Spain La Liga'
])

# Load data based on selected league
data = load_data(league)

# Ensure required metric columns are present in the dataset
home_team_metrics = ['FTHG', 'HC', 'HF', 'HY', 'HR']
away_team_metrics = ['FTAG', 'AC', 'AF', 'AY', 'AR']

missing_metrics = [metric for metric in home_team_metrics + away_team_metrics if metric not in data.columns]

if missing_metrics:
    st.error(f"The following metrics are missing from the dataset: {', '.join(missing_metrics)}")
else:
    # Compute averages for home team metrics
    avg_home_metrics = {}
    for metric in home_team_metrics:
        avg_home_metrics[metric] = round(data.groupby('HomeTeam')[metric].mean().reset_index(), 2)
        avg_home_metrics[metric].columns = ['HomeTeam', f'Average_{metric}']

    # Compute averages for away team metrics
    avg_away_metrics = {}
    for metric in away_team_metrics:
        avg_away_metrics[metric] = round(data.groupby('AwayTeam')[metric].mean().reset_index(), 2)
        avg_away_metrics[metric].columns = ['AwayTeam', f'Average_{metric}']

    # Metric descriptions dictionary
    metric_descriptions = {
        'FTHG': 'Full Time Home Goals',
        'FTAG': 'Full Time Away Goals',
        'HC': 'Home Corners',
        'AC': 'Away Corners',
        'HF': 'Home Fouls',
        'AF': 'Away Fouls',
        'HY': 'Home Yellow Cards',
        'AY': 'Away Yellow Cards',
        'HR': 'Home Red Cards',
        'AR': 'Away Red Cards'
        # Add more metrics and descriptions as needed
    }

    # Dropdown selection for metric with full descriptions
    metric_options = {metric: f'{metric} - {metric_descriptions[metric]}' for metric in home_team_metrics + away_team_metrics}
    selected_metric = st.selectbox('Select Metric', list(metric_options.values()))


    # Retrieve selected metric based on shortened version
    selected_shortened_metric = next(key for key, value in metric_options.items() if value == selected_metric)

    # Access the appropriate DataFrame and column name based on selected metric
    if selected_shortened_metric in home_team_metrics:
        selected_df = avg_home_metrics[selected_shortened_metric]
        y_axis = f'Average_{selected_shortened_metric}'
        group_column = 'HomeTeam'
    elif selected_shortened_metric in away_team_metrics:
        selected_df = avg_away_metrics[selected_shortened_metric]
        y_axis = f'Average_{selected_shortened_metric}'
        group_column = 'AwayTeam'

    # Calculate overall average of the selected metric
    overall_avg = data[selected_shortened_metric].mean()

    # Create a bar chart with Altair
    chart = alt.Chart(selected_df).mark_bar().encode(
        x=alt.X(group_column, sort=None),
        y=alt.Y(y_axis)
    ).properties(
        width=600,
        height=400,
        title=f'Average {selected_shortened_metric} by {group_column}'
    )

    # Display the chart in the Streamlit app
    st.altair_chart(chart, use_container_width=True)

    # Display overall average below the chart
    st.write(f'Overall Average {selected_shortened_metric}: {overall_avg:.2f}')


    # Section for selecting individual match
    st.header('Select Individual Match')
    selected_home_team = st.selectbox('Select Home Team', sorted(data['HomeTeam'].unique()))
    selected_away_team = st.selectbox('Select Away Team', sorted(data['AwayTeam'].unique()))

    if st.button('Show Match Metrics'):
        match_data = data[(data['HomeTeam'] == selected_home_team) & (data['AwayTeam'] == selected_away_team)]
        st.subheader(f'Match Metrics: {selected_home_team} vs {selected_away_team}')
        st.write(match_data)
