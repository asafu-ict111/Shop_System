import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import re
import urllib.parse

st.set_page_config(page_title="Online Shop Management System", page_icon="🛒")
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-Aigc_yDYS26ApGo1QrqmBbQVIgjLGOIMKObaq6IWDg/edit?usp=drivesdk"

# ---------- HELPERS - CHECKED ----------
def fix_drive_link(link):
    """Convert Google Drive share link to direct photo link. If not Drive, return as-is."""
    if not link or not isinstance(link, str):
        return ""
    link = link.strip()
    try:
        # Format 1: https://drive.google.com/file/d/FILE_ID/view...
        if "drive.google.com/file/d/" in link:
            file_id = link.split("/d/")[1].split("/")[0].split("?")[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        # Format 2: https://drive.google.com/open?id=FILE_ID
        if "drive.google.com/open?id=" in link:
            file_id = link.split("id=")[1].split("&")[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        return link
    except:
        return link

def show_photo(photo_link):
    """Show photo directly from link. Never crash if link is bad."""
    if not photo_link or not isinstance(photo_link, str):
        st.write("📦 No photo")
        return
    photo_link = photo_link.strip()
    if len(photo_link) < 10 or "http" not in photo_link:
        st.write("📦 No photo")
        return
    try:
        st.image(fix_drive_link(photo_link), width=200)
    except:
        st.write("📦 Photo link broken")

def safe_int(val, default=0):
    try:
        if pd.isna(val):
            return default
        return int(float(val))
    except:
        return default

def safe_float(val, default=0.0):
    try:
        if pd.isna(val):
            return default
        return float(val)
    except:
        return default

def clean_phone(phone):
    """Return last 9 digits for WhatsApp, e.g. 0778162582 -> 778162582"""
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) >= 9:
        return digits[-9:]
    return digits

# ---------- LOAD / SAVE ----------
def load_stock():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Stock", ttl=0)
        df = df.dropna(how="all")
        for c in ["Shop","Product","Price","Quantity","Photo","Phone"]:
            if c not in df.columns:
                df[c] = ""
        return df
    except:
        return pd.DataFrame(columns=["Shop","Product","Price","Quantity","Photo","Phone"])

def load_sales():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Sales", ttl=0)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Shop","Product","Quantity","Total","Date"])

def load_orders():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Orders", ttl=0)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Shop","Product","Quantity","Total","Date","CustomerName","CustomerPhone","Location","Status","ShopPhone"])

def save_stock(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="Stock", data=df)
def save_sales(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="Sales", data=df)
def save_orders(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="Orders", data=df)

def get_shop_number(shop_text):
    nums = re.findall(r'\d+', str(shop_text))
    return int(nums[0]) if nums else 1

def get_expected_code(shop_text):
    now = datetime.now()
    shop_num = get_shop_number(shop_text)
    code_num = shop_num * now.month + (now.year - 2020) + 7
    return f"SHOP-{code_num}"

# ---------- TOP ----------
st.title("🛒 Online Shop Management System")
st.write("Buy from home | Sell from home")
mode = st.radio("Who are you?", ["🛍️ I'm a Customer - Buy FREE", "💼 I'm a Businessman - Manage My Shop"], horizontal=True)

# =========================================================
# CUSTOMER - FREE, NO CODE
# =========================================================
if mode == "🛍️ I'm a Customer - Buy FREE":
    st.header("🛍️ Shop From Home - FREE")
    stock_df = load_stock()
    if stock_df.empty:
        st.write("No products yet. Check back soon.")
        st.stop()
    search = st.text_input("🔍 Search product (e.g. soya, rice, sugar):")
    if search:
        stock_df = stock_df[stock_df["Product"].astype(str).str.lower().str.contains(search.lower(), na=False)]
    if stock_df.empty:
        st.write("No product found for that search.")
        st.stop()

    for idx, row in stock_df.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                show_photo(row.get("Photo", ""))
            with col2:
                st.subheader(f"{row['Product']}")
                st.write(f"**Price: K{safe_float(row['Price'])}** | In Stock: {safe_int(row['Quantity'])}")
                st.write(f"Shop: {row['Shop']} | 📞 {row.get('Phone','')}")
                with st.expander(f"Buy {row['Product']}"):
                    c_name = st.text_input("Your Name:", key=f"name_{idx}")
                    c_phone = st.text_input("Your Phone Number:", key=f"phone_{idx}")
                    c_loc = st.text_input("Delivery Location / Pick Up:", key=f"loc_{idx}")
                    max_qty = safe_int(row['Quantity'], 1)
                    if max_qty < 1:
                        max_qty = 1
                    qty = st.number_input("How many?", min_value=1, max_value=max_qty, value=1, key=f"qty_{idx}")
                    total = safe_float(row['Price']) * qty
                    st.write(f"**Total: K{total}**")
                    if st.button(f"Place Order - K{total}", key=f"order_{idx}"):
                        if not c_name.strip() or not c_phone.strip():
                            st.error("Type your name and phone first")
                        else:
                            try:
                                orders_df = load_orders()
                                new_order = pd.DataFrame([{
                                    "Shop": row['Shop'], "Product": row['Product'], "Quantity": qty,
                                    "Total": total, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "CustomerName": c_name.strip(), "CustomerPhone": c_phone.strip(), "Location": c_loc.strip(),
                                    "Status": "New", "ShopPhone": row.get('Phone','')
                                }])
                                save_orders(pd.concat([orders_df, new_order], ignore_index=True))
                                # Reduce stock
                                all_stock = load_stock()
                                mask = (all_stock["Shop"] == row['Shop']) & (all_stock["Product"] == row['Product'])
                                if mask.any():
                                    s_idx = all_stock[mask].index[0]
                                    all_stock.at[s_idx, "Quantity"] = safe_int(all_stock.at[s_idx, "Quantity"]) - qty
                                    save_stock(all_stock)
                                st.success("Order placed! Shop will contact you.")
                                shop_phone_clean = clean_phone(row.get('Phone',''))
                                if len(shop_phone_clean) == 9:
                                    msg = f"Hi {row['Shop']}, I want to order {qty} x {row['Product']} - Total K{total}. My name is {c_name}, Location: {c_loc}"
                                    wa_link = f"https://wa.me/260{shop_phone_clean}?text={urllib.parse.quote(msg)}"
                                    st.link_button("💬 Chat Shop on WhatsApp", wa_link)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Order failed, try again. Error: {e}")
    st.stop()

