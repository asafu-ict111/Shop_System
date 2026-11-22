import streamlit as st
import pandas as pd
from datetime import datetime
import re

st.set_page_config(page_title="Online Shopping", page_icon="🛒")

SHEET_ID = "1-Aigc_yDYS26ApGo1QrqmBbQVIgjLGOIMKObaq6IWDg"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Stock"
PAY_NUMBER = "0778162582"
PAY_NAME = "Hamainza"
PAY_AMOUNT = 15

def expected_code(shop_number, year, month):
    # FINAL FORMULA: (Year - 2020) x Shop Number + 22 - 8 + 7 - Month
    value = (year - 2020) * shop_number + 22 - 8 + 7 - month
    return f"SHOP-{value}"

def drive_to_direct(link):
    if not link or str(link) == "nan":
        return ""
    link = str(link).strip()
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    if m:
        return f"https://drive.google.com/uc?export=view&id={m.group(1)}"
    m2 = re.search(r"id=([a-zA-Z0-9_-]+)", link)
    if m2:
        return f"https://drive.google.com/uc?export=view&id={m2.group(1)}"
    return link

def show_media(link):
    try:
        direct = drive_to_direct(link)
        if not direct or not str(direct).startswith("http"):
            return
        if any(x in str(direct).lower() for x in [".mp4", ".mov", ".webm", "video"]):
            st.video(direct)
        else:
            st.image(direct, use_container_width=True)
    except:
        return

def show_stars(avg):
    full = int(round(avg))
    return "⭐" * full + "☆" * (5 - full) + f" {avg:.1f}"

if "role" not in st.session_state:
    st.session_state.role = None
if "my_products" not in st.session_state:
    st.session_state.my_products = []
if "shop_number" not in st.session_state:
    st.session_state.shop_number = None
if "shop_name" not in st.session_state:
    st.session_state.shop_name = None
if "ratings" not in st.session_state:
    st.session_state.ratings = {}
if "daily_book" not in st.session_state:
    st.session_state.daily_book = []
if "shop_whatsapp" not in st.session_state:
    st.session_state.shop_whatsapp = ""
if "all_shop_whatsapp" not in st.session_state:
    st.session_state.all_shop_whatsapp = {}

st.title("🛒 Online Shopping")
st.subheader("Online Shop Management System")

if st.session_state.role is None:
    st.write("Who are you?")
    if st.button("👤 I'M A CUSTOMER - FREE", use_container_width=True):
        st.session_state.role = "customer"
        st.rerun()
    st.write("")
    if st.button("💼 I'M A BUSINESSMAN - K15 / Month", use_container_width=True):
        st.session_state.role = "businessman_check"
        st.rerun()
    st.caption("Customers shop FREE. Businessmen pay K15 to sell.")
    st.stop()

if st.session_state.role == "businessman_check":
    st.title("💼 Businessman Access")
    now = datetime.now()
    month_name = now.strftime("%B %Y")
    st.info(f"1. Send **K{PAY_AMOUNT}** to **{PAY_NUMBER} - {PAY_NAME}**")
    st.write(f"2. You will receive this month's code for {month_name}")
    shop_num_input = st.number_input("What is your Shop Number?", min_value=1, value=1)
    code = st.text_input("Enter this month's code:")
    if st.button("✅ ENTER WITH CODE", use_container_width=True):
        correct = expected_code(int(shop_num_input), now.year, now.month)
        if code.strip().upper() == correct:
            st.session_state.shop_number = int(shop_num_input)
            st.session_state.role = "shop_setup"
            st.rerun()
        else:
            st.error(f"Wrong code. For Shop {int(shop_num_input)} this month code is different. Pay K15 first, then enter code Hamainza sent you.")
    if st.button("⬅ Back"):
        st.session_state.role = None
        st.rerun()
    st.stop()

