import streamlit as st
import time
from datetime import date, timedelta

# ==========================================
# 1. PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="LuxeStay | Global & Local", page_icon="🗝️", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATASETS (Global vs Local with Fixed Images)
# ==========================================
GLOBAL_PROPERTIES = [
    {
        "id": "g1", "title": "Architectural Masterpiece with Ocean Views", "location": "Malibu, California", 
        "price": 850, "currency": "$", "cleaning_fee": 80, "rating": 4.96, "reviews": 124, "host": "Sarah Jenkins", "guests": 8, "beds": 4, "baths": 3.5, 
        "desc": "Experience unparalleled luxury in this award-winning architectural triumph. Floor-to-ceiling glass walls blend the indoor living spaces with the infinite Pacific Ocean horizon.", 
        "img": "https://picsum.photos/seed/malibu/800/500"
    },
    {
        "id": "g2", "title": "Historic Penthouse Loft", "location": "New York City, NY", 
        "price": 420, "currency": "$", "cleaning_fee": 60, "rating": 4.89, "reviews": 312, "host": "David Chen", "guests": 4, "beds": 2, "baths": 2, 
        "desc": "A meticulously restored pre-war loft in the heart of Tribeca. Exposed brick and museum-quality lighting combined with modern luxury appliances make this the perfect urban retreat.", 
        "img": "https://picsum.photos/seed/nyc/800/500"
    },
    {
        "id": "g3", "title": "Modern Alpine Estate", "location": "Aspen, Colorado", 
        "price": 1200, "currency": "$", "cleaning_fee": 150, "rating": 4.99, "reviews": 89, "host": "Elena Rostova", "guests": 12, "beds": 6, "baths": 6.5, 
        "desc": "The ultimate winter sanctuary. This sprawling estate offers direct slope access, a private spa wing with cedar sauna, and a massive great room with a 30-foot limestone fireplace.", 
        "img": "https://picsum.photos/seed/aspen/800/500"
    },
    {
        "id": "g4", "title": "Minimalist Desert Oasis", "location": "Joshua Tree, CA", 
        "price": 550, "currency": "$", "cleaning_fee": 70, "rating": 4.92, "reviews": 201, "host": "Marcus West", "guests": 6, "beds": 3, "baths": 2, 
        "desc": "Stunning minimalist design constructed entirely of concrete and glass, situated on 10 private acres of pristine desert. Star-gaze from the outdoor soaking tub.", 
        "img": "https://picsum.photos/seed/desert/800/500"
    }
]

LOCAL_PROPERTIES = [
    {
        "id": "l1", "title": "Private Island Villa", "location": "South Goa, India", 
        "price": 85000, "currency": "₹", "cleaning_fee": 5000, "rating": 4.98, "reviews": 156, "host": "Arjun Desai", "guests": 10, "beds": 5, "baths": 5, 
        "desc": "A secluded Portuguese-style villa with private beach access. Features an infinity pool overlooking the Arabian Sea, a private chef, and lush tropical gardens.", 
        "img": "https://picsum.photos/seed/goa/800/500"
    },
    {
        "id": "l2", "title": "Sea-Facing Luxury Penthouse", "location": "Worli, Mumbai", 
        "price": 45000, "currency": "₹", "cleaning_fee": 3000, "rating": 4.91, "reviews": 240, "host": "Priya Sharma", "guests": 4, "beds": 2, "baths": 2.5, 
        "desc": "Ultra-modern penthouse offering panoramic views of the Bandra-Worli Sea Link. Equipped with smart-home features, a private jacuzzi, and premium Italian furnishings.", 
        "img": "https://picsum.photos/seed/mumbai/800/500"
    },
    {
        "id": "l3", "title": "Himalayan Glasshouse", "location": "Manali, Himachal Pradesh", 
        "price": 35000, "currency": "₹", "cleaning_fee": 2500, "rating": 4.95, "reviews": 189, "host": "Karan Singh", "guests": 6, "beds": 3, "baths": 3, 
        "desc": "Nestled in the pine forests, this modern A-frame glasshouse offers unobstructed views of snow-capped peaks. Includes a heated indoor pool and a traditional bukhari (wood stove).", 
        "img": "https://picsum.photos/seed/manali/800/500"
    },
    {
        "id": "l4", "title": "Royal Heritage Palace Suite", "location": "Udaipur, Rajasthan", 
        "price": 120000, "currency": "₹", "cleaning_fee": 8000, "rating": 4.99, "reviews": 92, "host": "Maharaja Stays", "guests": 4, "beds": 2, "baths": 2, 
        "desc": "Live like royalty in a restored 18th-century Haveli overlooking Lake Pichola. Features authentic Rajput architecture, frescoed walls, and 24/7 butler service.", 
        "img": "https://picsum.photos/seed/udaipur/800/500"
    }
]

# ==========================================
# 3. SESSION STATE & NAVIGATION
# ==========================================
if 'view' not in st.session_state:
    st.session_state.view = 'home'
if 'active_property' not in st.session_state:
    st.session_state.active_property = None
if 'checkout_data' not in st.session_state:
    st.session_state.checkout_data = {}
if 'mode' not in st.session_state:
    st.session_state.mode = 'Local (India)'

def navigate_to(view_name, prop=None):
    st.session_state.view = view_name
    if prop:
        st.session_state.active_property = prop
    st.rerun()