# =========================================================
# BUSINESSMAN - K15/MONTH
# =========================================================
st.header("💼 Businessman Dashboard - K15/Month")
shop = st.text_input("Enter Your Shop Number:", value="Shop 1")
code = st.text_input("Enter Unlock Code:", type="password")

if code != "FREE-NOV":
    expected = get_expected_code(shop)
    if code != expected:
        st.warning("App is locked. Pay K15/month to get your code. MoMo: 0778162582")
        st.info("Ask Hamainza for this month's code. Do NOT share your code.")
        st.info("Customers are FREE - they don't need a code. Only businessmen pay.")
        st.stop()

st.success(f"Welcome! {shop} Management system!")
stock_df = load_stock()
sales_df = load_sales()
orders_df = load_orders()
my_stock = stock_df[stock_df["Shop"] == shop] if not stock_df.empty else pd.DataFrame(columns=["Shop","Product","Price","Quantity","Photo","Phone"])
my_sales = sales_df[sales_df["Shop"] == shop] if not sales_df.empty else pd.DataFrame(columns=["Shop","Product","Quantity","Total","Date"])
my_orders = orders_df[orders_df["Shop"] == shop] if not orders_df.empty else pd.DataFrame(columns=["Shop","Product","Quantity","Total","Date","CustomerName","CustomerPhone","Location","Status","ShopPhone"])

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
c1,c2,c3,c4,c5 = st.columns(5)
if c1.button("🏠 Dashboard"): st.session_state.page = "Dashboard"
if c2.button("📦 My Stock"): st.session_state.page = "Stock"
if c3.button("➕ Add Product"): st.session_state.page = "Add"
if c4.button("🛒 Orders"): st.session_state.page = "Orders"
if c5.button("💰 Sell"): st.session_state.page = "Sell"
choice = st.session_state.page

if choice == "Dashboard":
    st.subheader("📊 My Sales")
    today_str = datetime.now().strftime("%Y-%m-%d")
    month_str = datetime.now().strftime("%Y-%m")
    daily_total = 0.0
    monthly_total = 0.0
    if not my_orders.empty:
        my_orders = my_orders.copy()
        my_orders["Total_num"] = pd.to_numeric(my_orders["Total"], errors="coerce").fillna(0)
        my_orders["Date_str"] = my_orders["Date"].astype(str)
        daily_total += my_orders[my_orders["Date_str"].str.contains(today_str, na=False)]["Total_num"].sum()
        monthly_total += my_orders[my_orders["Date_str"].str.contains(month_str, na=False)]["Total_num"].sum()
    if not my_sales.empty:
        my_sales = my_sales.copy()
        my_sales["Total_num"] = pd.to_numeric(my_sales["Total"], errors="coerce").fillna(0)
        my_sales["Date_str"] = my_sales["Date"].astype(str)
        daily_total += my_sales[my_sales["Date_str"].str.contains(today_str, na=False)]["Total_num"].sum()
        monthly_total += my_sales[my_sales["Date_str"].str.contains(month_str, na=False)]["Total_num"].sum()
    colA, colB, colC = st.columns(3)
    colA.metric("Today Sales", f"K{daily_total}")
    colB.metric("This Month Sales", f"K{monthly_total}")
    colC.metric("Total Orders", f"{len(my_orders)}")
    st.write("---")
    st.subheader("Recent Orders")
    if my_orders.empty:
        st.write("No orders yet.")
    else:
        st.dataframe(my_orders.sort_values("Date", ascending=False), use_container_width=True)

if choice == "Stock":
    st.subheader("My Stock")
    if my_stock.empty:
        st.write("No stock yet. Add a product.")
    else:
        for _, r in my_stock.iterrows():
            with st.container(border=True):
                show_photo(r.get("Photo",""))
                st.write(f"**{r['Product']}** - K{safe_float(r['Price'])} | Qty: {safe_int(r['Quantity'])} | Phone: {r.get('Phone','')}")