if st.session_state.role == "shop_setup":
    st.title("🛒 Shop Manager System")
    st.write(f"Your Shop Number is: {st.session_state.shop_number}")
    shop_name = st.text_input("What is your Shop Name? e.g. Mary's Shop")
    st.write("🟢 WhatsApp Group Link - OPTIONAL, you can leave blank:")
    st.caption("If you want customer to see photo on WhatsApp, paste link. If not, leave blank and press Enter My Shop.")
    wa_link = st.text_input("Paste WhatsApp Group Link here (OPTIONAL): e.g. https://chat.whatsapp.com/xxxx")
    if shop_name.strip() == "":
        st.info("Please enter your Shop Name above.")
    else:
        st.success(f"Welcome {shop_name} - Shop {st.session_state.shop_number}!")
        if st.button("✅ Enter My Shop", use_container_width=True):
            st.session_state.shop_name = shop_name
            st.session_state.shop_whatsapp = wa_link.strip() if wa_link else ""
            st.session_state.all_shop_whatsapp[shop_name] = st.session_state.shop_whatsapp
            st.session_state.role = "businessman"
            st.rerun()
    if st.button("⬅ Back"):
        st.session_state.role = None
        st.rerun()
    st.stop()

if st.button("⬅ Change Login / Logout"):
    st.session_state.role = None
    st.session_state.shop_name = None
    st.rerun()

if st.session_state.role == "customer":
    st.success("👤 Customer Mode - FREE Shopping")
    st.header("🛍️ Shop Now")
    all_products = []
    for p in st.session_state.my_products:
        all_products.append(p)
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]
        for idx, row in df.iterrows():
            all_products.append({
                "Product": row.get("Product","Product"),
                "Price": row.get("Price",0),
                "Stock": row.get("Stock",""),
                "Shop": row.get("Shop","Shop 1"),
                "Phone": str(row.get("Phone","")).replace(".0","").strip(),
                "Image": row.get("Image",""),
                "WhatsApp": row.get("WhatsApp","")
            })
    except:
        st.error("Could not load Sheet.")
    for p in all_products:
        pname = str(p["Product"])
        st.divider()
        show_media(p.get("Image",""))
        st.subheader(f"{pname} - K{p['Price']}")
        st.write(f"Shop: {p['Shop']} | Stock: {p['Stock']}")
        wa = str(p.get("WhatsApp","") or "").strip()
        if not wa:
            wa = str(st.session_state.all_shop_whatsapp.get(str(p["Shop"]), "") or "").strip()
        if wa.startswith("http"):
            st.link_button("🟢 View Product on WhatsApp - See Photo / Video", wa, use_container_width=True)
        ratings_list = st.session_state.ratings.get(pname, [])
        if ratings_list:
            avg = sum(ratings_list) / len(ratings_list)
            st.write(f"Rating: {show_stars(avg)} ({len(ratings_list)} ratings)")
        else:
            st.write("Rating: ☆☆☆☆☆ No ratings yet - Be first to rate!")
        qty = st.number_input(f"How many {pname} do you want?", min_value=1, value=1, key=f"qty_cust_{pname}")
        try:
            total = float(p["Price"]) * qty
        except:
            total = 0
        st.write(f"Total: **K{total}**")
        ph = str(p.get("Phone","")).strip()
        if ph and ph != "nan":
            st.link_button(f"🛒 BUY NOW - K{total} on WhatsApp", f"https://wa.me/{ph}?text=Hi {p['Shop']}, I want to BUY {qty} x {pname} = K{total}. My name is: ", key=f"buy_{pname}")
            c1, c2 = st.columns(2)
            with c1:
                st.link_button("💬 WhatsApp Chat", f"https://wa.me/{ph}?text=Hi, I want {pname}")
            with c2:
                st.link_button("📞 Call Shop", f"tel:{ph}")
        st.write("Rate this product:")
        stars = st.selectbox(f"Your rating for {pname}:", [5,4,3,2,1], format_func=lambda x: "⭐"*x, key=f"rate_{pname}")
        if st.button(f"⭐ Submit Rating", key=f"submit_rate_{pname}"):
            if pname not in st.session_state.ratings:
                st.session_state.ratings[pname] = []
            st.session_state.ratings[pname].append(stars)
            st.success(f"Thanks! You rated {pname} {stars} stars")
            st.rerun()
    st.stop()

