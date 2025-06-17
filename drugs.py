import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="⚕️",
    layout="wide",
)

# --- DATA LOADING AND CLEANING ---
@st.cache_data  # cache for performance
def load_data(path):
    df = pd.read_csv(path)
    # parse dates
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    # drop rows missing any of these critical fields
    df.dropna(subset=['Date', 'Age', 'Sex', 'Race', 'DeathCounty'], inplace=True)
    # cast age to int and extract year
    df['Age'] = df['Age'].astype(int)
    df['Year'] = df['Date'].dt.year

    # list of drug columns (matching your CSV headers)
    drug_columns = [
        'Heroin', 'Cocaine', 'Fentanyl', 'Oxycodone', 'Oxymorphone',
        'Ethanol', 'Hydrocodone', 'Benzodiazepine', 'Methadone',
        'Amphet', 'Tramad', 'Morphine_NotHeroin'
    ]
    # convert 'Y' → 1, everything else → 0
    for col in drug_columns:
        if col in df.columns:
            df[col] = df[col].map({'Y': 1}).fillna(0).astype(int)

    return df

# load the data file (must live alongside app.py)
df = load_data('drug_deaths.csv')

# --- SIDEBAR FILTERS ---
st.sidebar.header("Dashboard Filters")

# County filter
counties = ['All'] + sorted(df['DeathCounty'].unique())
selected_county = st.sidebar.selectbox("Select County", counties)

# Age filter
min_age, max_age = int(df.Age.min()), int(df.Age.max())
selected_age = st.sidebar.slider("Select Age Range", min_age, max_age, (min_age, max_age))

# Gender filter
genders = ['All'] + df['Sex'].unique().tolist()
selected_gender = st.sidebar.selectbox("Select Gender", genders)

# apply filters
df_filtered = df[df['Age'].between(*selected_age)]
if selected_county != 'All':
    df_filtered = df_filtered[df_filtered['DeathCounty'] == selected_county]
if selected_gender != 'All':
    df_filtered = df_filtered[df_filtered['Sex'] == selected_gender]

# --- MAIN PAGE ---
st.title("⚕️ Trauma Center Analytics: Accidental Drug Deaths")
st.markdown("Insights into Connecticut accidental drug-related deaths (2012–2018).")
st.markdown("---")

# Key Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Deaths", f"{len(df_filtered):,}")
with col2:
    st.metric("Average Age", int(df_filtered['Age'].mean()))
with col3:
    st.metric("Fentanyl-Involved Deaths", int(df_filtered['Fentanyl'].sum()))

st.markdown("---")

# --- VISUALIZATIONS ---
# 1. Deaths Over Time
st.subheader("Deaths Over Time")
deaths_by_year = df_filtered.groupby('Year').size().reset_index(name='Count')
fig_time = px.line(deaths_by_year, x='Year', y='Count', markers=True,
                   labels={'Count': 'Number of Deaths', 'Year': 'Year'})
st.plotly_chart(fig_time, use_container_width=True)

# 2. Deaths by County
st.subheader("Deaths by County")
deaths_by_county = df_filtered['DeathCounty'].value_counts().reset_index()
deaths_by_county.columns = ['County', 'Count']
fig_county = px.bar(deaths_by_county.sort_values('Count', ascending=True),
                    x='Count', y='County', orientation='h',
                    labels={'Count': 'Number of Deaths', 'County': 'County'})
st.plotly_chart(fig_county, use_container_width=True)

# 3. Most Common Substances Involved
st.subheader("Most Common Substances Involved")
substances = ['Heroin', 'Cocaine', 'Fentanyl', 'Oxycodone', 'Oxymorphone',
              'Ethanol', 'Hydrocodone', 'Benzodiazepine', 'Methadone']
sub_counts = df_filtered[substances].sum().sort_values(ascending=True)
fig_subs = px.bar(x=sub_counts.values, y=sub_counts.index, orientation='h',
                  labels={'x': 'Number of Cases', 'y': 'Substance'})
st.plotly_chart(fig_subs, use_container_width=True)

# 4. Age Distribution by Gender
st.subheader("Age Distribution by Gender")
fig_age = px.histogram(df_filtered, x='Age', color='Sex', nbins=30,
                       labels={'Age': 'Age', 'Sex': 'Gender'})
st.plotly_chart(fig_age, use_container_width=True)

# --- SHOW RAW DATA ---
if st.checkbox("Show Filtered Raw Data"):
    st.dataframe(df_filtered)