if choice == "Add":
    st.subheader("Add New Product")
    st.info("How to get photo link: Upload photo to Google Drive / Google Photos -> Share -> Copy Link -> Paste here. Customers will see the PHOTO, not the link.")
    name = st.text_input("Product Name:")
    price = st.number_input("Price (K):", min_value=0, value=0)
    qty = st.number_input("How many in stock?", min_value=0, value=0)
    phone = st.text_input("Your Shop Phone / WhatsApp Number (e.g. 0778162582):")
    photo_link_raw = st.text_input("Paste Photo Link (from Google Drive / Photos):")
    if photo_link_raw:
        st.write("Preview - this is what customer will see:")
        show_photo(photo_link_raw)
    if st.button("Add Product"):
        if not name.strip():
            st.error("Type product name first")
        else:
            photo_link = fix_drive_link(photo_link_raw)
            new_row = pd.DataFrame([{"Shop": shop, "Product": name.strip(), "Price": price, "Quantity": qty, "Photo": photo_link, "Phone": phone.strip()}])
            updated = pd.concat([stock_df, new_row], ignore_index=True)
            save_stock(updated)
            st.success(f"{name} added! Customers can now see its photo.")
            st.rerun()

if choice == "Orders":
    st.subheader("My Orders - From Customers")
    if my_orders.empty:
        st.write("No orders yet.")
    else:
        st.dataframe(my_orders.sort_values("Date", ascending=False), use_container_width=True)
        options = []
        for _, r in my_orders.iterrows():
            options.append(f"{r['Date']} - {r['Product']} - {r['CustomerName']} - {r.get('Status','New')}")
        sel = st.selectbox("Select order to mark Delivered:", options)
        if st.button("Mark as Delivered ✅"):
            for idx2, r in orders_df.iterrows():
                label = f"{r['Date']} - {r['Product']} - {r['CustomerName']} - {r.get('Status','New')}"
                if label == sel and r['Shop'] == shop:
                    orders_df.at[idx2, "Status"] = "Delivered"
            save_orders(orders_df)
            st.success("Marked Delivered")
            st.rerun()

if choice == "Sell":
    st.subheader("Sell to a Customer (Walk-in)")
    if my_stock.empty:
        st.write("No stock to sell. Add stock first.")
    else:
        prod = st.selectbox("Choose Product:", my_stock["Product"].tolist())
        prod_row = my_stock[my_stock["Product"] == prod].iloc[0]
        st.write(f"Price: K{safe_float(prod_row['Price'])} | In Stock: {safe_int(prod_row['Quantity'])}")
        max_q = safe_int(prod_row['Quantity'], 1)
        if max_q < 1:
            st.error("Out of stock")
        else:
            sell_qty = st.number_input("How many to sell?", min_value=1, max_value=max_q, value=1)
            total = safe_float(prod_row['Price']) * sell_qty
            st.subheader(f"Total: K{total}")
            if st.button("Complete Sale"):
                idx = stock_df[(stock_df["Shop"]==shop) & (stock_df["Product"]==prod)].index[0]
                stock_df.at[idx, "Quantity"] = safe_int(stock_df.at[idx, "Quantity"]) - sell_qty
                save_stock(stock_df)
                new_sale = pd.DataFrame([{"Shop": shop, "Product": prod, "Quantity": sell_qty, "Total": total, "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}])
                updated_sales = pd.concat([sales_df, new_sale], ignore_index=True)
                save_sales(updated_sales)
                st.success(f"Sold! K{total} saved.")
                st.rerun()

# Edit / Delete
with st.expander("Remove / Edit Product"):
    if my_stock.empty:
        st.write("No stock to edit.")
    else:
        prod = st.selectbox("Choose Product to Remove/Edit:", my_stock["Product"].tolist(), key="edit_prod")
        prod_row = my_stock[my_stock["Product"] == prod].iloc[0]
        new_price = st.number_input("New Price (K):", min_value=0, value=safe_int(prod_row['Price']), key="edit_price")
        new_qty = st.number_input("New Quantity:", min_value=0, value=safe_int(prod_row['Quantity']), key="edit_qty")
        new_photo = st.text_input("New Photo Link (leave same if you don't want to change):", value=str(prod_row.get("Photo","")), key="edit_photo")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Product"):
                idx = stock_df[(stock_df["Shop"]==shop) & (stock_df["Product"]==prod)].index[0]
                stock_df.at[idx, "Price"] = new_price
                stock_df.at[idx, "Quantity"] = new_qty
                stock_df.at[idx, "Photo"] = fix_drive_link(new_photo)
                save_stock(stock_df)
                st.success(f"{prod} updated!")
                st.rerun()
        with col2:
            if st.button("DELETE Product ❌"):
                updated = stock_df[~((stock_df["Shop"]==shop) & (stock_df["Product"]==prod))]
                save_stock(updated)
                st.success(f"{prod} deleted!")
                st.rerun()