if st.session_state.role == "businessman":
    st.success(f"💼 {st.session_state.shop_name} - Shop {st.session_state.shop_number} - Business Mode")
    if st.session_state.shop_whatsapp and str(st.session_state.shop_whatsapp).startswith("http"):
        st.write(f"🟢 Your WhatsApp Group: {st.session_state.shop_whatsapp}")
    else:
        st.caption("🟢 WhatsApp Group: Not set - OPTIONAL. You can add it later in My WhatsApp Group.")
    choice = st.selectbox("Choose:", ["View Market", "Add New Product", "My Products", "📓 Daily Business Routine", "📊 Monthly Review", "🟢 My WhatsApp Group"])

    if choice == "🟢 My WhatsApp Group":
        st.header("🟢 My WhatsApp Group - OPTIONAL")
        st.write("Paste your group link here if you want customer to see photo on WhatsApp. You can leave blank or delete it anytime.")
        new_wa = st.text_input("WhatsApp Group Link (OPTIONAL):", value=st.session_state.shop_whatsapp)
        if st.button("💾 Save WhatsApp Link", use_container_width=True):
            st.session_state.shop_whatsapp = new_wa.strip() if new_wa else ""
            st.session_state.all_shop_whatsapp[st.session_state.shop_name] = st.session_state.shop_whatsapp
            st.success("Saved!")
            st.rerun()
        if st.session_state.shop_whatsapp and str(st.session_state.shop_whatsapp).startswith("http"):
            st.link_button("🟢 Test - Open My WhatsApp Group", st.session_state.shop_whatsapp)

    if choice == "Add New Product":
        st.header("Add New Product")
        name = st.text_input("Product Name:")
        price = st.number_input("Price (K):", min_value=0, value=0)
        stock = st.number_input("How many in stock?", min_value=0, value=0)
        phone = st.text_input("Phone (e.g 260770000000):")
        st.caption("Photo is NOT needed here. If you have WhatsApp Group, post photo there. If not, customer will just call / WhatsApp Chat you.")
        if st.button("Add Product"):
            if name and price > 0:
                st.session_state.my_products.append({
                    "Product": name, "Price": price, "Stock": stock,
                    "Shop": st.session_state.shop_name, "Phone": phone,
                    "Image": "", "WhatsApp": st.session_state.shop_whatsapp
                })
                st.success(f"{name} added!")
            else:
                st.warning("Enter Product Name and Price")

    if choice == "My Products":
        st.header("My Products - Business Only")
        st.write("To delete, press 🗑️ Delete under the product you don't want.")
        if len(st.session_state.my_products) == 0:
            st.write("You have not added any product yet.")
        # Use list copy with index so delete works
        for idx, p in enumerate(list(st.session_state.my_products)):
            st.divider()
            st.subheader(f"{p['Product']} - K{p['Price']}")
            st.write(f"Shop: {p['Shop']} | Stock: {p['Stock']}")
            if st.session_state.shop_whatsapp and str(st.session_state.shop_whatsapp).startswith("http"):
                st.link_button("🟢 View Product on WhatsApp", st.session_state.shop_whatsapp)
            rlist = st.session_state.ratings.get(str(p["Product"]), [])
            if rlist:
                st.write(f"Rating: {show_stars(sum(rlist)/len(rlist))} ({len(rlist)} ratings)")
            else:
                st.write("Rating: No ratings yet")
            if st.button(f"🗑️ Delete {p['Product']}", key=f"del_{idx}_{p['Product']}"):
                st.session_state.my_products.pop(idx)
                st.success(f"Deleted {p['Product']}")
                st.rerun()

    if choice == "View Market":
        st.header("View Market - Business View")
        for p in st.session_state.my_products:
            st.divider()
            st.subheader(f"{p['Product']} - K{p['Price']}")
            st.write(f"Shop: {p['Shop']} | Stock: {p['Stock']}")
            if st.session_state.shop_whatsapp and str(st.session_state.shop_whatsapp).startswith("http"):
                st.link_button("🟢 View Product on WhatsApp", st.session_state.shop_whatsapp)
            rlist = st.session_state.ratings.get(str(p["Product"]), [])
            if rlist:
                st.write(f"Rating: {show_stars(sum(rlist)/len(rlist))} ({len(rlist)} ratings)")
        try:
            df = pd.read_csv(SHEET_URL)
            df.columns = [c.strip() for c in df.columns]
            for idx, row in df.iterrows():
                name2 = row.get("Product", "Product")
                st.divider()
                show_media(row.get("Image",""))
                st.subheader(f"{name2} - K{row.get('Price','')}")
                st.write(f"Shop: {row.get('Shop','')} | Stock: {row.get('Stock','')}")
                wa2 = str(row.get("WhatsApp","") or "").strip()
                if wa2.startswith("http"):
                    st.link_button("🟢 View Product on WhatsApp", wa2)
                rlist2 = st.session_state.ratings.get(str(name2), [])
                if rlist2:
                    st.write(f"Rating: {show_stars(sum(rlist2)/len(rlist2))} ({len(rlist2)} ratings)")
                else:
                    st.write("Rating: No ratings yet")
        except:
            st.error("Could not load Sheet.")

    if choice == "📓 Daily Business Routine":
        st.header("📓 Daily Business Routine")
        st.write(f"Shop: {st.session_state.shop_name} - Shop {st.session_state.shop_number}")
        st.write("Save what happened today. Customer CANNOT see this, only you.")
        date_pick = st.date_input("Date:", value=datetime.now().date())
        item_sold = st.text_input("What did you sell today? e.g. Soya chunks, Smart shoe")
        sales = st.number_input("Money IN - Sales today (K):", min_value=0, value=0)
        expenses = st.number_input("Money OUT - Expenses today (K): e.g. transport, stock", min_value=0, value=0)
        note = st.text_area("Note / Routine: e.g. Bought 10 bags, Paid rent, Customer ordered 5 shoes")
        if st.button("💾 Save Today's Routine", use_container_width=True):
            st.session_state.daily_book.append({
                "date": str(date_pick),
                "shop": st.session_state.shop_name,
                "shop_number": st.session_state.shop_number,
                "item": item_sold,
                "sales": sales,
                "expenses": expenses,
                "profit": sales - expenses,
                "note": note
            })
            st.success(f"Saved! {date_pick} - Profit: K{sales - expenses}")
            st.rerun()
        st.divider()
        st.subheader("My Saved Days - Latest First")
        my_days = [d for d in st.session_state.daily_book if d["shop_number"] == st.session_state.shop_number]
        if not my_days:
            st.write("No days saved yet. Save today above.")
        for d in reversed(my_days):
            st.write(f"**{d['date']}** - {d['item']}")
            st.write(f"Sales: K{d['sales']} | Expenses: K{d['expenses']} | Profit: **K{d['profit']}**")
            if d['note']:
                st.write(f"Note: {d['note']}")
            st.write("---")

    if choice == "📊 Monthly Review":
        st.header("📊 Monthly Review")
        st.write(f"Shop: {st.session_state.shop_name}")
        month_pick = st.selectbox("Which Month?", ["2026-11", "2026-12", "2027-01", "2027-02", "2027-03"])
        my_days = [d for d in st.session_state.daily_book if d["shop_number"] == st.session_state.shop_number and str(d["date"]).startswith(month_pick)]
        total_sales = sum(d["sales"] for d in my_days)
        total_exp = sum(d["expenses"] for d in my_days)
        total_profit = total_sales - total_exp
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Sales", f"K{total_sales}")
        with c2:
            st.metric("Total Expenses", f"K{total_exp}")
        with c3:
            st.metric("Total Profit", f"K{total_profit}")
        st.write(f"Days saved in {month_pick}: **{len(my_days)} days**")
        if not my_days:
            st.info("No routine saved for this month yet. Go to Daily Business Routine and save.")
        for d in my_days:
            st.write(f"**{d['date']}** - {d['item']} | Sales K{d['sales']} | Expenses K{d['expenses']} | Profit K{d['profit']}")
            if d['note']:
                st.write(f"Note: {d['note']}")