# ==========================================
# 4. SIDEBAR - GLOBAL/LOCAL TOGGLE
# ==========================================
with st.sidebar:
    st.markdown("### 🌍 Platform Mode")
    new_mode = st.radio(
        "Select Region:",
        options=['Local (India)', 'Global'],
        index=0 if st.session_state.mode == 'Local (India)' else 1
    )
    
    # Force view reset to home if the user switches modes while viewing a property
    if new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        st.session_state.active_property = None
        st.session_state.view = 'home'
        st.rerun()
        
    st.divider()
    st.markdown(f"**Current Currency:** {'₹ INR' if st.session_state.mode == 'Local (India)' else '$ USD'}")

# ==========================================
# 5. VIEWS
# ==========================================

def render_home():
    st.title("LUXESTAY")
    st.markdown(f"### Find your next luxury escape in **{st.session_state.mode.split(' ')[0]}** locations.")
    
    # Search Bar Interface
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
    with search_col1:
        st.text_input("Location", placeholder="Anywhere")
    with search_col2:
        st.date_input("Dates", value=(date.today(), date.today() + timedelta(days=5)))
    with search_col3:
        st.selectbox("Guests", ["1 Guest", "2 Guests", "3 Guests", "4+ Guests"])

    st.divider()

    # Dynamic dataset assignment based on toggle
    properties_to_show = LOCAL_PROPERTIES if st.session_state.mode == 'Local (India)' else GLOBAL_PROPERTIES

    # Render Listings Grid
    cols = st.columns(4)
    for index, prop in enumerate(properties_to_show):
        col = cols[index % 4]
        with col:
            st.image(prop["img"], use_container_width=True)
            st.markdown(f"**{prop['location']}**")
            st.markdown(f"*{prop['title']}*")
            st.markdown(f"**{prop['currency']}{prop['price']:,}** / night · ★ {prop['rating']}")
            if st.button("View Property", key=f"btn_{prop['id']}", use_container_width=True):
                navigate_to('property_details', prop)

def render_property_details():
    prop = st.session_state.active_property
    curr = prop['currency']
    
    if st.button("← Back to Search"):
        navigate_to('home')
        
    st.title(prop["title"])
    st.markdown(f"★ **{prop['rating']}** ({prop['reviews']} reviews) · {prop['location']}")
    
    st.image(prop["img"], use_container_width=True)
    
    col_content, col_booking = st.columns([2, 1], gap="large")
    
    with col_content:
        st.subheader(f"Hosted by {prop['host']}")
        st.markdown(f"{prop['guests']} guests · {prop['beds']} bedrooms · {prop['baths']} baths")
        st.divider()
        st.write(prop["desc"])
        st.divider()
        st.subheader("What this place offers")
        st.markdown("- 📶 Fast Wi-Fi\n- 🍳 Fully equipped kitchen\n- ❄️ Central AC\n- 🚗 Free parking on premises")

    with col_booking:
        st.markdown(f"### **{curr}{prop['price']:,}** / night")
        
        checkin = st.date_input("Check-in", value=date.today())
        checkout = st.date_input("Checkout", value=date.today() + timedelta(days=5))
        guests = st.number_input("Guests", min_value=1, max_value=prop["guests"], value=2)
        
        nights = (checkout - checkin).days
        if nights > 0:
            base_price = nights * prop["price"]
            cleaning_fee = prop["cleaning_fee"]
            service_fee = int(base_price * 0.14)
            total_price = base_price + cleaning_fee + service_fee
            
            st.divider()
            st.markdown(f"{curr}{prop['price']:,} x {nights} nights: **{curr}{base_price:,}**")
            st.markdown(f"Cleaning fee: **{curr}{cleaning_fee:,}**")
            st.markdown(f"Service fee: **{curr}{service_fee:,}**")
            st.markdown(f"### Total: {curr}{total_price:,}")
            
            if st.button("Reserve Now", type="primary", use_container_width=True):
                st.session_state.checkout_data = {"nights": nights, "total": total_price, "currency": curr}
                navigate_to('checkout')
        else:
            st.error("Checkout date must be after Check-in date.")

def render_checkout():
    prop = st.session_state.active_property
    total = st.session_state.checkout_data["total"]
    curr = st.session_state.checkout_data["currency"]
    
    if st.button("← Back to Property"):
        navigate_to('property_details', prop)
        
    st.title("Confirm and Pay")
    
    col_form, col_summary = st.columns([1.5, 1], gap="large")
    
    with col_form:
        st.subheader("Payment Details")
        st.text_input("Name on Card")
        st.text_input("Card Number", max_chars=19, placeholder="0000 0000 0000 0000")
        
        c1, c2 = st.columns(2)
        c1.text_input("Expiration", placeholder="MM/YY")
        c2.text_input("CVC", max_chars=4, placeholder="123")
        
        st.divider()
        
        if st.button(f"Pay {curr}{total:,}", type="primary", use_container_width=True):
            with st.spinner("Processing secure payment..."):
                time.sleep(2) # Simulate network API delay for payment gateway
            navigate_to('success')

    with col_summary:
        st.info("Price Summary")
        st.image(prop["img"])
        st.markdown(f"**{prop['title']}**")
        st.markdown(f"**Total due today: {curr}{total:,}**")

def render_success():
    st.success("✅ Payment Successful! Your reservation is confirmed.")
    st.balloons()
    
    st.markdown("### Pack your bags!")
    st.write(f"You are heading to **{st.session_state.active_property['location']}**.")
    st.write("A receipt and itinerary have been sent to your email.")
    
    if st.button("Return to Home"):
        navigate_to('home')

# ==========================================
# 6. APP ROUTING
# ==========================================
if st.session_state.view == 'home':
    render_home()
elif st.session_state.view == 'property_details':
    render_property_details()
elif st.session_state.view == 'checkout':
    render_checkout()
elif st.session_state.view == 'success':
    render_success()