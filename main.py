import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from dashboard.func import DataAnalyzer, BrazilMapPlotter
from babel.numbers import format_currency

sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("./data/all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('./data/geolocation_dataset.csv')

# Pastikan 'customer_unique_id' memang ada di dataset geolocation
if 'customer_unique_id' in geolocation.columns:
    data = geolocation.drop_duplicates(subset='customer_unique_id')
else:
    st.error("Kolom 'customer_unique_id' tidak ditemukan di dataset geolocation")

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Royan Aditya")

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    # Convert start_date and end_date to datetime64 for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

# Main
main_df = all_df[(all_df["order_approved_at"] >= start_date) & 
                 (all_df["order_approved_at"] <= end_date)]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Title
st.header("E-Commerce Dashboard")

# PERTANYAAN 1 Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

# Membuat subplot untuk barplot
fig, ax = plt.subplots(1, 2, figsize=(16, 8))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=20)
ax[0].tick_params(axis='y', labelsize=15)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=15)
ax[1].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# PERTANYAAN 2 Review Score
st.subheader("Review Score")
col1, col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index, 
            y=review_score.values, 
            order=review_score.index,
            palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
            )

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

# PERTANYAAN 3 Order Approved
# PERTANYAAN 3 Order Approved 
st.subheader("Orders Approved")

all_df = all_df[(all_df['order_approved_at'] >= start_date) & (all_df['order_approved_at'] <= end_date)]

monthly_order = all_df.resample(rule='M', on='order_approved_at').agg({
    "order_id": "size",
})
monthly_order.index = monthly_order.index.strftime('%B')
monthly_order = monthly_order.reset_index()
monthly_order.rename(columns={
    "order_id": "order_count",
}, inplace=True)
monthly_order = monthly_order.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')
month_mapping = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

monthly_order["month_numeric"] = monthly_order["order_approved_at"].map(month_mapping)
monthly_order = monthly_order.sort_values("month_numeric")
monthly_order = monthly_order.drop("month_numeric", axis=1)

col1, col2 = st.columns(2)

with col1:
    # Calculate total orders and average orders per month
    total_orders = all_df.shape[0]
    st.markdown(f"Total Orders Approved:\n{total_orders}")

with col2:
    # Average orders per month
    avg_orders_per_month = all_df.resample(rule='M', on='order_approved_at').size().mean()
    st.markdown(f"Average Orders per Month:\n{avg_orders_per_month}")

fig, ax = plt.subplots(figsize=(10, 5))
plt.plot(
    monthly_order["order_approved_at"],
    monthly_order["order_count"],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)
plt.title("Number of Orders Approved per Month", loc="center", fontsize=20)

# Set the x-ticks (month names) rotated by 45 degrees upwards
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel("Month", fontsize=14)
plt.ylabel("Order Count", fontsize=14)

# Display the plot
st.pyplot(fig)


# PERTANYAAN 4 Customer Demographic
st.subheader("Customer Demographic")
tab1, tab2 = st.tabs(["State", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette="viridis"
                    )

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)  # Memastikan fig dipakai di sini

with tab2:
    map_plot.plot()

    with st.expander("See Explanation"):
        st.write('According to the graph that has been created, there are more customers in the southeast and south. Other information, there are more customers in cities that are capitals (São Paulo, Rio de Janeiro, Porto Alegre, and others).')

st.caption('Copyright (C) Royan Aditya 2024')