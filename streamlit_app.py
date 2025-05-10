
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="COVID-19 Global Dashboard")

# Title
st.title("🦠 COVID-19 Global Data Dashboard")
st.markdown("Data from [Our World in Data](https://ourworldindata.org/coronavirus)")

@st.cache_data
def load_data():
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    df = pd.read_csv(url, parse_dates=['date'])
    columns = [
        'iso_code', 'continent', 'location', 'date',
        'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
        'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated',
        'hosp_patients', 'icu_patients', 'population'
    ]
    df = df[columns]
    df.dropna(subset=["continent"], inplace=True)
    df.sort_values(['location', 'date'], inplace=True)
    df.fillna(method='ffill', inplace=True)
    return df

df = load_data()

# Sidebar
st.sidebar.header("Filter Data")
countries = sorted(df['location'].unique())
selected_country = st.sidebar.selectbox("Select Country", countries, index=countries.index("United States"))
date_range = st.sidebar.date_input("Date Range",
    [df['date'].min(), df['date'].max()],
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = df[(df['location'] == selected_country) & (df['date'] >= start_date) & (df['date'] <= end_date)]

# Main visualizations
st.subheader(f"COVID-19 Trends in {selected_country}")

col1, col2 = st.columns(2)

with col1:
    fig_cases = px.line(filtered_df, x='date', y='total_cases', title="Total Cases")
    st.plotly_chart(fig_cases, use_container_width=True)

with col2:
    filtered_df['death_rate'] = filtered_df['total_deaths'] / filtered_df['total_cases']
    fig_deaths = px.line(filtered_df, x='date', y='death_rate', title="Death Rate")
    st.plotly_chart(fig_deaths, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    filtered_df['vaccination_pct'] = filtered_df['people_vaccinated'] / filtered_df['population']
    fig_vax = px.line(filtered_df, x='date', y='vaccination_pct', title="Vaccination Coverage")
    st.plotly_chart(fig_vax, use_container_width=True)

with col4:
    if filtered_df['hosp_patients'].notna().sum() > 0:
        fig_hosp = px.line(filtered_df, x='date', y='hosp_patients', title="Hospitalized Patients")
        st.plotly_chart(fig_hosp, use_container_width=True)
    else:
        st.info("No hospitalization data available for this country.")

# Summary metrics
st.markdown("### Latest Stats")
latest = filtered_df.iloc[-1]
st.write(f"**Total Cases**: {int(latest['total_cases']):,}")
st.write(f"**Total Deaths**: {int(latest['total_deaths']):,}")
st.write(f"**People Vaccinated**: {int(latest['people_vaccinated']):,}")
st.write(f"**Hospitalized Patients**: {int(latest['hosp_patients']) if pd.notna(latest['hosp_patients']) else 'N/A'}")

st.markdown("---")
st.markdown("💡 *Built with Streamlit. Data: Our World in Data.*")
