import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

# Page Configuration
st.set_page_config(page_title="Hotel Booking Dashboard", layout="wide")

# Load Data
@st.cache_data

def load_data():
    data = pd.read_csv('hotel_bookings.csv')
    data['reservation_status_date'] = pd.to_datetime(data['reservation_status_date'])
    data['arrival_date'] = pd.to_datetime(data['arrival_date_year'].astype(str) + '-' +
                                         data['arrival_date_month'].astype(str) + '-1')
    data['total_revenue'] = data['adr'] * (data['stays_in_week_nights'] + data['stays_in_weekend_nights'])
    return data

data = load_data()

# Sidebar Filters
st.sidebar.header("Filter the Data")
selected_year = st.sidebar.multiselect("Select Year", sorted(data['arrival_date_year'].unique()), default=data['arrival_date_year'].unique())
# Create 'month_num' from 'arrival_date_month'
month_order = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6,
               'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}

data['month_num'] = data['arrival_date_month'].map(month_order)
data['year'] = data['arrival_date_year']
data['month'] = data['arrival_date_month']
selected_month = st.sidebar.multiselect("Select Month", sorted(data['arrival_date_month'].unique()), default=data['arrival_date_month'].unique())
selected_hotel = st.sidebar.multiselect("Select Hotel", sorted(data['hotel'].unique()), default=data['hotel'].unique())
selected_customer = st.sidebar.multiselect("Customer Type", sorted(data['customer_type'].unique()), default=data['customer_type'].unique())

# Apply Filters
filtered_data = data[
    (data['arrival_date_year'].isin(selected_year)) &
    (data['arrival_date_month'].isin(selected_month)) &
    (data['hotel'].isin(selected_hotel)) &
    (data['customer_type'].isin(selected_customer))
]

# KPIs
st.title("Hotel Booking Dashboard")

st.markdown("### Key Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"{filtered_data['total_revenue'].sum():,.2f} €")
col2.metric("Total Bookings", f"{filtered_data.shape[0]:,}")
col3.metric("Avg Lead Time", f"{filtered_data['lead_time'].mean():.1f} Days")
col4.metric("Cancellation Rate", f"{filtered_data['is_canceled'].mean()*100:.2f}%")

# Lead Time Distribution
st.markdown("### Distribution of Lead Time")
plt.figure(figsize=(10, 4))
sns.histplot(filtered_data['lead_time'], bins=50, kde=True, color='#2e68ab')
plt.xlabel("Lead Time")
plt.ylabel("Frequency")
plt.grid(True, linestyle='--', alpha=0.7)
st.pyplot(plt)

# Box Plot: Lead Time vs Reservation Status
st.markdown("### Lead Time by Reservation Status")
plt.figure(figsize=(10, 4))
sns.boxplot(data=filtered_data, x='reservation_status', y='lead_time', palette='Blues')
plt.grid(axis='y', linestyle='--', alpha=0.6)
st.pyplot(plt)

# Scatter Plot: Lead Time vs Total Revenue
st.markdown("### Lead Time vs Total Revenue")
fig = px.scatter(filtered_data, x='lead_time', y='total_revenue', color='is_canceled',
                 color_discrete_map={0: 'green', 1: 'red'},
                 labels={'is_canceled': 'Canceled'})
st.plotly_chart(fig, use_container_width=True)

# Monthly Trend of Successful and Canceled Bookings
st.markdown("### Monthly Booking Trends")
data['month_num'] = pd.to_datetime(data['arrival_date_month'], format='%B').dt.month
monthly = filtered_data.groupby(['arrival_date_year', 'month_num']).agg({
    'is_canceled': ['count', 'sum']
}).reset_index()
monthly.columns = ['year', 'month', 'total_bookings', 'cancellations']
monthly['successful'] = monthly['total_bookings'] - monthly['cancellations']
monthly = monthly.sort_values(['year', 'month'])

fig2 = px.line(monthly, x='month', y='successful', color='year', markers=True,
               labels={'successful': 'Successful Bookings', 'month': 'Month'},
               title='Monthly Successful Bookings by Year')
st.plotly_chart(fig2, use_container_width=True)

# Correlation Matrix
st.markdown("### Correlation Matrix")
corr = filtered_data.select_dtypes(include=['float64', 'int64']).corr()
plt.figure(figsize=(12, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", square=True, linewidths=0.5)
plt.title("Correlation Heatmap")
st.pyplot(plt)
