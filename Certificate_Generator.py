import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
from datetime import datetime
import os
import math

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Official Bulk Certificate Generator", page_icon="🎓", layout="wide")

# --- EXPANDED STYLE DICTIONARY ---
DEFAULT_STYLE = {
    "bg_color": "#FFFFFF",
    "watermark_text": "",        
    "watermark_opacity": 35,     
    
    "border_style": "classic",   
    "border_gold": "#D4AF37",
    "border_gold_width": 14,
    "border_navy": "#0B3C5D",
    "border_navy_width": 45,
    "border_dark": "#323232",
    "border_dark_width": 6,
    
    "title_text": "CERTIFICATE OF COMPLETION",
    "subtitle_text": "PROUDLY PRESENTED TO",
    "citation_text": "for successfully fulfilling all curriculum requirements and demonstrating mastery in",
    "date_label": "DATE OF ISSUANCE",
    
    # HARDCODED LOCKED SIGNATURE ENTRIES
    "sig_label_left": "Mahul Dutta",
    "sig_role_left": "Head of Organization",
    "sig_label_right": "Madhusree Das",
    "sig_role_right": "Co-Head of Organization",
    
    # FIXED VERTICAL SCALE COORDINATES
    "title_color": "#0B3C5D", "title_size": 130, "title_y_position": 500, "title_style": "Bold",
    "subtitle_color": "#323232", "subtitle_size": 70, "subtitle_y_position": 780, "subtitle_style": "Regular",
    "name_color": "#0B3C5D", "name_size": 180, "name_y_position": 960, "name_style": "Bold",
    "body_color": "#323232", "body_size": 52, "body_y_position": 1280, "body_style": "Italic",
    "course_color": "#D4AF37", "course_size": 120, "course_y_position": 1430, "course_style": "BoldItalic",
    "meta_lbl_size": 52, "meta_val_size": 60
}

if "current_style" not in st.session_state:
    st.session_state.current_style = DEFAULT_STYLE.copy()

# --- UTILITY DRAWING FUNCTIONS ---

def get_font_variant(style_name, font_size):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_files = {
        "Regular": "Montserrat-Regular.ttf",
        "Bold": "Montserrat-Bold.ttf",
        "Italic": "Montserrat-Italic.ttf",
        "BoldItalic": "Montserrat-BoldItalic.ttf"
    }
    target_file = font_files.get(style_name, "Montserrat-Regular.ttf")
    font_path = os.path.join(script_dir, target_file)
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, font_size)
    return ImageFont.load_default()

def draw_official_seal(draw, x, y, r=120):
    """Draws a premium geometric burst seal using pure vectors."""
    draw.ellipse([x - r, y - r, x + r, y + r], outline="#D4AF37", width=5)
    draw.ellipse([x - (r - 10), y - (r - 10), x + (r - 10), y + (r - 10)], outline="#D4AF37", width=2)
    draw.ellipse([x - (r - 26), y - (r - 26), x + (r - 26), y + (r - 26)], outline="#D4AF37", width=3)
    
    points = 8
    inner_r = r - 85
    outer_r = r - 45
    star_points = []
    for i in range(points * 2):
        angle = i * math.pi / points
        current_r = outer_r if i % 2 == 0 else inner_r
        pt_x = x + current_r * math.cos(angle)
        pt_y = y + current_r * math.sin(angle)
        star_points.append((pt_x, pt_y))
    
    draw.polygon(star_points, fill="#D4AF37")

def draw_text_centered(draw, text, y, font, color, canvas_width=3508):
    try:
        w = draw.textlength(text, font=font)
    except AttributeError:
        left, top, right, bottom = font.getbbox(text)
        w = right - left
    x = (canvas_width - w) / 2
    draw.text((x, y), text, fill=color, font=font)
    
