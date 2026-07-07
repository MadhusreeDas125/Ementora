import streamlit as st
import time
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Ementora Hospitals Digital Gateway",
    page_icon="🏥",
    layout="wide"
)

# --- BRANDING & THEME INJECTION ---
st.markdown(
    """
    <style>
    /* Ementora Medical Deep Teal Palette */
    h1, h2, h3 {
        color: #005F73 !important;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    .ementora-banner {
        background-color: #005F73;
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    div[data-testid="stMetricValue"] {
        color: #0A9396 !important;
        font-weight: bold;
    }
    div.stButton > button:first-child {
        background-color: #005F73;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        padding: 10px 24px;
    }
    div.stButton > button:first-child:hover {
        background-color: #0A9396;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIMULATED DATABASE STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_role" not in st.session_state:
    st.session_state.login_role = "Patient"
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "booking_completed" not in st.session_state:
    st.session_state.booking_completed = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Ementora Patient Hub"
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "prescription_signed" not in st.session_state:
    st.session_state.prescription_signed = False
if "pharmacy_name" not in st.session_state:
    st.session_state.pharmacy_name = "Ementora Central Pharmacy - Tower B"

# --- DISCHARGE & BILLING TRACKING STATE ---
if "discharge_status" not in st.session_state:
    st.session_state.discharge_status = "Admitted"  # Options: "Admitted", "Discharged"
if "days_admitted" not in st.session_state:
    st.session_state.days_admitted = 5

# --- SYSTEM CLINICAL ROSTER DATABASE ---
DOCTOR_ROSTER = {
    "Cardiology": [
        {"name": "Dr. Sarah Jenkins", "title": "Senior Consultant - Interventional Cardiology", "fee": "₹1,200"},
        {"name": "Dr. Arvind Swamy", "title": "Director - Cardiac Electrophysiology", "fee": "₹1,500"}
    ],
    "Neurology": [
        {"name": "Dr. Rohan Patel", "title": "Associate Director - Neurosciences", "fee": "₹1,400"},
        {"name": "Dr. Meera Alva", "title": "Consultant - Pediatric Neurology", "fee": "₹1,100"}
    ],
    "Orthopedics": [
        {"name": "Dr. Rajesh Kapoor", "title": "Chief Surgeon - Joint Replacements", "fee": "₹1,300"},
        {"name": "Dr. Nitin Verma", "title": "Consultant - Sports Medicine & Arthroscopy", "fee": "₹1,000"}
    ],
    "General Medicine": [
        {"name": "Dr. Sunita Sharma", "title": "Senior Consultant - Internal Medicine", "fee": "₹800"},
        {"name": "Dr. Alan DeSouza", "title": "Consultant - Infectious Diseases", "fee": "₹800"}
    ]
}

# --- PATIENT BILLING PROFILE REGISTRY ---
PATIENT_PROFILES = {
    "Alex Rivera (ID: EM-2026-8831)": {
        "room": "ICU Deluxe - Bed 104",
        "bed_rate": 4500,
        "treatments": [
            {"item": "Post-Op Septal Defect Repair", "cost": 120000},
            {"item": "Continuous ECG & Cardiac Echo Monitoring", "cost": 15000}
        ],
        "medicines": [
            {"item": "IV Inotropic Taper & Prophylaxis", "cost": 12500},
            {"item": "Antiplatelet Infusion Supplies", "cost": 8400}
        ]
    },
    "Mrs. Prema Nair (ID: EM-2026-4412)": {
        "room": "General Ward 3-A - Bed 1",
        "bed_rate": 1800,
        "treatments": [
            {"item": "Acute Coronary Stabilization Protocol", "cost": 45000},
            {"item": "Cardiac Troponin & Biomarker Series", "cost": 6500}
        ],
        "medicines": [
            {"item": "Sublingual Nitroglycerin & Statins", "cost": 3200}
        ]
    },
    "Mr. Amit Sharma (ID: EM-2026-9011)": {
        "room": "Daycare Suite - Bed 12",
        "bed_rate": 2500,
        "treatments": [
            {"item": "Diagnostic Coronary Angiography", "cost": 35000},
            {"item": "Radial Compressing Seal Procedure", "cost": 4200}
        ],
        "medicines": [
            {"item": "Contrast Dye & Local Anesthetic Block", "cost": 5100}
        ]
    }
}

# --- GATE 0: SECURE ACCESS & ROLE VERIFICATION GATEWAY ---
if not st.session_state.authenticated:
    st.title("🏥 Ementora Hospitals")
    st.markdown("### 🛡️ Secure Gate Access & Verification Portal")
    
    login_mode = st.radio("Select Portal Access Path", ["User / Patient Gateway", "Hospital Administrator / Doctor Terminal"], horizontal=True)
    
    col1, col2 = st.columns([1, 1])
    
    # DOCTOR / ADMIN AUTHENTICATION BRANCH
    if login_mode == "Hospital Administrator / Doctor Terminal":
        with col1:
            st.markdown("#### Staff Verification Key")
            doc_id = st.text_input("Enter Individual Hospital ID Token", placeholder="EM-DOC-4921", value="EM-DOC-4921")
            doc_pass = st.text_input("Security Pin / Password", type="password", value="••••••••")
            
            if st.button("Authorize Staff Session", type="primary"):
                if doc_id:
                    st.session_state.authenticated = True
                    st.session_state.login_role = "Doctor"
                    st.session_state.user_role = "Ementora Clinical Workspace (Doctor)"
                    st.session_state.booking_completed = True 
                    st.toast("Staff biometric signature matches directory ledger.", icon="🔑")
                    st.rerun()
                else:
                    st.error("Hospital ID is a required field.")
        with col2:
            st.markdown("<div style='margin-top:40px; padding:20px; border-left: 4px solid #0A9396; background-color:#f4f9fa;'>👨‍⚕️ <b>Ementora Medical Enterprise Gateway.</b> Clinical practitioners must provide their verified active Directory Token ID to unlock localized scheduling blocks.</div>", unsafe_allow_html=True)
            
    # PATIENT AUTHENTICATION BRANCH
    else:
        st.session_state.login_role = "Patient"
        with col1:
            st.markdown("#### Choose Verification Protocol")
            auth_method = st.radio("Select preferred route to receive your verification code:", ["📱 Phone Number", "✉️ Email Address"])
            
            if auth_method == "📱 Phone Number":
                user_credential = st.text_input("Enter Mobile Number", placeholder="+91 98765 43210")
            else:
                user_credential = st.text_input("Enter Email Address", placeholder="patient@example.com")
                
            if st.button("Generate Secure OTP"):
                if user_credential:
                    with st.spinner("Generating automated token parameters..."):
                        time.sleep(0.5)
                    st.session_state.otp_sent = True
                    st.toast("Verification OTP sent successfully! Use code: **123456**", icon="💬")
                else:
                    st.error("Please insert a valid mobile number or email destination.")

        with col2:
            if st.session_state.otp_sent:
                st.markdown("#### Enter One-Time Password")
                st.info("💡 **Prototype Shortcut:** Enter standard demo credential **123456** to log into the clinical system infrastructure.")
                otp_input = st.text_input("6-Digit Code", max_chars=6, type="password")
                
                if st.button("Verify OTP & Open Access", type="primary"):
                    if otp_input == "123456":
                        st.session_state.authenticated = True
                        st.session_state.success = "Session cryptographically validated. Initializing secure interface pipelines..."
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid verification token. Review entry details and try again.")
            else:
                st.markdown("<div style='margin-top:40px; padding:20px; border-left: 4px solid #005F73; background-color:#f4f9fa;'>👋 <b>Welcome to Ementora Unified Gate.</b> Provide your diagnostic contact detail path on the left to securely invoke credentials.</div>", unsafe_allow_html=True)
                
    st.stop()


# --- SIDEBAR INTERFACE CONTROLS ---
st.sidebar.markdown("# 🏥 Ementora Central")
accessibility_mode = st.sidebar.toggle("Enlarged UI Text / High Contrast")
st.sidebar.caption("🔒 HIPAA & DPDP Compliant Encryption System")

if accessibility_mode:
    st.markdown("<style>html, body, p, li, label { font-size: 1.25rem !important; color: #000000 !important; }</style>", unsafe_allow_html=True)

# --- 1. APPOINTMENT BOOKING GATEWAY ---
if not st.session_state.booking_completed:
    st.title("🏥 Ementora Hospitals")
    st.markdown("### Smart Patient Intake & Registration Engine")
    st.info("💡 **Prototype Guidance:** Fill out the initial registration details below to instantly initialize the medical dashboard simulation.")
    
    with st.form("appointment_form"):
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("Full Patient Name", value="Alex Rivera")
            patient_email = st.text_input("Email Address", value="alex.rivera@email.com")
        with col2:
            patient_phone = st.text_input("Contact Number", value="+91 98765 43210")
            pref_date = st.date_input("Registration Date", value=datetime.now())
        
        reason = st.text_area("Brief Description of Primary Symptoms / Medical History Notes", value="Recurring sharp headaches accompanied by slight nausea.")
        submit_booking = st.form_submit_button("Confirm Profile & Launch Interactive Workspace")
        
        if submit_booking:
            st.session_state.booking_completed = True
            st.toast("Profile data compiled securely.", icon="📋")
            st.rerun()
    st.stop()

# --- LOGOUT & ENVIRONMENT CONTROLS ---
st.sidebar.markdown(f"**Active Workspace:** `{st.session_state.user_role}`")

if st.sidebar.button("🔒 Sign Out & Terminate Secure Session", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.otp_sent = False
    st.session_state.booking_completed = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Cross-Department Navigation")

if st.session_state.login_role == "Doctor":
    nav_options = ["Ementora Clinical Workspace (Doctor)", "Ementora Administration & Billings", "Ementora Patient Hub"]
else:
    nav_options = ["Ementora Patient Hub", "Ementora Clinical Workspace (Doctor)", "Ementora Administration & Billings"]

role = st.sidebar.radio(
    "Jump to Department Dashboard:",
    nav_options,
    index=nav_options.index(st.session_state.user_role)
)
st.session_state.user_role = role

# --- 2. PATIENT ENVIRONMENT ---
if st.session_state.user_role == "Ementora Patient Hub":
    st.markdown('<div class="ementora-banner"><h1>📱 Ementora Patient Dashboard</h1><p>Welcome back, Mr. Alex Rivera | <b>Patient ID: EM-2026-8831</b></p></div>', unsafe_allow_html=True)
    
    st.markdown("### 🛠️ Ementora Medical Services Central")
    service_type = st.tabs(["🗓️ General OPD Consultation", "⚡ Premium Pay Clinic (Instant Priority)", "🩸 Diagnostic Lab & Blood Tests"])
    
    with service_type[0]:
        st.markdown("#### Schedule a Standard General OPD Visit")
        col1, col2 = st.columns(2)
        with col1:
            opd_dept = st.selectbox("Select Target OPD Department", list(DOCTOR_ROSTER.keys()), key="opd_dept_select")
            available_opd_docs = [f"{d['name']} ({d['title']})" for d in DOCTOR_ROSTER[opd_dept]]
            selected_opd_doc_str = st.selectbox("Choose OPD Specialist Consultant", available_opd_docs, key="opd_doc_select")
            opd_date = st.date_input("Select Appointment Date", value=datetime.now(), key="opd_date_picker")
        with col2:
            st.markdown("<div style='background-color:#f0f7f7; padding:15px; border-radius:8px;'><b>OPD Protocol:</b> General OPD scheduling assigns tokens sequentially. Waiting periods may vary depending on patient emergency influxes at the desk.</div>", unsafe_allow_html=True)
            opd_pay_method = st.selectbox("Preferred Payment Pathway", ["UPI (GPay / PhonePe / BHIM)", "Credit / Debit Card", "NetBanking Secure Gateway", "Pay Cash at Hospital Desk"], key="opd_pay")
            
        if st.button("Confirm OPD Allocation Slot", type="primary"):
            st.success(f"🎉 OPD Consultation successfully requested with {selected_opd_doc_str.split(' (')[0]} for {opd_date}. Routing transaction via {opd_pay_method}...")

    with service_type[1]:
        st.markdown("#### Ementora Premium Pay Clinic Hub")
        col1, col2 = st.columns(2)
        with col1:
            pc_dept = st.selectbox("Select Department Specialty", list(DOCTOR_ROSTER.keys()), key="pc_dept_select")
            pc_docs = DOCTOR_ROSTER[pc_dept]
            pc_doc_names = [f"{d['name']} - {d['title']}" for d in pc_docs]
            selected_pc_doc_idx = st.selectbox("Select Premium Panel Consultant", range(len(pc_doc_names)), format_func=lambda x: pc_doc_names[x], key="pc_doc_select")
            chosen_doc = pc_docs[selected_pc_doc_idx]
            st.metric("Consultant Premium Care Fee", value=chosen_doc["fee"], delta="Includes Express Lounge Processing")
        with col2:
            pc_date = st.date_input("Select Priority Date", value=datetime.now(), key="pc_date_picker")
            pc_pay_method = st.radio("Instant Online Checkout", ["UPI (Instant QR Auto-Gen)", "Credit / Debit Card", "NetBanking Secure Gateway", "Cash (Counter Clearance)"], key="pc_pay")
        
        if st.button("Book Premium Appointment Token", type="primary"):
            st.success(f"🚀 Premium Pay Clinic slot locked securely with {chosen_doc['name']}. Confirmation SMS and secure pass generated. Payment: {pc_pay_method}")

    with service_type[2]:
        st.markdown("#### Diagnostic Lab & Blood Test Booking Hub")
        col1, col2 = st.columns(2)
        with col1:
            test_package = st.selectbox("Select Lab Test / Profile", ["Complete Blood Count (CBC)", "Executive Full Body Health Checkup", "Lipid Profile (Cholesterol Tracker)", "HbA1c & Fasting Blood Sugar", "Thyroid Profile (T3, T4, TSH)"])
            collection_method = st.radio("Sample Collection Preference", ["🏠 Home Sample Collection", "🏥 Walk-In to Ementora Lab Clinic"])
        with col2:
            test_date = st.date_input("Schedule Lab Date", value=datetime.now(), key="lab_date_picker")
            if collection_method == "🏠 Home Sample Collection":
                home_address = st.text_input("Confirm Home Address for Phlebotomist Visit", value="Flat 402, Green Glen Layout, Outer Ring Road")
            else:
                st.markdown("<p style='color:#0A9396; padding-top:25px;'>📍 Dynamic Token ID will be generated upon confirmation for zero-wait check-in.</p>", unsafe_allow_html=True)
            lab_pay = st.selectbox("Select Lab Checkout Mode", ["UPI", "Credit / Debit Card", "NetBanking", "Cash Collection on Site"])

        if st.button("Confirm Lab Reservation", type="primary"):
            st.success(f"🎉 Success! {test_package} booked dynamically ({collection_method}). Settlement tracked via {lab_pay}.")

    st.markdown("---")
    st.warning("📅 **Confirmed Telehealth Slot:** Your scheduled appointment with Dr. Sarah Jenkins is allocated for today at 3:00 PM.")
    if st.button("▶ Honor Appointment: Join Virtual Consultation Room", type="primary"):
        st.success("Tunneling established. Initializing secure video link with Ementora Tele-Health Server Nodes...")

    st.markdown("---")
    st.markdown("### 🤖 Ementora Smart-Triage AI Engine")
    symptom_input = st.text_input("Input sudden health updates to feed live to your provider", value="Intermittent chest tightness after light jogging")
    if symptom_input:
        with st.spinner("Processing automated triage classification layers..."):
            time.sleep(0.5)
        st.markdown("#### **System Diagnostics Summary:**")
        st.error("⚠️ **Clinical Severity Flag:** Cardio-Vascular follow-up parameters triggered.")
        st.markdown("""**Automated Response Directives:**\n1. 🪑 Discontinue all strenuous activities immediately.\n2. 📅 Acknowledge your 3:00 PM appointment with Dr. Jenkins.\n3. 🚨 **Emergency Line:** For sudden severe pain spikes, immediately dial the emergency team desk at **1057**.""")

# --- 3. DOCTOR ENVIRONMENT ---
elif st.session_state.user_role == "Ementora Clinical Workspace (Doctor)":
    st.markdown('<div class="ementora-banner"><h1>🩺 Ementora Med-Connect Workspace</h1><p>Logged in: <b>Dr. Sarah Jenkins</b> | Dept of Cardiology, Ementora Metro Core Complex (ID: EM-DOC-4921)</p></div>', unsafe_allow_html=True)
    
    doc_panel_tabs = st.tabs(["📊 Duty Schedule & Leaves", "🛌 Admitted Patient Ward Management", "✍️ Live OP Clinic & Prescription Hub"])
    
    # DOCTOR TAB 1
    with doc_panel_tabs[0]:
        st.markdown("### 📅 Your Weekly Practice Footprint")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Today's Appts Booked", "14 Slots", "Fully Allocated")
        mcol2.metric("Working Hours", "09:00 AM - 05:00 PM", "Shift Style A")
        mcol3.metric("Roster Allocation Days", "Mon, Tue, Wed, Fri", "Thursdays: Research Block")
        mcol4.metric("Active Emergency Calls Today", "1 Active Case", "Tower A ICU")
        
        st.markdown("---")
        st.markdown("#### 📝 Apply for Leave of Absence")
        with st.form("leave_form"):
            l_date = st.date_input("Leave Commencing Date", value=datetime.now())
            l_type = st.selectbox("Leave Type", ["Casual Sick Leave", "Earned Privilege Leave", "Medical Conference Delegation"])
            l_reason = st.text_input("Reason Note for Medical Director Log", placeholder="Attending National Cardio Conference block...")
            if st.form_submit_button("File Leave Application with Administration"):
                st.toast("Leave application forwarded cleanly to Medical Operations Hub.", icon="📩")
                st.success("Application indexed successfully. Checking coverage availability with cross-department peers...")

    # DOCTOR TAB 2
    with doc_panel_tabs[1]:
        st.markdown("### 🛌 Patients Currently Admitted Under Your Care (Inpatient Department)")
        st.markdown(f"""
        | Bed Unit ID | Patient Name | Medical Condition / Diagnosis | Active Treatments Administered | Laboratory / Radiological Tests Done | Status Parameter |
        | :--- | :--- | :--- | :--- | :--- | :--- |
        | **ICU-Bed 104** | Alex Rivera | Post-Op Septal Defect Repair | IV Inotropic Taper, Standard Prophylaxis | Echocardiogram (Morning), Electrolytes | `{st.session_state.discharge_status}` |
        | **Ward 3-A (Bed 1)**| Mrs. Prema Nair | Acute Coronary Presentation | Antiplatelet Infusion Protocol | Continuous ECG, Cardiac Troponin I (Elevated)| `Under Monitoring` |
        | **Daycare-Bed 12** | Mr. Amit Sharma | Diagnostic Coronary Angiography| Localized Radial Compressing Seal | Renal Profiling, Fasting Blood Sugar | `Ready for Discharge`|
        """)

    # DOCTOR TAB 3
    with doc_panel_tabs[2]:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### 👥 Outpatient OP Consultation Queue")
            st.info("**Current Active Patient:** Alex Rivera (ID: EM-2026-8831)")
            st.write("• Prema Nair (3:30 PM) - *Checked In & Waiting*")
            st.write("• Amit Sharma (4:00 PM) - *Confirmed*")
            st.markdown("---")
            st.markdown("### 💡 AI-Clinical Decision Support")
            st.error("❌ **DRUG ALLERGY THREAT:** Patient profile contains critical cross-reactive allergy to **Penicillin**.")

        with col2:
            st.markdown("### 📂 Centralized EHR Worksheet: Alex Rivera")
            st.markdown("#### 🎙️ Integrated Nuance Medical Voice Dictation")
            if st.button("🎤 Enable Microphone Stream", use_container_width=True):
                with st.spinner("Processing voice input..."):
                    time.sleep(1.0)
                st.session_state.notes = "Patient reports mild chest discomfort and episodic high-intensity headaches. Wearable monitoring confirms fluctuating resting heart rates."
            
            clinical_notes = st.text_area("Physician Notes", value=st.session_state.notes, height=150)
            st.session_state.notes = clinical_notes
            
            st.markdown("#### 💊 Ementora e-Prescription (eRx) Hub")
            drug = st.selectbox("Select Formulary Item", ["Sumatriptan 50mg (Migraine)", "Amoxicillin (Antibiotic)", "Ibuprofen 400mg"])
            pharmacy = st.text_input("Target Disbursal Point", value=st.session_state.pharmacy_name)
            
            if drug == "Amoxicillin (Antibiotic)":
                st.error("❌ CRITICAL OVERRIDE: Prescription locked automatically due to Penicillin Allergy.")

# --- 4. ADMINISTRATION & BILLINGS ENVIRONMENT ---
elif st.session_state.user_role == "Ementora Administration & Billings":
    st.markdown('<div class="ementora-banner"><h1>💼 Ementora Administration & Finance Core</h1><p>Internal Operations Node | <b>Billing Ledger & Discharge Ledger Terminal</b></p></div>', unsafe_allow_html=True)
    
    # Selection of Patient Profile
    selected_patient = st.selectbox("Select Patient Record for Verification & Clearance:", list(PATIENT_PROFILES.keys()))
    profile = PATIENT_PROFILES[selected_patient]
    
    # Context-specific state management for dynamic status switching of the current profile selection
    if selected_patient == "Alex Rivera (ID: EM-2026-8831)":
        status_label = st.session_state.discharge_status
    else:
        status_label = "Admitted" # Static defaults for secondary demo targets

    # TOP METRICS BANNER
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.metric(label="Assigned Unit Location", value=profile["room"])
    with mcol2:
        if selected_patient == "Alex Rivera (ID: EM-2026-8831)":
            st.session_state.days_admitted = st.number_input("Billable Days Admitted", min_value=1, value=st.session_state.days_admitted, step=1)
            days = st.session_state.days_admitted
        else:
            days = 4
            st.metric(label="Billable Days Admitted", value=f"{days} Days")
    with mcol3:
        color_badge = "🟢 Live Active Tracker" if status_label == "Admitted" else "🔴 Official Archive: Discharged"
        st.metric(label="Administrative Discharge Status", value=status_label, delta=color_badge)

    st.markdown("---")
    
    # DYNAMIC CALCULATIONS
    total_bed_cost = profile["bed_rate"] * days
    total_treatment_cost = sum(t["cost"] for t in profile["treatments"])
    total_medicine_cost = sum(m["cost"] for m in profile["medicines"])
    gross_total = total_bed_cost + total_treatment_cost + total_medicine_cost
    
    # DISPLAY ITEMIZED STATEMENTS
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 📋 Itemized Invoice Ledger Breakdown")
        
        # 1. Bed Charges Table
        st.markdown(f"#### 🛏️ 1. Accommodation Charges (Rate: ₹{profile['bed_rate']:,} / day)")
        st.markdown(f"""
        | Item Particulars | Rate Parameter | Multiplier / Days | Line Subtotal |
        | :--- | :--- | :--- | :--- |
        | Base Institutional Bed Charges ({profile['room']}) | ₹{profile['bed_rate']:,} | {days} Days | **₹{total_bed_cost:,}** |
        """)
        
        # 2. Treatment Charges Table
        st.markdown("#### 🩺 2. Clinical Procedures & Surgical Interventions")
        treatment_rows = ""
        for t in profile["treatments"]:
            treatment_rows += f"| {t['item']} | Institutional Base Rate | 1 | ₹{t['cost']:,} |\n"
        st.markdown(f"""
        | Intervention Particulars | Schedule Class | Qty | Line Subtotal |
        | :--- | :--- | :--- | :--- |
        {treatment_rows}
        """)
        
        # 3. Medicine Charges Table
        st.markdown("#### 💊 3. Pharmacy & Consumables Allocation")
        med_rows = ""
        for m in profile["medicines"]:
            med_rows += f"| {m['item']} | Formulary Standard | 1 | ₹{m['cost']:,} |\n"
        st.markdown(f"""
        | Medication/Consumable Item | Class Tier | Qty | Line Subtotal |
        | :--- | :--- | :--- | :--- |
        {med_rows}
        """)

    with col_right:
        st.markdown("### 💰 Financial Statement Summary")
        if status_label == "Admitted":
            st.info("ℹ️ **Provisional Invoice:** The summary below lists compiled charges accrued up to this local time stamp.")
        else:
            st.success("✅ **Finalized Summary:** Patient has cleared financial parameters and holds formal discharge paperwork.")
            
        st.markdown(f"""
        * **Total Bed Space Cost:** ₹{total_bed_cost:,}
        * **Total Procedure Cost:** ₹{total_treatment_cost:,}
        * **Total Medicine Cost:** ₹{total_medicine_cost:,}
        """)
        st.markdown("---")
        st.markdown(f"## **Gross Total: ₹{gross_total:,}**")
        st.markdown("---")
        
        # ADMINISTRATIVE MANAGEMENT ACTIONS
        st.markdown("### ⚙️ Management Action Console")
        if selected_patient == "Alex Rivera (ID: EM-2026-8831)":
            if st.session_state.discharge_status == "Admitted":
                if st.button("💥 Process Discharge & Finalize Statements", type="primary", use_container_width=True):
                    st.session_state.discharge_status = "Discharged"
                    st.toast("Discharge verified and logged successfully.", icon="📝")
                    st.rerun()
            else:
                if st.button("🔄 Reverse Discharge Status to Admitted", use_container_width=True):
                    st.session_state.discharge_status = "Admitted"
                    st.toast("Patient status reverted to active status.", icon="↩️")
                    st.rerun()
        else:
            st.warning("🔒 Administrative actions are limited to primary active validation sandbox profiles.")