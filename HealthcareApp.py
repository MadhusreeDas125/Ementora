import streamlit as st
import time
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SecureHealth Prototype",
    page_icon="🏥",
    layout="wide"
)

# --- SIMULATED DATABASE STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Patient"
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "prescription_signed" not in st.session_state:
    st.session_state.prescription_signed = False

# ---🤖 ACCESSIBILITY SETTINGS (GLOBAL) ---
st.sidebar.markdown("## ⚙️ Accessibility & Security")
accessibility_mode = st.sidebar.toggle("High Contrast / Large Font Mode")
st.sidebar.caption("🔒 AES-256 Encryption Active | HIPAA & DPDP Compliant")

# Apply basic accessibility styling via markdown injection if toggled
if accessibility_mode:
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-size: 1.15rem !important;
            color: #000000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# --- 1. GLOBAL AUTHENTICATION LAYER ---
if not st.session_state.authenticated:
    st.title("🏥 SecureHealth Portal Login")
    st.info("Demo Mock: Enter any password or click Mock Biometric Login to proceed.")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username / Email", value="alex.rivera@email.com")
        password = st.text_input("Password", type="password", value="••••••••")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        bio_login = st.button("🧬 Simulate Biometric Login (Face ID/Fingerprint)")

    mfa_code = st.text_input("Enter 6-Digit MFA Token sent to your device", value="123456")
    
    if st.button("Log In Securely") or bio_login:
        if mfa_code:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Please enter your MFA token.")
    st.stop()

# --- LOGOUT & ROLE SWITCHER ---
st.sidebar.markdown(f"**Logged in as:** `{st.session_state.user_role}`")
if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Switch User View (Prototype Controls)")
role = st.sidebar.radio(
    "Select Persona Environment:",
    ["Patient Mobile App", "Doctor Web Portal", "Administrative & Billing Console"]
)
st.session_state.user_role = role

# --- 2. PATIENT ENVIRONMENT ---
if st.session_state.user_role == "Patient Mobile App":
    st.title("📱 SecureHealth Patient Dashboard")
    st.subheader("Welcome back, Alex!")
    
    # Wearable Sync Section
    st.markdown("### ⌚ Wearable & Vitals Sync (Apple Health / Fitbit)")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="❤️ Heart Rate", value="72 bpm", delta="Normal")
    col2.metric(label="🩸 Oxygen Saturation (SpO2)", value="98%", delta="Optimal")
    col3.metric(label="👣 Daily Steps", value="6,420 steps", delta="+1,200 vs yesterday")
    
    st.markdown("---")
    
    # Telehealth Notification
    st.warning("📅 **Upcoming Telehealth Visit:** Dr. Sarah Jenkins today at 3:00 PM (In 45 mins)")
    if st.button("▶️ Join Virtual Waiting Room"):
        st.success("Connected! Waiting for Dr. Jenkins to launch the encrypted video session...")

    st.markdown("---")
    
    # AI Symptom Checker Feature
    st.markdown("### 🤖 Interactive AI Symptom Checker")
    symptom_input = st.text_input("Describe what you are feeling (e.g., 'Sharp headache and nausea for 3 hours')")
    if symptom_input:
        with st.spinner("AI analyzing symptoms and cross-referencing safety parameters..."):
            time.sleep(1) # Simulate processing
        st.markdown("#### **AI Assessment:**")
        st.warning("⚠️ **Potential Indication:** Migraine Episode vs. Acute Dehydration.")
        st.markdown("""
        **Recommended Actions:**
        1. 💧 Drink 500ml of water and rest in a dark, quiet room.
        2. 📅 Use the link above to proceed with your scheduled appointment with Dr. Jenkins.
        3. 🚨 *Emergency Flag:* Go to the nearest ER if you experience sudden vision loss or numbness.
        """)

