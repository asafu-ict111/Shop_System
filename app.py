import streamlit as st
from datetime import date

st.set_page_config(page_title="Shop Management System", page_icon="🛒")
st.title("🛒 Shop Management System")

# ===== SHOP SETTINGS - GENERAL =====
shop_id = st.number_input("What is your Shop Number?", min_value=1, max_value=100, step=1)
shop_name = st.text_input("What is your Shop Name? e.g. Mary's Shop")

today = date.today()

# ===== UNLOCK CODE - NEW FORMULA WITH YEAR =====
# Formula: SHOP x MONTH + (YEAR - 2020) + 7
correct_number = shop_id * today.month + (today.year - 2020) + 7
correct_code = f"SHOP-{correct_number}"

if not shop_name:
    st.info("Please enter your Shop Name and Shop Number above.")
    st.stop()

st.write(f"Welcome to **{shop_name}** - Shop {shop_id}")
st.write(f"Today: {today}")

code = st.text_input("Enter Unlock Code (after you pay):", type="password")
if code != correct_code:
    st.warning(f"Shop {shop_id} is locked. Pay K100 to get your code for this month.")
    st.info("Send K100 to MoMo, send screenshot on WhatsApp, then you will get your code.")
    st.stop()

st.success(f"Welcome {shop_name}! Unlocked!")

# ===== PRODUCTS - Saved in memory =====
if "products" not in st.session_state:
    st.session_state.products = ["Mealie Meal", "Sugar", "Cooking Oil", "Soap"]
    st.session_state.prices = [150, 80, 120, 35]
    st.session_state.stock = [10, 10, 10, 10]
    st.session_state.sales = []

products = st.session_state.products
prices = st.session_state.prices
stock = st.session_state.stock

# ===== MENU =====
menu = st.selectbox("Choose:", ["Sell to a Customer", "Add New Product", "See Stock", "See All Customer Sales"])

if menu == "Add New Product":
    st.subheader("Add New Product")
    name = st.text_input("Product Name:")
    price = st.number_input("Price (K):", min_value=1, step=1)
    qty = st.number_input("How many in stock?", min_value=0, step=1)
    if st.button("Add Product"):
        if name:
            products.append(name)
            prices.append(price)
            stock.append(qty)
            st.success(f"{name} added!")
        else:
            st.error("Enter product name!")

elif menu == "Sell to a Customer":
    st.subheader("Sell to a Customer")
    customer = st.text_input("Customer Name?")
    total = 0
    quantities = []
    for i in range(len(products)):
        st.write(f"**{products[i]}** - Stock: {stock[i]} - K{prices[i]}")
        if stock[i] == 0:
            st.error("OUT OF STOCK!")
            quantities.append(0)
            continue
        if stock[i] < 3:
            st.warning("LOW STOCK!")
        q = st.number_input(f"How many {products[i]} did {customer} buy?", min_value=0, max_value=stock[i], step=1, key=f"q{i}")
        quantities.append(q)
        total += q * prices[i]
    
    st.write(f"### Total for {customer}: K{total}")
    if st.button("Save Receipt"):
        for i in range(len(products)):
            stock[i] -= quantities[i]
        st.session_state.sales.append(f"{today}, Shop {shop_id} - {shop_name}, {customer}, Total: K{total}")
        st.success(f"Receipt for {customer} saved!")

elif menu == "See Stock":
    st.subheader("Stock")
    for i in range(len(products)):
        st.write(f"{products[i]}: {stock[i]} left - K{prices[i]}")
        if stock[i] == 0:
            st.error("OUT OF STOCK!")
        elif stock[i] < 3:
            st.warning("LOW STOCK!")

elif menu == "See All Customer Sales":
    st.subheader("All Customer Sales")
    if len(st.session_state.sales) == 0:
        st.write("No sales yet!")
    else:
        for s in st.session_state.sales:
            st.write(s)
