"""
EduSphere — A functional prototype of a live-classes education platform
with separate Student and Teacher portals.

Run with:  streamlit run app.py
"""

import streamlit as st
import sqlite3
import hashlib
import secrets
import datetime
import uuid
import re
import pandas as pd

# =========================================================================
# CONFIG
# =========================================================================
DB_PATH = "edusphere.db"
APP_NAME = "EduSphere"
BRAND_PRIMARY = "#12355B"   # deep navy
BRAND_ACCENT = "#D9A441"    # muted gold
BRAND_SUCCESS = "#1E8E5A"
BRAND_DANGER = "#C0392B"
BRAND_BG = "#F5F7FA"

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="wide")

# =========================================================================
# GLOBAL STYLE — clean, formal, professional look
# =========================================================================
st.markdown(f"""
<style>
    #MainMenu, footer {{visibility: hidden;}}
    .stApp {{
        background-color: {BRAND_BG};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {BRAND_PRIMARY};
    }}
    section[data-testid="stSidebar"] * {{
        color: #F0F2F5 !important;
    }}
    .es-card {{
        background: white;
        border-radius: 10px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 5px solid {BRAND_ACCENT};
    }}
    .es-badge {{
        display:inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        color: white;
        background: {BRAND_PRIMARY};
        margin-right: 6px;
    }}
    .es-badge-danger {{ background: {BRAND_DANGER}; }}
    .es-badge-success {{ background: {BRAND_SUCCESS}; }}
    .es-title {{
        color: {BRAND_PRIMARY};
        font-weight: 700;
    }}
    .es-header {{
        padding: 18px 24px;
        background: linear-gradient(90deg, {BRAND_PRIMARY}, #1B4B7A);
        border-radius: 10px;
        color: white;
        margin-bottom: 22px;
    }}
    .stButton>button {{
        background-color: {BRAND_PRIMARY};
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        background-color: {BRAND_ACCENT};
        color: {BRAND_PRIMARY};
    }}
</style>
""", unsafe_allow_html=True)

