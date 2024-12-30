import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

# Title
st.title("Dashboard Analisis Data E-Commerce")

# Description
st.write("Visualisasi data dari berbagai dataset terkait e-commerce.")

# Load datasets
data_path = "../data/"
customers_df = pd.read_csv(data_path + "customers.csv")
orderitems_df = pd.read_csv(data_path + "orderitems.csv")
orderpays_df = pd.read_csv(data_path + "orderpays.csv")
orderreviews_df = pd.read_csv(data_path + "orderreviews.csv")
products_df = pd.read_csv(data_path + "products.csv")
product_translate_df = pd.read_csv(data_path + "producttranslate.csv")

# Merge product translations
if "product_category_name" in products_df.columns and "product_category_name" in product_translate_df.columns:
    products_df = products_df.merge(product_translate_df, on="product_category_name", how="left")
else:
    st.error("Kolom 'product_category_name' tidak ditemukan dalam dataset produk atau terjemahan produk.")

if "product_id" in orderitems_df.columns and "product_id" in products_df.columns:
    orderitems_df = orderitems_df.merge(products_df, on="product_id", how="left")
else:
    st.error("Kolom 'product_id' tidak ditemukan dalam dataset order items atau produk.")

# Show a sample of each dataset
st.header("Preview Dataset")
with st.expander("Customers Dataset"):
    st.write(customers_df.head())

with st.expander("Order Items Dataset"):
    st.write(orderitems_df.head())

with st.expander("Order Payments Dataset"):
    st.write(orderpays_df.head())

with st.expander("Order Reviews Dataset"):
    st.write(orderreviews_df.head())

# Visualization 1: Top Categories
st.header("Visualisasi 1: Top 10 Produk Terlaris Berdasarkan Nama (Bahasa Inggris)")
if "product_category_name_english" in orderitems_df.columns:
    top_products = orderitems_df['product_category_name_english'].value_counts().head(10)
    fig1, ax1 = plt.subplots()
    sns.barplot(x=top_products.values, y=top_products.index, ax=ax1)
    ax1.set_title("Top 10 Produk Terlaris")
    ax1.set_xlabel("Jumlah Pesanan")
    ax1.set_ylabel("Nama Kategori Produk")
    st.pyplot(fig1)
else:
    st.error("Kolom 'product_category_name_english' tidak ditemukan dalam dataset.")

# Visualization 2: Pola Keterlambatan Berdasarkan Lokasi
st.header("Visualisasi 2: Pola Keterlambatan Berdasarkan Lokasi (State)")
orders_df = pd.read_csv(data_path + "orders.csv")
orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'], errors='coerce')
orders_df['order_estimated_delivery_date'] = pd.to_datetime(orders_df['order_estimated_delivery_date'], errors='coerce')
customers_df['customer_state'] = customers_df['customer_state'].fillna('Unknown')

# Gabungkan informasi lokasi pelanggan dari customers_df ke orders_df
if "customer_id" in orders_df.columns and "customer_id" in customers_df.columns:
    orders_df = pd.merge(orders_df, customers_df[['customer_id', 'customer_state']], on='customer_id', how='left')
else:
    st.error("Kolom 'customer_id' tidak ditemukan dalam dataset orders atau customers.")

# Hitung keterlambatan pengiriman
if 'order_delivered_customer_date' in orders_df.columns and 'order_estimated_delivery_date' in orders_df.columns:
    orders_df['delivery_delay_days'] = (
        orders_df['order_delivered_customer_date'] - orders_df['order_estimated_delivery_date']
    ).dt.days
else:
    st.error("Kolom tanggal pengiriman tidak ditemukan dalam dataset orders.")

# Analisis keterlambatan berdasarkan lokasi
if 'delivery_delay_days' in orders_df.columns and 'customer_state' in orders_df.columns:
    delay_by_state = orders_df.groupby('customer_state')['delivery_delay_days'].mean().sort_values()

    # Visualisasi
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.barplot(x=delay_by_state.index, y=delay_by_state.values, ax=ax2)
    ax2.set_title("Rata-Rata Keterlambatan Pengiriman per Lokasi")
    ax2.set_xlabel("State")
    ax2.set_ylabel("Rata-Rata Keterlambatan (Hari)")
    plt.xticks(rotation=45)
    st.pyplot(fig2)
else:
    st.error("Data keterlambatan pengiriman atau lokasi tidak tersedia untuk visualisasi.")

# Visualization 3: Hubungan Waktu Pengiriman dengan Skor Ulasan
st.header("Visualisasi 3: Hubungan Waktu Pengiriman dengan Skor Ulasan")
if 'order_id' in orders_df.columns and 'order_id' in orderitems_df.columns:
    orders_reviews = pd.merge(orders_df, orderitems_df, on='order_id', how='inner')
    if 'order_id' in orderreviews_df.columns and 'review_score' in orderreviews_df.columns:
        orders_reviews = pd.merge(orders_reviews, orderreviews_df[['order_id', 'review_score']], on='order_id', how='left')

        # Pastikan kolom tanggal sesuai tipe datetime
        orders_reviews['order_purchase_timestamp'] = pd.to_datetime(orders_reviews['order_purchase_timestamp'], errors='coerce')

        if 'order_delivered_customer_date' in orders_reviews.columns and 'order_purchase_timestamp' in orders_reviews.columns:
            orders_reviews['delivery_time_days'] = (
                orders_reviews['order_delivered_customer_date'] - orders_reviews['order_purchase_timestamp']
            ).dt.days

            fig3, ax3 = plt.subplots(figsize=(12, 6))
            sns.boxplot(data=orders_reviews, x='review_score', y='delivery_time_days', ax=ax3)
            ax3.set_title("Hubungan Waktu Pengiriman dengan Skor Ulasan")
            ax3.set_xlabel("Skor Ulasan")
            ax3.set_ylabel("Waktu Pengiriman (Hari)")
            st.pyplot(fig3)
        else:
            st.error("Kolom tanggal pengiriman atau pembelian tidak tersedia atau salah format.")
    else:
        st.error("Kolom 'review_score' atau 'order_id' tidak tersedia dalam dataset ulasan.")
else:
    st.error("Kolom 'order_id' tidak ditemukan dalam dataset orders atau order items.")