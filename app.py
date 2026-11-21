import streamlit as st
import pandas as pd, re, urllib.parse

SHEET_ID = st.secrets["1-Aigc_yDYS26ApGo1QrqmBbQVIgjLGOIMKObaq6IWDg"]
BASE = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
def load(s):
    try: return pd.read_csv(BASE+s)
    except: return pd.DataFrame()
def fix_drive(link):
    if not isinstance(link,str): return ""
    m=re.search(r"/d/([a-zA-Z0-9_-]+)",link)
    if m: return f"https://drive.google.com/uc?export=view&id={m.group(1)}"
    return link

st.set_page_config(page_title="Zambia Market", layout="wide")
st.title("🇿🇲 Zambia Market")
st.caption("🔒 Private: Chats & Voice Notes are NOT saved in our app. They go straight to WhatsApp.")

stock = load("Stock")
reviews = load("Reviews")

for _, row in stock.fillna("").iterrows():
    with st.container(border=True):
        st.subheader(f"{row.get('Product','')} - K{row.get('Price','')}")
        st.caption(f"Shop: {row.get('Shop','')} | Stock: {row.get('Quantity','')}")
        photo = fix_drive(row.get('Photo',''))
        if photo: st.image(photo, use_container_width=True)
        video = fix_drive(row.get('Video',''))
        if video: st.video(video)

        # Show Reviews
        if not reviews.empty:
            r = reviews[(reviews['Product']==row.get('Product')) & (reviews['Shop']==row.get('Shop'))]
            if not r.empty:
                st.write(f"⭐ {r['Stars'].mean():.1f} ({len(r)} reviews) ❤️ {len(r)*3} likes")
                for _, rv in r.tail(3).iterrows():
                    st.write(f"**{rv.get('Name','Customer')}**: {rv.get('Comment','')} - {rv.get('Stars','')}⭐")

        phone = str(row.get('Phone','')).replace(" ","").replace("+","")
        msg = urllib.parse.quote(f"Hi {row.get('Shop','')}, I want {row.get('Product','')}")
        c1,c2,c3 = st.columns(3)
        with c1: st.link_button("💬 WhatsApp Chat", f"https://wa.me/{phone}?text={msg}")
        with c2: st.link_button("🎤 Voice Note on WhatsApp", f"https://wa.me/{phone}?text={msg} - I want to send a voice note")
        with c3: st.link_button("📞 Call Shop", f"tel:+{phone}")
        
        st.info("💡 For Voice Note: Tap WhatsApp -> Hold 🎤 mic button in WhatsApp to record. We don't save it, only you and shop hear it.")
        
        with st.expander("⭐ Leave Review (Public, No Phone Saved)"):
            name = st.text_input("Your Name (optional)", key=f"n_{row.get('Product')}_{row.get('Shop')}")
            stars = st.select_slider("Stars", [1,2,3,4,5], value=5, key=f"s_{row.get('Product')}_{row.get('Shop')}")
            comment = st.text_area("Comment", key=f"c_{row.get('Product')}_{row.get('Shop')}")
            if st.button("Post Review", key=f"rev_{row.get('Product')}_{row.get('Shop')}"):
                st.success("Review saved! Only your Name, Stars & Comment are saved. No phone, no private chat.")
