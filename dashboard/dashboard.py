import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi untuk membaca dataset
@st.cache_data
def load_data():
    customers = pd.read_csv("data/customers.csv")
    orderitems = pd.read_csv("data/orderitems.csv")
    orders = pd.read_csv("data/orders.csv")
    products = pd.read_csv("data/products.csv")
    product_translate = pd.read_csv("data/producttranslate.csv")
    return customers, orderitems, orders, products, product_translate

# Fungsi untuk membersihkan dataset
def clean_data(orders, products, product_translate):
    orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'], errors='coerce')
    orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'], errors='coerce')
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'], errors='coerce')
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
    products = products.merge(product_translate, on="product_category_name", how="left")
    return orders, products

# Fungsi analisis data umum
def data_summary(data, dataset_name):
    st.write(f"### {dataset_name} Summary (Setelah Cleaning)")
    st.write(data.describe(include='all'))
    st.write("### Missing Values")
    st.write(data.isna().sum())
    st.write("### Duplikasi Data")
    st.write(f"Jumlah duplikasi: {data.duplicated().sum()}")
    st.write("### Cuplikan Data")
    st.write(data.head())

# Fungsi untuk menghitung produk terpopuler
def popular_products(orderitems, products):
    merged_data = orderitems.merge(products, on='product_id', how='inner')
    top_products = merged_data['product_category_name_english'].value_counts().head(10)
    return top_products

# Fungsi untuk menghitung rata-rata waktu pengiriman
def shipping_analysis(orders):
    valid_orders = orders.dropna(subset=['order_delivered_carrier_date', 'order_delivered_customer_date'])
    valid_orders['delivery_time'] = (
        valid_orders['order_delivered_customer_date'] - valid_orders['order_delivered_carrier_date']
    ).dt.days
    avg_delivery_time = valid_orders['delivery_time'].mean()
    return avg_delivery_time, valid_orders

# Fungsi visualisasi
def plot_bar(data, title, xlabel, ylabel, color="skyblue"):
    fig, ax = plt.subplots()
    data.plot(kind='bar', color=color, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig

def plot_histogram(data, title, xlabel, ylabel, bins=20, color="green"):
    fig, ax = plt.subplots()
    sns.histplot(data, bins=bins, kde=True, ax=ax, color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig

# Load dan bersihkan data
customers, orderitems, orders, products, product_translate = load_data()
orders, products = clean_data(orders, products, product_translate)

# Layout aplikasi
st.title("Dashboard Analisis E-Commerce")
st.markdown("""
Selamat datang di **Dashboard Analisis E-Commerce**!  
Dashboard ini membantu Anda memahami berbagai aspek dari aktivitas penjualan dan pengiriman.  
Gunakan menu di samping untuk navigasi.
""")

# Sidebar menu
menu = st.sidebar.radio("Pilih Menu", [
    "Overview", 
    "Summary Dataset", 
    "Analisis Produk Terpopuler", 
    "Analisis Pengiriman", 
    "Kesimpulan"
])

# Menu Overview
if menu == "Overview":
    st.subheader("Tahap Analisis Data")
    st.markdown("""
    **Tahapan yang dilakukan dalam analisis ini meliputi:**
    1. **Data Wrangling**: Pembersihan dan persiapan dataset.
    2. **Exploratory Data Analysis**:
       - Analisis produk terpopuler.
       - Analisis waktu pengiriman.
    3. **Kesimpulan**: Menyusun temuan utama untuk mendukung pengambilan keputusan bisnis.
    """)

# Menu Summary Dataset
elif menu == "Summary Dataset":
    dataset = st.selectbox("Pilih Dataset", ["Customers", "Order Items", "Orders", "Products"])
    if dataset == "Customers":
        data_summary(customers, "Customers")
    elif dataset == "Order Items":
        data_summary(orderitems, "Order Items")
    elif dataset == "Orders":
        data_summary(orders, "Orders")
    elif dataset == "Products":
        data_summary(products, "Products")

# Menu Analisis Produk Terpopuler
elif menu == "Analisis Produk Terpopuler":
    st.subheader("Analisis Produk Terpopuler")
    top_products = popular_products(orderitems, products)
    st.markdown("**Top 10 Produk Terpopuler Berdasarkan Kategori:**")
    st.bar_chart(top_products)
    fig = plot_bar(top_products, "Top 10 Produk Terpopuler", "Kategori Produk", "Jumlah Pemesanan")
    st.pyplot(fig)

# Menu Analisis Pengiriman
elif menu == "Analisis Pengiriman":
    st.subheader("Analisis Waktu Pengiriman")
    avg_delivery_time, valid_orders = shipping_analysis(orders)
    st.metric(label="Rata-rata Waktu Pengiriman (hari)", value=round(avg_delivery_time, 2))
    fig = plot_histogram(
        valid_orders['delivery_time'],
        "Distribusi Waktu Pengiriman (Carrier ke Customer)",
        "Hari",
        "Jumlah Pengiriman"
    )
    st.pyplot(fig)

# Menu Kesimpulan
elif menu == "Kesimpulan":
    st.subheader("Kesimpulan")
    st.markdown("### Ringkasan Visualisasi")
    
    # 1. Produk Terpopuler
    st.markdown("#### Produk Terpopuler")
    top_products = popular_products(orderitems, products)
    st.bar_chart(top_products)
    
    # 2. Distribusi Waktu Pengiriman
    st.markdown("#### Distribusi Waktu Pengiriman")
    avg_delivery_time, valid_orders = shipping_analysis(orders)
    fig = plot_histogram(
        valid_orders['delivery_time'],
        "Distribusi Waktu Pengiriman (Carrier ke Customer)",
        "Hari",
        "Jumlah Pengiriman"
    )
    st.pyplot(fig)

    # Kesimpulan
    st.markdown("""
    **Kesimpulan Akhir**:
    - **Produk Populer**: Kategori tertentu memiliki permintaan lebih tinggi, seperti elektronik, kecantikan, dan rumah tangga.
    - **Pengiriman**: Rata-rata waktu pengiriman dari carrier ke pelanggan adalah **8,88 hari**.
    """)

# Footer
st.sidebar.markdown("""
**Dibuat oleh:**  
Indi Bagus Prasetyo  
**Email:** endang.saefulloh@gmail.com  
""")
