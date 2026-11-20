import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import re

st.set_page_config(page_title="AWH Shop App", page_icon="🛒")
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-Aigc_yDYS26ApGo1QrqmBbQVIgjLGOIMKObaq6IWDg/edit?usp=drivesdk"

def load_stock():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Stock", ttl=0)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Shop","Product","Price","Quantity"])
def load_sales():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Sales", ttl=0)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Shop","Product","Quantity","Total","Date"])
def save_stock(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="Stock", data=df)
def save_sales(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="Sales", data=df)

def get_shop_number(shop_text):
    nums = re.findall(r'\d+', str(shop_text))
    return int(nums[0]) if nums else 1

def get_expected_code(shop_text):
    now = datetime.now()
    month = now.month
    year = now.year
    shop_num = get_shop_number(shop_text)
    code_num = shop_num * month + (year - 2020) + 7
    return f"SHOP-{code_num}"

st.title("🛒 Online Shop Management")
shop = st.text_input("Enter Your Shop Number:", value="Shop 1")
code = st.text_input("Enter Unlock Code:", type="password")

if code == "FREE-NOV":
    pass
else:
    expected = get_expected_code(shop)
    if code != expected:
        st.warning("Shop is locked. Pay K50 to get your code. MoMo: 0778162582")
        st.info("Ask Hamainza for this month's code. Do NOT share your code.")
        st.stop()

st.success(f"Welcome! to your ! {shop} shop Management system!")
stock_df = load_stock()
sales_df = load_sales()
my_stock = stock_df[stock_df["Shop"] == shop] if not stock_df.empty else pd.DataFrame(columns=["Shop","Product","Price","Quantity"])
my_sales = sales_df[sales_df["Shop"] == shop] if not sales_df.empty else pd.DataFrame(columns=["Shop","Product","Quantity","Total","Date"])

choice = st.selectbox("Choose:", ["See Stock", "Add New Product", "Sell to a Customer", "Remove / Edit Product", "See My Sales"])

if choice == "See Stock":
    st.subheader("Stock")
    if my_stock.empty:
        st.write("No stock yet. Add a product.")
    else:
        st.dataframe(my_stock[["Product","Price","Quantity"]], use_container_width=True)

if choice == "Add New Product":
    st.subheader("Add New Product")
    name = st.text_input("Product Name:")
    price = st.number_input("Price (K):", min_value=0, value=0)
    qty = st.number_input("How many in stock?", min_value=0, value=0)
    if st.button("Add Product"):
        if name:
            new_row = pd.DataFrame([{"Shop": shop, "Product": name, "Price": price, "Quantity": qty}])
            updated = pd.concat([stock_df, new_row], ignore_index=True)
            save_stock(updated)
            st.success(f"{name} added! Saved in Google Sheets forever.")
            st.rerun()
        else:
            st.error("Type product name first")

if choice == "Sell to a Customer":
    st.subheader("Sell to a Customer")
    if my_stock.empty:
        st.write("No stock to sell. Add stock first.")
    else:
        prod = st.selectbox("Choose Product:", my_stock["Product"].tolist())
        prod_row = my_stock[my_stock["Product"] == prod].iloc[0]
        st.write(f"Price: K{prod_row['Price']} | In Stock: {prod_row['Quantity']}")
        sell_qty = st.number_input("How many to sell?", min_value=1, max_value=int(prod_row['Quantity']), value=1)
        total = float(prod_row['Price']) * sell_qty
        st.subheader(f"Total: K{total}")
        if st.button("Complete Sale"):
            idx = stock_df[(stock_df["Shop"]==shop) & (stock_df["Product"]==prod)].index[0]
            stock_df.at[idx, "Quantity"] = int(stock_df.at[idx, "Quantity"]) - sell_qty
            save_stock(stock_df)
            new_sale = pd.DataFrame([{"Shop": shop, "Product": prod, "Quantity": sell_qty, "Total": total, "Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}])
            updated_sales = pd.concat([sales_df, new_sale], ignore_index=True)
            save_sales(updated_sales)
            st.success(f"Sold! K{total} saved.")
            st.rerun()

if choice == "Remove / Edit Product":
    st.subheader("Remove / Edit Product")
    if my_stock.empty:
        st.write("No stock to remove.")
    else:
        prod = st.selectbox("Choose Product to Remove/Edit:", my_stock["Product"].tolist())
        prod_row = my_stock[my_stock["Product"] == prod].iloc[0]
        st.write(f"Now: Price K{prod_row['Price']} | Qty: {prod_row['Quantity']}")
        new_price = st.number_input("New Price (K):", min_value=0, value=int(prod_row['Price']))
        new_qty = st.number_input("New Quantity:", min_value=0, value=int(prod_row['Quantity']))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Product"):
                idx = stock_df[(stock_df["Shop"]==shop) & (stock_df["Product"]==prod)].index[0]
                stock_df.at[idx, "Price"] = new_price
                stock_df.at[idx, "Quantity"] = new_qty
                save_stock(stock_df)
                st.success(f"{prod} updated!")
                st.rerun()
        with col2:
            if st.button("DELETE Product ❌"):
                updated = stock_df[~((stock_df["Shop"]==shop) & (stock_df["Product"]==prod))]
                save_stock(updated)
                st.success(f"{prod} deleted from Google Sheets!")
                st.rerun()

if choice == "See My Sales":
    st.subheader("My Sales - Forever Saved")
    if my_sales.empty:
        st.write("No sales yet.")
    else:
        st.dataframe(my_sales, use_container_width=True)
        st.subheader(f"Total Sales: K{my_sales['Total'].sum()}")
