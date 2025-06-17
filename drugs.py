import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="⚕️",
    layout="wide",
)

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date', 'Age', 'Sex', 'Race', 'DeathCounty'], inplace=True)
    df['Age'] = df['Age'].astype(int)
    df['Year'] = df['Date'].dt.year
    drug_columns = [
        'Heroin', 'Cocaine', 'Fentanyl', 'Oxycodone', 'Oxymorphone',
        'Ethanol', 'Hydrocodone', 'Benzodiazepine', 'Methadone',
        'Amphet', 'Tramad', 'Morphine_NotHeroin'
    ]
    for col in drug_columns:
        if col in df.columns:
            df[col] = df[col].map({'Y': 1}).fillna(0).astype(int)
    return df

df = load_data('drug_deaths.csv')

# Sidebar filters
st.sidebar.header("Dashboard Filters")
counties = ['All'] + sorted(df['DeathCounty'].unique())
selected_county = st.sidebar.selectbox("Select County", counties)
min_age, max_age = int(df.Age.min()), int(df.Age.max())
selected_age = st.sidebar.slider("Select Age Range", min_age, max_age, (min_age, max_age))
genders = ['All'] + df['Sex'].unique().tolist()
selected_gender = st.sidebar.selectbox("Select Gender", genders)

df_filtered = df[df['Age'].between(*selected_age)]
if selected_county != 'All':
    df_filtered = df_filtered[df_filtered['DeathCounty'] == selected_county]
if selected_gender != 'All':
    df_filtered = df_filtered[df_filtered['Sex'] == selected_gender]

st.title("⚕️ Trauma Center Analytics: Accidental Drug Deaths")
st.markdown("Insights into Connecticut accidental drug-related deaths (2012–2018).")

# --- Arrange everything in columns and rows to fit one page ---

# Key metrics at the top
col1, col2, col3 = st.columns(3)
col1.metric("Total Deaths", f"{len(df_filtered):,}")
col2.metric("Average Age", int(df_filtered['Age'].mean()))
col3.metric("Fentanyl-Involved Deaths", int(df_filtered['Fentanyl'].sum()))

# Charts in two rows, two columns
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# 1. Deaths Over Time
deaths_by_year = df_filtered.groupby('Year').size().reset_index(name='Count')
fig_time = px.line(deaths_by_year, x='Year', y='Count', markers=True,
                   labels={'Count': 'Number of Deaths', 'Year': 'Year'})
row1_col1.plotly_chart(fig_time, use_container_width=True)
row1_col1.caption("Deaths Over Time")

# 2. Deaths by County
deaths_by_county = df_filtered['DeathCounty'].value_counts().reset_index()
deaths_by_county.columns = ['County', 'Count']
fig_county = px.bar(deaths_by_county.sort_values('Count', ascending=True),
                    x='Count', y='County', orientation='h',
                    labels={'Count': 'Number of Deaths', 'County': 'County'})
row1_col2.plotly_chart(fig_county, use_container_width=True)
row1_col2.caption("Deaths by County")

# 3. Most Common Substances Involved
substances = ['Heroin', 'Cocaine', 'Fentanyl', 'Oxycodone', 'Oxymorphone',
              'Ethanol', 'Hydrocodone', 'Benzodiazepine', 'Methadone']
sub_counts = df_filtered[substances].sum().sort_values(ascending=True)
fig_subs = px.bar(x=sub_counts.values, y=sub_counts.index, orientation='h',
                  labels={'x': 'Number of Cases', 'y': 'Substance'})
row2_col1.plotly_chart(fig_subs, use_container_width=True)
row2_col1.caption("Most Common Substances Involved")

# 4. Age Distribution by Gender
fig_age = px.histogram(df_filtered, x='Age', color='Sex', nbins=30,
                       labels={'Age': 'Age', 'Sex': 'Gender'})
row2_col2.plotly_chart(fig_age, use_container_width=True)
row2_col2.caption("Age Distribution by Gender")

# Raw data in an expander at the bottom
with st.expander("Show Filtered Raw Data"):
    st.dataframe(df_filtered)

