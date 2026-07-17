import streamlit as st
import time
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Feast Beast | Ultimate Cloud Kitchen",
    page_icon="👹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM ULTRA-MODERN CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Feast Beast Hero Banner */
    .beast-hero {
        background: linear-gradient(135deg, #111111 0%, #ff4b2b 100%);
        padding: 50px 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(255, 75, 43, 0.15);
    }
    
    .beast-title {
        font-size: 48px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0;
    }
    
    /* Food Item Styling */
    .food-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #eef2f5;
        margin-bottom: 25px;
    }
    
    /* Food Markers */
    .tag-veg {
        color: #00b0ff;
        font-weight: 600;
        font-size: 11px;
        border: 1.5px solid #00b0ff;
        padding: 2px 8px;
        border-radius: 20px;
        text-transform: uppercase;
    }
    .tag-nonveg {
        color: #ff3d00;
        font-weight: 600;
        font-size: 11px;
        border: 1.5px solid #ff3d00;
        padding: 2px 8px;
        border-radius: 20px;
        text-transform: uppercase;
    }
    
    .beast-price {
        font-size: 20px;
        font-weight: 800;
        color: #ff4b2b;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "order_status" not in st.session_state:
    st.session_state.order_status = None

# --- FEAST BEAST CURATED MENU ---
MENU = {
    "Beast Starters (Heavy Hitters)": [
        {"id": "fb_s1", "name": "Monster Malai Tikka", "price": 369, "type": "Non-Veg", "desc": "Jumbo chicken chunks saturated in cheese, cashew melt, and cooked over blazing coal embers.", "emoji": "🔥"},
        {"id": "fb_s2", "name": "Dynamite Paneer Popper Tikka", "price": 319, "type": "Veg", "desc": "Fiery-spiced, heavily loaded cottage cheese blocks fired up with a blend of three local chilis.", "emoji": "🌶️"},
        {"id": "fb_s3", "name": "Crunchy Beast Corn Wheels", "price": 259, "type": "Veg", "desc": "Crispy fried golden corn patties packing a punch of intense garlic and pepper flakes.", "emoji": "🌽"}
    ],
    "Legendary Mains": [
        {"id": "fb_m1", "name": "Smoked Butter Chicken (The Beast Edition)", "price": 449, "type": "Non-Veg", "desc": "Tandoor charcoal-smoked pulled chicken deeply simmered in an unapologetically buttery rich gravy.", "emoji": "🍗"},
        {"id": "fb_m2", "name": "Mega Shahi Paneer Lababdar", "price": 399, "type": "Veg", "desc": "Velvety smooth, premium cashew-tomato gravy chunked up with artisan cottage cheese blocks.", "emoji": "🧀"},
        {"id": "fb_m3", "name": "Overnight Coal-Smoked Dal Makhani", "price": 349, "type": "Veg", "desc": "Black lentils slow-rendered over slow flames for an authentic, insanely creamy texture.", "emoji": "🍲"}
    ],
    "Signature Dum Biryanis": [
        {"id": "fb_b1", "name": "Beast Mode Dum Chicken Biryani", "price": 469, "type": "Non-Veg", "desc": "Spiced-to-the-bone succulent chicken leg layers baked under heavy dough sealing inside fragrant long-grain rice.", "emoji": "👑"},
        {"id": "fb_b2", "name": "Wild Forest Subz Dum Biryani", "price": 389, "type": "Veg", "desc": "Fresh seasonal greens, root vegetables, and mountain spices steamed systematically in layered pots.", "emoji": "🌿"}
    ],
    "Heavy Breads": [
        {"id": "fb_r1", "name": "Bullet Garlic Naan", "price": 89, "type": "Veg", "desc": "Leavened dynamic flour bread overloaded with minced garlic bits and doused in pure butter.", "emoji": "🫓"},
        {"id": "fb_r2", "name": "Beast-Layer Paratha", "price": 79, "type": "Veg", "desc": "Multi-layered, intensely crispy whole wheat flatbread made to tear apart.", "emoji": "🫓"}
    ]
}

# --- CART ENGINE ---
def add_item(item_id, name, price):
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]["qty"] += 1
    else:
        st.session_state.cart[item_id] = {"name": name, "price": price, "qty": 1}
    st.toast(f"Added {name} to your feast! 🔥")

def remove_item(item_id):
    if item_id in st.session_state.cart:
        if st.session_state.cart[item_id]["qty"] > 1:
            st.session_state.cart[item_id]["qty"] -= 1
        else:
            del st.session_state.cart[item_id]
        st.toast("Feast cart modified.")