def wrap_and_draw_course(draw, text, start_y, font, color, max_chars=40, line_spacing=150):
    if len(text) <= max_chars:
        draw_text_centered(draw, f"“ {text} ”", start_y, font, color)
        return start_y + line_spacing
    words = text.split(' ')
    midpoint = len(words) // 2
    line1 = " ".join(words[:midpoint+1])
    line2 = " ".join(words[midpoint+1:])
    draw_text_centered(draw, f"“ {line1}", start_y, font, color)
    draw_text_centered(draw, f"{line2} ”", start_y + line_spacing, font, color)

def create_base_template(style):
    width, height = 3508, 2480
    image = Image.new("RGBA", (width, height), style["bg_color"])
    draw = ImageDraw.Draw(image)
    
    if style["border_style"] != "none":
        g_w = style["border_gold_width"]
        n_w = style["border_navy_width"]
        d_w = style["border_dark_width"]
        
        draw.rectangle([(40, 40), (width - 40, height - 40)], outline=style["border_gold"], width=g_w)
        if style["border_style"] == "classic":
            draw.rectangle([(40 + g_w + 10, 40 + g_w + 10), (width - (40 + g_w + 10), height - (40 + g_w + 10))], outline=style["border_navy"], width=n_w)
            draw.rectangle([(40 + g_w + n_w + 20, 40 + g_w + n_w + 20), (width - (40 + g_w + n_w + 20), height - (40 + g_w + n_w + 20))], outline=style["border_dark"], width=d_w)

    return image.convert("RGB")

def generate_certificate(name, course, date_str, cert_id, style):
    img = create_base_template(style)
    draw = ImageDraw.Draw(img)
    
    title_font = get_font_variant(style["title_style"], style["title_size"])     
    subtitle_font = get_font_variant(style["subtitle_style"], style["subtitle_size"])
    name_font = get_font_variant(style["name_style"], style["name_size"])
    body_font = get_font_variant(style["body_style"], style["body_size"])
    course_font = get_font_variant(style["course_style"], style["course_size"])   
    meta_lbl_font = get_font_variant("Regular", style["meta_lbl_size"])

    draw_official_seal(draw, x=1754, y=300, r=120)

    draw_text_centered(draw, style["title_text"], style["title_y_position"], title_font, style["title_color"])
    draw_text_centered(draw, style["subtitle_text"], style["subtitle_y_position"], subtitle_font, style["subtitle_color"])
    draw_text_centered(draw, str(name).upper(), style["name_y_position"], name_font, style["name_color"])
    draw_text_centered(draw, style["citation_text"], style["body_y_position"], body_font, style["body_color"])
    wrap_and_draw_course(draw, str(course), style["course_y_position"], course_font, style["course_color"])
    
    sig_line_y = 2050
    text_offset_y = 25
    
    # Left Signature Track
    draw.text((400, sig_line_y - 75), style["sig_role_left"].upper(), fill=style["subtitle_color"], font=meta_lbl_font)
    draw.line([(400, sig_line_y), (1100, sig_line_y)], fill=style["border_navy"], width=6)
    handwritten_font_left = get_font_variant("Italic", 70)
    draw.text((430, sig_line_y + text_offset_y), style["sig_label_left"], fill=style["border_navy"], font=handwritten_font_left)
    
    # Center Global Identification Node
    draw_text_centered(draw, f"VERIFICATION ID: {cert_id}", 2015, meta_lbl_font, style["subtitle_color"])
    
    # Right Signature Track
    draw.text((2400, sig_line_y - 75), style["sig_role_right"].upper(), fill=style["subtitle_color"], font=meta_lbl_font)
    draw.line([(2400, sig_line_y), (3100, sig_line_y)], fill=style["border_navy"], width=6)
    handwritten_font_right = get_font_variant("Italic", 70)
    draw.text((2430, sig_line_y + text_offset_y), style["sig_label_right"], fill=style["border_navy"], font=handwritten_font_right)
    
    # Securely Positioned Issue Date Line
    draw_text_centered(draw, f"{style['date_label']}: {str(date_str).upper()}", 2180, meta_lbl_font, style["subtitle_color"])
    
    return img