# --- 3. DOCTOR ENVIRONMENT ---
elif st.session_state.user_role == "Doctor Web Portal":
    st.title("🩺 Clinical Workspace & EMR")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 👥 Patient Queue")
        st.info("**Active Session:** Alex Rivera (3:00 PM)")
        st.write("• James Cole (3:30 PM) - *Waiting*")
        st.write("• Maria Chen (4:00 PM) - *Scheduled*")
        
        st.markdown("---")
        st.markdown("### 💡 AI Decision Support")
        st.error("⚠️ **Allergy Alert:** Patient has a documented severe allergy to **Penicillin**.")
        st.info("📈 **Vitals Trend:** Synced data shows resting HR elevated by 8% over last 48 hours.")

    with col2:
        st.markdown("### 📂 Active EHR: Alex Rivera (Age: 34)")
        st.text("Past Medical History: Mild Asthma, Seasonal Allergies")
        
        st.markdown("#### 🎙️ Speech-to-Text Clinical Notes")
        if st.button("🎤 Simulate Dictation Start"):
            with st.spinner("Listening to physician voice inputs..."):
                time.sleep(1.5)
            st.session_state.notes = "Patient presents with episodic acute migraines. Accompanied by light sensitivity and nausea. Wearable vitals verified normal baseline rhythm during onset."
        
        clinical_notes = st.text_area("Live Charting Notes", value=st.session_state.notes, height=150)
        
        st.markdown("#### 💊 e-Prescriptions (eRx)")
        drug = st.selectbox("Select Medication", ["Sumatriptan 50mg (Migraine)", "Amoxicillin (Antibiotic)", "Ibuprofen 400mg"])
        pharmacy = st.text_input("Preferred Pharmacy", "CVS Pharmacy #4022 - Main St.")
        
        if drug == "Amoxicillin (Antibiotic)":
            st.error("❌ CRITICAL ERROR: Blocked due to flagged Penicillin allergy!")
        else:
            if st.button("✍️ Sign & Securely Transmit Prescription"):
                st.session_state.prescription_signed = True
                st.success(f"Prescription for {drug} encrypted and routed directly to {pharmacy}!")

# --- 4. ADMINISTRATOR ENVIRONMENT ---
elif st.session_state.user_role == "Administrative & Billing Console":
    st.title("💼 Financial & Claims Operations Dashboard")
    
    st.markdown("### 📋 Real-Time Insurance Claim Queue")
    
    # Mocking data framework via table layout
    st.markdown("""
    | Patient Name | Provider | Payer Network | Code / Service | Status | Action |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Alex Rivera** | Dr. S. Jenkins | BlueCross Shield | 99214 (Outpatient Visit) | `⏳ Pending Verification` | [Auto-Verify Eligibility] |
    | **James Cole** | Dr. S. Jenkins | Aetna Inc. | 99213 (Telehealth Call) | `✅ Auto-Approved` | [Disburse Settlement] |
    | **Maria Chen** | Dr. R. Patel | UnitedHealthcare | 94640 (Inhalation Tx) | `❌ Denied (Missing Auth)`| [Review Audit Logs] |
    """)
    
    st.markdown("---")
    st.markdown("### 💳 Integrated Payment Gateway Analytics")
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Today's Copay Revenue", "$4,250.00", "+12% vs last Tuesday")
    metric_col2.metric("Processing Success Rate", "100%", "0 system failures")
    metric_col3.metric("Pending Insurance Payouts", "$18,910.00", "Clearing in 24h")
    
    st.markdown("---")
    st.markdown("### 🛡️ Access & Compliance Audit Trail Log")
    st.caption("Immutable system events logged under strict regulatory oversight:")
    st.code(f"""
    [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SUCCESS: Access token granted to Dr. Sarah Jenkins (MFA verified).
    [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ENCRYPTION: Vault keys rotated. Payload transit security passing handshake protocols.
    [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PRIVACY: Data deletion purge routine cleared temporary app caches successfully.
    """, language="bash")