# --- SIDEBAR DISPLAY ---
st.sidebar.markdown("<h1 style='color: #ff4b2b; margin-bottom: 0;'>FEAST BEAST</h1>", unsafe_allow_html=True)
st.sidebar.caption("Unapologetic Indian Flavors. Unleashed.")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "App Hub", 
    ["🔥 Unleash Menu", "🛒 Feast Cart & Checkout", "📦 Track Live Beast Delivery"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Live Beast Counter")
if st.session_state.cart:
    total_qty = sum(x["qty"] for x in st.session_state.cart.values())
    sub_val = sum(x["price"] * x["qty"] for x in st.session_state.cart.values())
    st.sidebar.metric(label="Items Selected", value=total_qty)
    st.sidebar.metric(label="Current Value", value=f"₹{sub_val}")
else:
    st.sidebar.info("The Beast is hungry. Load up your cart!")


# --- VIEW 1: UNLEASH MENU ---
if app_mode == "🔥 Unleash Menu":
    st.markdown("""
    <div class="beast-hero">
        <h1 class="beast-title">FEAST BEAST</h1>
        <p style='font-size: 18px; font-weight:300; opacity: 0.95; margin: 10px 0;'>Bold Flavors. Massive Portions. Straight From Our Monster Cloud Kitchens.</p>
        <div style='margin-top: 15px;'>
            <span style='background: #111; color:#fff; font-size:12px; padding:6px 14px; border-radius:30px; font-weight:bold;'>⭐ 4.9 Cloud Rated</span>
            <span style='background: #fff; color:#ff4b2b; font-size:12px; padding:6px 14px; border-radius:30px; font-weight:bold; margin-left:10px;'>⏱️ 30 MIN SUPERFAST DELIVERY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    menu_tabs = st.tabs(list(MENU.keys()))
    
    for tab_idx, section in enumerate(MENU.keys()):
        with menu_tabs[tab_idx]:
            st.markdown(f"### {section}")
            
            for food in MENU[section]:
                with st.container():
                    left_col, right_col = st.columns([4, 1])
                    
                    with left_col:
                        lbl_type = "tag-veg" if food["type"] == "Veg" else "tag-nonveg"
                        st.markdown(f"<span class='{lbl_type}'>{food['type']}</span>", unsafe_allow_html=True)
                        st.markdown(f"#### {food['emoji']} {food['name']}")
                        st.caption(food["desc"])
                        st.markdown(f"<span class='beast-price'>₹{food['price']}</span>", unsafe_allow_html=True)
                        
                    with right_col:
                        st.write(" ")
                        st.write(" ")
                        in_cart_qty = st.session_state.cart.get(food["id"], {}).get("qty", 0)
                        
                        if in_cart_qty > 0:
                            st.write(f"Loaded: **{in_cart_qty}**")
                            b_p, b_m = st.columns(2)
                            with b_p:
                                if st.button("➕", key=f"p_{food['id']}"):
                                    add_item(food["id"], food["name"], food["price"])
                                    st.rerun()
                            with b_m:
                                if st.button("➖", key=f"m_{food['id']}"):
                                    remove_item(food["id"])
                                    st.rerun()
                        else:
                            if st.button("Add 🔥", key=f"add_{food['id']}", use_container_width=True):
                                add_item(food["id"], food["name"], food["price"])
                                st.rerun()
                                
                st.markdown("<hr style='border:0; border-top:1px solid #f0f2f6; margin:20px 0;'>", unsafe_allow_html=True)


# --- VIEW 2: FEAST CART & CHECKOUT ---
elif app_mode == "🛒 Feast Cart & Checkout":
    st.title("🛒 Complete Your Order")
    
    if not st.session_state.cart:
        st.error("No fuel loaded in the Beast! Go grab some food from the menu first.")
    else:
        left_layout, right_layout = st.columns([3, 2])
        
        with left_layout:
            st.markdown("### 🍔 Items Locked In")
            
            for fid, data in list(st.session_state.cart.items()):
                calc_total = data["price"] * data["qty"]
                with st.container():
                    i_col1, i_col2, i_col3 = st.columns([3, 2, 2])
                    with i_col1:
                        st.markdown(f"**{data['name']}**")
                        st.caption(f"Price per block: ₹{data['price']}")
                    with i_col2:
                        st.write(f"Quantity: **{data['qty']}**")
                    with i_col3:
                        st.write(f"Total: **₹{calc_total}**")
                st.markdown("<div style='height: 1px; background-color: #eee; margin-bottom:15px;'></div>", unsafe_allow_html=True)
            
            st.markdown("### 📍 Location Coordinates")
            buyer_name = st.text_input("Beast Consumer Name", value="Vikram Malhotra")
            buyer_phone = st.text_input("Hotline Number", value="+91 91111 22222")
            buyer_address = st.text_area("Drop Zone Address", value="Penthouse B, SkyHigh Towers, Phase 5, DLF Phase 3, Gurugram, India")
            
        with right_layout:
            st.markdown("### 🧾 Financial Breakdown")
            
            sub_aggregate = sum(x["price"] * x["qty"] for x in st.session_state.cart.values())
            computed_gst = round(sub_aggregate * 0.05, 2)
            ship_fee = 0 if sub_aggregate > 450 else 50
            pack_fee = 30
            final_invoice = round(sub_aggregate + computed_gst + ship_fee + pack_fee, 2)
            
            st.markdown(f"""
            <div style="background-color: #111; padding: 25px; border-radius: 12px; color: white; border: 2px solid #ff4b2b;">
                <p style="display:flex; justify-content:space-between; margin: 8px 0; opacity: 0.8;"><span>Subtotal:</span> <span>₹{sub_aggregate}</span></p>
                <p style="display:flex; justify-content:space-between; margin: 8px 0; opacity: 0.8;"><span>Govt GST Tax (5%):</span> <span>₹{computed_gst}</span></p>
                <p style="display:flex; justify-content:space-between; margin: 8px 0; opacity: 0.8;"><span>Beast Dispatch Fee:</span> <span>₹{ship_fee}</span></p>
                <p style="display:flex; justify-content:space-between; margin: 8px 0; opacity: 0.8;"><span>Secure Beast-Packaging:</span> <span>₹{pack_fee}</span></p>
                <hr style="border: 0; border-top: 1px dashed #ff4b2b; margin: 15px 0;">
                <h2 style="display:flex; justify-content:space-between; margin: 0; color: #ff4b2b; font-weight:800;"><span>Total Bill:</span> <span>₹{final_invoice}</span></h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(" ")
            pay_gateway = st.selectbox("Select Payment Engine", ["Instant UPI Tracker", "Credit Matrix Card", "Feast Cash on Delivery"])
            
            st.write(" ")
            if st.button("💥 FIRE ORDER TO THE KITCHEN", use_container_width=True, type="primary"):
                with st.spinner("Locking transaction and spinning up the tandoors..."):
                    time.sleep(1.5)
                    st.session_state.order_status = {
                        "ticket_id": f"BST-{random.randint(2000, 8999)}",
                        "ordered_items": list(st.session_state.cart.values()),
                        "bill_final": final_invoice,
                        "timestamp": time.strftime("%I:%M %p"),
                        "current_milestone": 0
                    }
                    st.session_state.cart = {}
                    st.success("The Beast Kitchen has locked onto your order! 🚀")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()


# --- VIEW 3: LIVE BEAST DELIVERY ---
elif app_mode == "📦 Track Live Beast Delivery":
    st.title("📦 Beast Logistics Radar")
    
    if not st.session_state.order_status:
        st.info("The Radar is blank. Run your payment checkout to begin live kitchen tracking.")
    else:
        active_order = st.session_state.order_status
        
        main_block, side_block = st.columns([2, 1])
        
        with main_block:
            st.subheader(f"Tracker ID: {active_order['ticket_id']}")
            st.caption(f"Authenticated at: {active_order['timestamp']}")
            
            milestones = [
                "🔥 Feast Beast Kitchen verified and claims ticket",
                "👨‍🍳 Head Chefs are loading ingredients into fires",
                "🍱 Packed inside thermal heat lock containers",
                "🛵 Beast Rider has picked up your massive package",
                "🏡 Package Dropped! Attack the Feast!"
            ]
            
            index_state = active_order["current_milestone"]
            st.progress(index_state * 25)
            
            st.write(" ")
            for step_num, step_name in enumerate(milestones):
                if step_num < index_state:
                    st.markdown(f"🔥 <span style='color: #ff4b2b; font-weight:600;'>[PASSED] {step_name}</span>", unsafe_allow_html=True)
                elif step_num == index_state:
                    st.markdown(f"⚡ **[ACTIVE NODE] {step_name}**")
                else:
                    st.markdown(f"⚪ <span style='color:#a0a0a0;'>{step_name}</span>", unsafe_allow_html=True)
            
            st.write(" ")
            if index_state < 4:
                if st.button("⚡ Move Kitchen Stage Forward"):
                    st.session_state.order_status["current_milestone"] += 1
                    st.rerun()
            else:
                st.success("Target Delivered! The beast has been fed.")
                if st.button("Clear App Tracker Cache"):
                    st.session_state.order_status = None
                    st.rerun()
                    
        with side_block:
            st.markdown("### Manifest")
            for item in active_order["ordered_items"]:
                st.write(f"**{item['qty']}x** {item['name']}")
            st.markdown("---")
            st.markdown(f"**Total Debited:** ₹{active_order['bill_final']}")