# --- STREAMLIT USER INTERFACE LAYOUT ---
st.title("🎓 Institutional Bulk Certificate Processing core")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Modifiable Content Strings")
    st.session_state.current_style["title_text"] = st.text_input("Title Block Header Text", st.session_state.current_style["title_text"])
    st.session_state.current_style["subtitle_text"] = st.text_input("Presentation Subtitle Phrase", st.session_state.current_style["subtitle_text"])
    st.session_state.current_style["citation_text"] = st.text_area("Default Course Citation Statement", st.session_state.current_style["citation_text"])
    
    st.markdown("---")
    st.subheader("📋 Locked Verification Details")
    st.text_input("Primary Registrar Signee Authority", value=st.session_state.current_style["sig_label_left"], disabled=True)
    st.text_input("Secondary Executive Signee Authority", value=st.session_state.current_style["sig_label_right"], disabled=True)

with col2:
    mode = st.radio("Choose System Operating Mode", ["Single Sandbox Preview Panel", "Secure Bulk Spreadsheet Portal"])
    
    if mode == "Single Sandbox Preview Panel":
        st.header("📥 Individual Record Simulation")
        single_name = st.text_input("Recipient Full Name", "Aditi Pal")
        single_course = st.text_input("Course Specification Domain", "Advanced Data Structures & AI System Design")
        single_date = st.date_input("Processing Operational Date", datetime.now())
        single_id = st.text_input("Unique Database Record ID", "AMITY-2026-X98A")
        
        formatted_date = single_date.strftime("%B %d, %Y")
        
        preview_img = generate_certificate(
            single_name, single_course, formatted_date, single_id, st.session_state.current_style
        )
        st.image(preview_img.resize((900, 636)), caption="Dynamic UI Design Sandbox Canvas Proof", use_container_width=True)
        
        buf = io.BytesIO()
        preview_img.save(buf, format="PNG")
        st.download_button(label="📥 Export Current Frame Image", data=buf.getvalue(), file_name=f"Certificate_{single_name.replace(' ', '_')}.png", mime="image/png")
        
    else:
        st.header("📊 Bulk Secure Processing Console")
        st.markdown("""
        **Roster Document Structural Conditions:** Upload a valid data worksheet file matching these precise tracking headers: `Name`, `Course`, `Date`, and `ID`.
        """)
        
        uploaded_data_sheet = st.file_uploader("Upload Target Roster Spreadsheet Document", type=["csv", "xlsx"])
        
        if uploaded_data_sheet is not None:
            try:
                if uploaded_data_sheet.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_data_sheet)
                else:
                    df = pd.read_excel(uploaded_data_sheet)
                
                st.write("📋 **Data Grid Verification Monitor:**")
                st.dataframe(df.head(5))
                
                required_cols = ["Name", "Course", "Date", "ID"]
                if all(col in df.columns for col in required_cols):
                    if st.button("🚀 Execute Secure Archive Compilation"):
                        zip_buffer = io.BytesIO()
                        
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            progress_bar = st.progress(0)
                            total_rows = len(df)
                            
                            for idx, row in df.iterrows():
                                cert_img = generate_certificate(
                                    row["Name"], row["Course"], str(row["Date"]), row["ID"], st.session_state.current_style
                                )
                                
                                img_bytes = io.BytesIO()
                                cert_img.save(img_bytes, format="PNG")
                                img_bytes.seek(0)
                                
                                clean_filename = f"Certificate_{str(row['Name']).replace(' ', '_')}_{row['ID']}.png"
                                zip_file.writestr(clean_filename, img_bytes.getvalue())
                                progress_bar.progress((idx + 1) / total_rows)
                        
                        zip_buffer.seek(0)
                        st.success(f"Successfully rendered and compiled {total_rows} official entries!")
                        
                        st.download_button(
                            label="📥 Download Secure Distribution Package (.ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"Official_Bulk_Certificates_{datetime.now().strftime('%Y%m%d')}.zip",
                            mime="application/zip"
                        )
                else:
                    st.error(f"Data mapping error. Missing critical database tracking headers from file: {required_cols}")
            except Exception as e:
                st.error(f"Processing execution trace exception logged: {e}")