# =========================================================================
# DATABASE LAYER
# =========================================================================

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student','teacher')),
        created_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        teacher_id INTEGER NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        days TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        duration_weeks INTEGER,
        FOREIGN KEY(teacher_id) REFERENCES users(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        txn_id TEXT NOT NULL,
        amount_paid REAL NOT NULL,
        enrolled_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'success',
        FOREIGN KEY(student_id) REFERENCES users(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        login_date TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    conn.commit()

    # Seed demo data only once
    c.execute("SELECT COUNT(*) AS n FROM users")
    if c.fetchone()["n"] == 0:
        seed_demo_data(conn)
    conn.close()


def seed_demo_data(conn):
    c = conn.cursor()

    def make_user(name, email, password, role):
        salt = secrets.token_hex(16)
        pwd_hash = hash_password(password, salt)
        c.execute(
            "INSERT INTO users (name, email, password_hash, salt, role, created_at) VALUES (?,?,?,?,?,?)",
            (name, email, pwd_hash, salt, role, datetime.datetime.now().isoformat())
        )
        return c.lastrowid

    t1 = make_user("Dr. Ananya Sharma", "teacher1@edu.com", "Teach@123", "teacher")
    t2 = make_user("Prof. Rohan Verma", "teacher2@edu.com", "Teach@123", "teacher")

    s1 = make_user("Aditi Singh", "student1@edu.com", "Stud@123", "student")
    s2 = make_user("Karan Mehta", "student2@edu.com", "Stud@123", "student")
    s3 = make_user("Priya Nair", "student3@edu.com", "Stud@123", "student")

    courses = [
        ("Python Programming Mastery", "Programming", t1, 2999,
         "From basics to building real projects — hands-on Python for beginners and intermediate learners.",
         "Mon,Wed,Fri", "18:00", "19:30", 8),
        ("Data Structures & Algorithms", "Programming", t1, 3499,
         "Crack coding interviews with a structured, problem-solving-first approach to DSA.",
         "Mon,Wed,Fri", "20:00", "21:30", 10),
        ("Digital Marketing Bootcamp", "Skill Development", t1, 1999,
         "SEO, social media, and performance marketing fundamentals for the modern marketer.",
         "Sat,Sun", "10:00", "12:00", 6),
        ("UPSC Prelims Foundation", "Competitive Exams", t2, 4999,
         "A complete foundation course covering Polity, History, Geography and Current Affairs.",
         "Tue,Thu,Sat", "19:00", "20:30", 12),
        ("SSC CGL Complete Course", "Competitive Exams", t2, 3999,
         "Quantitative Aptitude, Reasoning, English and General Awareness — exam-focused teaching.",
         "Mon,Tue,Wed,Thu", "17:00", "18:30", 16),
    ]
    course_ids = []
    for title, cat, tid, price, desc, days, st_, et_, wk in courses:
        c.execute("""INSERT INTO courses
            (title, category, teacher_id, price, description, days, start_time, end_time, duration_weeks)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (title, cat, tid, price, desc, days, st_, et_, wk))
        course_ids.append(c.lastrowid)

    def enroll(student_id, course_id, method, amount):
        c.execute("""INSERT INTO enrollments
            (student_id, course_id, payment_method, txn_id, amount_paid, enrolled_at, status)
            VALUES (?,?,?,?,?,?,'success')""",
            (student_id, course_id, method, "TXN" + uuid.uuid4().hex[:10].upper(),
             amount, datetime.datetime.now().isoformat()))

    enroll(s1, course_ids[0], "UPI", 2999)
    enroll(s2, course_ids[0], "Card", 2999)
    enroll(s2, course_ids[3], "Net Banking", 4999)
    enroll(s3, course_ids[3], "UPI", 4999)

    # Login history: s1 active recently, s2 inactive 4 days, s3 inactive 5 days
    today = datetime.date.today()

    def log_login(user_id, days_ago):
        d = today - datetime.timedelta(days=days_ago)
        c.execute("INSERT INTO login_logs (user_id, login_date) VALUES (?,?)",
                   (user_id, d.isoformat()))

    for d in [0, 1, 2, 3, 5, 7]:
        log_login(s1, d)
    for d in [4, 6, 9]:
        log_login(s2, d)
    for d in [5, 8, 11]:
        log_login(s3, d)
    for d in [0, 1, 2]:
        log_login(t1, d)
        log_login(t2, d)

    conn.commit()


# =========================================================================
# SECURITY HELPERS
# =========================================================================

def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()


def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    return secrets.compare_digest(hash_password(password, salt), stored_hash)


def is_strong_password(pwd: str) -> bool:
    return bool(re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$", pwd))


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def record_login(user_id: int):
    conn = get_conn()
    conn.execute("INSERT INTO login_logs (user_id, login_date) VALUES (?,?)",
                 (user_id, datetime.date.today().isoformat()))
    conn.commit()
    conn.close()


# =========================================================================
# DATA ACCESS HELPERS
# =========================================================================

def get_user_by_email(email: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row


def create_user(name, email, password, role):
    salt = secrets.token_hex(16)
    pwd_hash = hash_password(password, salt)
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, salt, role, created_at) VALUES (?,?,?,?,?,?)",
            (name, email, pwd_hash, salt, role, datetime.datetime.now().isoformat())
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()


def get_all_courses():
    conn = get_conn()
    rows = conn.execute("""
        SELECT courses.*, users.name AS teacher_name
        FROM courses JOIN users ON courses.teacher_id = users.id
        ORDER BY category, title
    """).fetchall()
    conn.close()
    return rows


def get_course(course_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT courses.*, users.name AS teacher_name
        FROM courses JOIN users ON courses.teacher_id = users.id
        WHERE courses.id = ?
    """, (course_id,)).fetchone()
    conn.close()
    return row


def get_student_enrollments(student_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT enrollments.*, courses.title, courses.days, courses.start_time,
               courses.end_time, courses.category, users.name AS teacher_name
        FROM enrollments
        JOIN courses ON enrollments.course_id = courses.id
        JOIN users ON courses.teacher_id = users.id
        WHERE enrollments.student_id = ?
        ORDER BY enrollments.enrolled_at DESC
    """, (student_id,)).fetchall()
    conn.close()
    return rows


def is_enrolled(student_id, course_id):
    conn = get_conn()
    row = conn.execute("SELECT 1 FROM enrollments WHERE student_id=? AND course_id=?",
                        (student_id, course_id)).fetchone()
    conn.close()
    return row is not None


def enroll_student(student_id, course_id, method, amount, masked_ref):
    conn = get_conn()
    txn_id = "TXN" + uuid.uuid4().hex[:10].upper()
    conn.execute("""INSERT INTO enrollments
        (student_id, course_id, payment_method, txn_id, amount_paid, enrolled_at, status)
        VALUES (?,?,?,?,?,?,'success')""",
        (student_id, course_id, f"{method} ({masked_ref})" if masked_ref else method,
         amount, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return txn_id


def get_teacher_courses(teacher_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM courses WHERE teacher_id = ?
        ORDER BY
        CASE WHEN days LIKE 'Mon%' OR days LIKE '%,Mon%' THEN 0 ELSE 1 END, start_time
    """, (teacher_id,)).fetchall()
    conn.close()
    return rows


def get_students_for_course(course_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT users.id, users.name, users.email, enrollments.enrolled_at
        FROM enrollments JOIN users ON enrollments.student_id = users.id
        WHERE enrollments.course_id = ?
        ORDER BY users.name
    """, (course_id,)).fetchall()
    conn.close()
    return rows


def get_last_login(user_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT MAX(login_date) AS last_login FROM login_logs WHERE user_id = ?
    """, (user_id,)).fetchone()
    conn.close()
    return row["last_login"] if row and row["last_login"] else None


def days_since(date_str):
    if not date_str:
        return None
    d = datetime.date.fromisoformat(date_str)
    return (datetime.date.today() - d).days


# =========================================================================
# SESSION STATE INIT
# =========================================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0
if "checkout_course_id" not in st.session_state:
    st.session_state.checkout_course_id = None

init_db()

# =========================================================================
# AUTH SCREENS
# =========================================================================

def render_auth():
    st.markdown(f"""
    <div class="es-header">
        <h1 style="margin-bottom:0;">🎓 {APP_NAME}</h1>
        <p style="margin-top:4px; opacity:0.9;">Learn live. Teach smart. Grow together.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup, tab_demo = st.tabs(["🔐 Log In", "📝 Sign Up", "ℹ️ Demo Credentials"])

    with tab_login:
        if st.session_state.login_attempts >= 5:
            st.error("Too many failed attempts. Please wait a moment before trying again.")
        else:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In")
                if submitted:
                    user = get_user_by_email(email.strip().lower())
                    if user and verify_password(password, user["salt"], user["password_hash"]):
                        st.session_state.user = dict(user)
                        st.session_state.login_attempts = 0
                        record_login(user["id"])
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error("Invalid email or password.")

    with tab_signup:
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            role = st.radio("I am a", ["student", "teacher"], horizontal=True,
                             format_func=lambda r: "Student" if r == "student" else "Teacher")
            password = st.text_input("Create Password", type="password",
                                      help="At least 8 characters, incl. a letter, number & symbol.")
            confirm = st.text_input("Confirm Password", type="password")
            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            submitted = st.form_submit_button("Create Account")
            if submitted:
                if not name or not email or not password:
                    st.error("Please fill in all fields.")
                elif not is_valid_email(email):
                    st.error("Please enter a valid email address.")
                elif not is_strong_password(password):
                    st.error("Password must be 8+ characters and include a letter, a number, and a symbol.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif not agree:
                    st.error("You must accept the Terms of Service to continue.")
                else:
                    ok, msg = create_user(name.strip(), email.strip().lower(), password, role)
                    if ok:
                        st.success(msg + " You can now log in from the Log In tab.")
                    else:
                        st.error(msg)

    with tab_demo:
        st.info("Use these pre-loaded accounts to explore both portals instantly.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Teacher accounts**")
            st.code("teacher1@edu.com / Teach@123\nteacher2@edu.com / Teach@123")
        with c2:
            st.markdown("**Student accounts**")
            st.code("student1@edu.com / Stud@123\nstudent2@edu.com / Stud@123\nstudent3@edu.com / Stud@123")
        st.caption("student2 and student3 haven't logged in for 3+ days — try the "
                   "'Inactive Students' feature on teacher1 / teacher2's dashboard.")


# =========================================================================
# STUDENT PORTAL
# =========================================================================

PAYMENT_METHODS = ["UPI", "Credit / Debit Card", "Net Banking"]


def render_payment_flow(course):
    st.markdown(f"### 💳 Checkout — {course['title']}")
    st.markdown(f"**Amount payable:** ₹{course['price']:,.0f}")
    method = st.radio("Choose a payment method", PAYMENT_METHODS, horizontal=True)

    masked_ref = ""
    with st.form("payment_form"):
        if method == "UPI":
            upi_id = st.text_input("UPI ID", placeholder="yourname@upi")
        elif method == "Credit / Debit Card":
            card_no = st.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX", max_chars=19)
            c1, c2 = st.columns(2)
            with c1:
                expiry = st.text_input("Expiry (MM/YY)", placeholder="MM/YY")
            with c2:
                cvv = st.text_input("CVV", type="password", max_chars=4)
        else:
            bank = st.selectbox("Select your bank", ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank"])

        pay_clicked = st.form_submit_button(f"Pay ₹{course['price']:,.0f} Securely")

        if pay_clicked:
            valid = True
            if method == "UPI":
                if "@" not in upi_id or len(upi_id) < 5:
                    st.error("Please enter a valid UPI ID.")
                    valid = False
                else:
                    masked_ref = upi_id.split("@")[0][:2] + "***@" + upi_id.split("@")[-1]
            elif method == "Credit / Debit Card":
                digits = re.sub(r"\D", "", card_no)
                if len(digits) < 12 or not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry or "") or len(cvv or "") < 3:
                    st.error("Please enter valid card details.")
                    valid = False
                else:
                    masked_ref = "**** **** **** " + digits[-4:]
            else:
                masked_ref = bank

            if valid:
                txn_id = enroll_student(st.session_state.user["id"], course["id"], method,
                                         course["price"], masked_ref)
                st.success(f"✅ Payment successful! Transaction ID: {txn_id}")
                st.balloons()
                st.session_state.checkout_course_id = None
                st.info("Go to **My Courses** in the sidebar to see your class schedule.")

    if st.button("← Cancel and go back"):
        st.session_state.checkout_course_id = None
        st.rerun()


def render_course_browser():
    st.markdown('<h2 class="es-title">Explore Courses</h2>', unsafe_allow_html=True)
    courses = get_all_courses()
    categories = sorted(set(c["category"] for c in courses))
    tabs = st.tabs(["All"] + categories)

    def render_course_card(course):
        already_in = is_enrolled(st.session_state.user["id"], course["id"])
        with st.container():
            st.markdown(f"""
            <div class="es-card">
                <span class="es-badge">{course['category']}</span>
                <h4 style="margin:8px 0 2px 0;">{course['title']}</h4>
                <p style="color:#555; margin:4px 0;">{course['description']}</p>
                <p style="margin:2px 0;"><b>Instructor:</b> {course['teacher_name']}</p>
                <p style="margin:2px 0;"><b>Schedule:</b> {course['days']} &nbsp;|&nbsp; {course['start_time']} – {course['end_time']}</p>
                <p style="margin:2px 0;"><b>Duration:</b> {course['duration_weeks']} weeks</p>
                <h4 style="color:{BRAND_PRIMARY}; margin-top:10px;">₹{course['price']:,.0f}</h4>
            </div>
            """, unsafe_allow_html=True)
            if already_in:
                st.success("✅ Already enrolled")
            else:
                if st.button("Enroll Now", key=f"enroll_{course['id']}"):
                    st.session_state.checkout_course_id = course["id"]
                    st.rerun()

    if st.session_state.checkout_course_id:
        course = get_course(st.session_state.checkout_course_id)
        render_payment_flow(course)
        return

    with tabs[0]:
        cols = st.columns(2)
        for i, course in enumerate(courses):
            with cols[i % 2]:
                render_course_card(course)

    for tab, cat in zip(tabs[1:], categories):
        with tab:
            filtered = [c for c in courses if c["category"] == cat]
            cols = st.columns(2)
            for i, course in enumerate(filtered):
                with cols[i % 2]:
                    render_course_card(course)


def render_my_courses():
    st.markdown('<h2 class="es-title">My Courses & Live Class Timetable</h2>', unsafe_allow_html=True)
    enrollments = get_student_enrollments(st.session_state.user["id"])
    if not enrollments:
        st.info("You haven't enrolled in any course yet. Head to **Explore Courses** to get started.")
        return

    for e in enrollments:
        st.markdown(f"""
        <div class="es-card">
            <span class="es-badge es-badge-success">ENROLLED</span>
            <h4 style="margin:8px 0 2px 0;">{e['title']}</h4>
            <p style="margin:2px 0;"><b>Instructor:</b> {e['teacher_name']} &nbsp;|&nbsp; <b>Category:</b> {e['category']}</p>
            <p style="margin:2px 0;">🗓️ <b>Live Class Days:</b> {e['days']}</p>
            <p style="margin:2px 0;">⏰ <b>Timing:</b> {e['start_time']} – {e['end_time']}</p>
            <p style="margin:2px 0; color:#777; font-size:13px;">Paid ₹{e['amount_paid']:,.0f} via {e['payment_method']} · Txn: {e['txn_id']} · Enrolled on {e['enrolled_at'][:10]}</p>
        </div>
        """, unsafe_allow_html=True)


def render_payment_history():
    st.markdown('<h2 class="es-title">Payment History</h2>', unsafe_allow_html=True)
    enrollments = get_student_enrollments(st.session_state.user["id"])
    if not enrollments:
        st.info("No payments made yet.")
        return
    df = pd.DataFrame([{
        "Course": e["title"],
        "Amount (₹)": e["amount_paid"],
        "Method": e["payment_method"],
        "Transaction ID": e["txn_id"],
        "Date": e["enrolled_at"][:10],
        "Status": e["status"].capitalize(),
    } for e in enrollments])
    st.dataframe(df, use_container_width=True, hide_index=True)


def student_portal():
    st.sidebar.markdown(f"### 👋 {st.session_state.user['name']}")
    st.sidebar.caption("Student Portal")
    page = st.sidebar.radio("Navigate", ["🏠 Dashboard", "📚 Explore Courses", "🗓️ My Courses", "💳 Payment History"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out"):
        st.session_state.user = None
        st.session_state.checkout_course_id = None
        st.rerun()

    if page == "🏠 Dashboard":
        st.markdown(f"""
        <div class="es-header"><h2 style="margin:0;">Welcome back, {st.session_state.user['name']} 👋</h2>
        <p style="opacity:0.9;">Here's a quick look at your learning journey.</p></div>
        """, unsafe_allow_html=True)
        enrollments = get_student_enrollments(st.session_state.user["id"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Courses Enrolled", len(enrollments))
        c2.metric("Total Invested", f"₹{sum(e['amount_paid'] for e in enrollments):,.0f}")
        last_login = get_last_login(st.session_state.user["id"])
        c3.metric("Last Login", last_login or "—")
        st.markdown("#### Upcoming Live Classes")
        if enrollments:
            for e in enrollments[:5]:
                st.write(f"📌 **{e['title']}** — {e['days']} at {e['start_time']}")
        else:
            st.info("Enroll in a course to see your class schedule here.")
    elif page == "📚 Explore Courses":
        render_course_browser()
    elif page == "🗓️ My Courses":
        render_my_courses()
    elif page == "💳 Payment History":
        render_payment_history()


# =========================================================================
# TEACHER PORTAL
# =========================================================================

def render_teacher_timetable():
    st.markdown('<h2 class="es-title">My Class Timetable</h2>', unsafe_allow_html=True)
    courses = get_teacher_courses(st.session_state.user["id"])
    if not courses:
        st.info("You have no scheduled courses yet.")
        return
    for c in courses:
        n_students = len(get_students_for_course(c["id"]))
        st.markdown(f"""
        <div class="es-card">
            <span class="es-badge">{c['category']}</span>
            <h4 style="margin:8px 0 2px 0;">{c['title']}</h4>
            <p style="margin:2px 0;">🗓️ <b>Days:</b> {c['days']}</p>
            <p style="margin:2px 0;">⏰ <b>Timing:</b> {c['start_time']} – {c['end_time']}</p>
            <p style="margin:2px 0;">👥 <b>Enrolled Students:</b> {n_students}</p>
        </div>
        """, unsafe_allow_html=True)


def render_teacher_students():
    st.markdown('<h2 class="es-title">My Students</h2>', unsafe_allow_html=True)
    courses = get_teacher_courses(st.session_state.user["id"])
    if not courses:
        st.info("No courses to show students for yet.")
        return
    course_map = {c["title"]: c["id"] for c in courses}
    selected_title = st.selectbox("Select a course", list(course_map.keys()))
    students = get_students_for_course(course_map[selected_title])
    if not students:
        st.info("No students enrolled in this course yet.")
        return
    rows = []
    for s in students:
        last = get_last_login(s["id"])
        gap = days_since(last)
        rows.append({
            "Name": s["name"],
            "Email": s["email"],
            "Enrolled On": s["enrolled_at"][:10],
            "Last Login": last or "Never",
            "Days Inactive": gap if gap is not None else "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_inactive_students():
    st.markdown('<h2 class="es-title">⚠️ Inactive Student Alerts</h2>', unsafe_allow_html=True)
    st.caption("Students across your courses who haven't logged in for 3 or more consecutive days.")
    courses = get_teacher_courses(st.session_state.user["id"])
    flagged = []
    for c in courses:
        for s in get_students_for_course(c["id"]):
            last = get_last_login(s["id"])
            gap = days_since(last)
            if gap is not None and gap >= 3:
                flagged.append({
                    "Student": s["name"],
                    "Email": s["email"],
                    "Course": c["title"],
                    "Last Login": last,
                    "Days Inactive": gap,
                })
    if not flagged:
        st.success("Great news — all your students have been active in the last 3 days!")
        return
    df = pd.DataFrame(flagged).sort_values("Days Inactive", ascending=False)
    for _, r in df.iterrows():
        st.markdown(f"""
        <div class="es-card" style="border-left-color:{BRAND_DANGER};">
            <span class="es-badge es-badge-danger">{r['Days Inactive']} days inactive</span>
            <h4 style="margin:8px 0 2px 0;">{r['Student']}</h4>
            <p style="margin:2px 0;">📧 {r['Email']}</p>
            <p style="margin:2px 0;">📚 Course: {r['Course']}</p>
            <p style="margin:2px 0;">🕒 Last seen: {r['Last Login']}</p>
        </div>
        """, unsafe_allow_html=True)


def teacher_portal():
    st.sidebar.markdown(f"### 👋 {st.session_state.user['name']}")
    st.sidebar.caption("Teacher Portal")
    page = st.sidebar.radio("Navigate", ["🏠 Dashboard", "🗓️ My Timetable", "👥 My Students", "⚠️ Inactive Alerts"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out"):
        st.session_state.user = None
        st.rerun()

    if page == "🏠 Dashboard":
        st.markdown(f"""
        <div class="es-header"><h2 style="margin:0;">Welcome back, {st.session_state.user['name']} 👋</h2>
        <p style="opacity:0.9;">Here's your teaching overview for today.</p></div>
        """, unsafe_allow_html=True)
        courses = get_teacher_courses(st.session_state.user["id"])
        total_students = sum(len(get_students_for_course(c["id"])) for c in courses)
        inactive_count = 0
        for c in courses:
            for s in get_students_for_course(c["id"]):
                gap = days_since(get_last_login(s["id"]))
                if gap is not None and gap >= 3:
                    inactive_count += 1
        c1, c2, c3 = st.columns(3)
        c1.metric("Courses Teaching", len(courses))
        c2.metric("Total Students", total_students)
        c3.metric("Inactive Alerts", inactive_count)
        st.markdown("#### Today's Classes")
        today_name = datetime.date.today().strftime("%a")
        today_courses = [c for c in courses if today_name in c["days"]]
        if today_courses:
            for c in today_courses:
                st.write(f"📌 **{c['title']}** — {c['start_time']} to {c['end_time']}")
        else:
            st.info("No live classes scheduled for today.")
    elif page == "🗓️ My Timetable":
        render_teacher_timetable()
    elif page == "👥 My Students":
        render_teacher_students()
    elif page == "⚠️ Inactive Alerts":
        render_inactive_students()


# =========================================================================
# MAIN ROUTER
# =========================================================================

if st.session_state.user is None:
    render_auth()
else:
    if st.session_state.user["role"] == "student":
        student_portal()
    else:
        teacher_portal()