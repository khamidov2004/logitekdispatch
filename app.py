import os
import io
import json
import re
import streamlit as st
from PIL import Image

# Import pdfplumber for PDF text extraction
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# Import pytesseract for image OCR
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# Import AI Providers
try:
    from google import genai as genai_sdk
    GOOGLE_GENAI_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_SDK_AVAILABLE = False

try:
    import google.generativeai as genai_legacy
    GEMINI_LEGACY_AVAILABLE = True
except ImportError:
    GEMINI_LEGACY_AVAILABLE = False

GEMINI_AVAILABLE = GOOGLE_GENAI_SDK_AVAILABLE or GEMINI_LEGACY_AVAILABLE

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ==========================================
# STREAMLIT PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="LOGITEK DISPATCH - Rate Confirmation AI",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for LOGITEK DISPATCH Liquid iOS 26 Theme and animated truck processing
st.markdown("""
<style>
    /* Hide Sidebar Completely */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Liquid Dark iOS 26 Global Background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%) !important;
        color: #f8fafc !important;
    }

    /* LOGITEK DISPATCH Liquid Hero Banner with Entrance Animation */
    .logitek-hero-banner {
        position: relative;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(35px);
        -webkit-backdrop-filter: blur(35px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 28px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.25);
        animation: liquidEntrance 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        overflow: hidden;
    }

    .liquid-ambient-aura {
        position: absolute;
        top: -60px;
        right: -60px;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.35) 0%, rgba(129, 140, 248, 0.15) 50%, transparent 70%);
        filter: blur(50px);
        border-radius: 50%;
        pointer-events: none;
        animation: auraPulse 6s ease-in-out infinite alternate;
    }

    .logitek-title {
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #ffffff 0%, #a5f3fc 35%, #38bdf8 70%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 10px 30px rgba(56, 189, 248, 0.3);
        margin: 0;
        line-height: 1.1;
    }

    .logitek-subtitle {
        font-size: 1.35rem;
        font-weight: 800;
        color: #38bdf8;
        letter-spacing: 2.5px;
        margin-top: 0.5rem;
        text-transform: uppercase;
        text-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);
    }

    .hero-badge-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(129, 140, 248, 0.2) 100%);
        border: 1px solid rgba(56, 189, 248, 0.4);
        color: #38bdf8;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.15);
    }

    .hero-stats-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 1.2rem;
    }

    .hero-stat-pill {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #cbd5e1;
        padding: 6px 14px;
        border-radius: 14px;
        font-size: 0.85rem;
        font-weight: 600;
        backdrop-filter: blur(10px);
    }

    @keyframes liquidEntrance {
        0% {
            opacity: 0;
            transform: translateY(35px) scale(0.95);
            filter: blur(12px);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
            filter: blur(0px);
        }
    }

    @keyframes auraPulse {
        0% { transform: scale(1) translate(0, 0); }
        100% { transform: scale(1.3) translate(-25px, 25px); }
    }

    /* iOS 26 Liquid File Uploader Styling */
    div[data-testid="stFileUploader"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border: 2px dashed rgba(56, 189, 248, 0.4) !important;
        border-radius: 24px !important;
        padding: 1.5rem !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 20px 45px rgba(56, 189, 248, 0.25) !important;
        transform: translateY(-2px);
    }

    .stCodeBlock {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(20px) !important;
    }

    /* Animated Truck Highway System */
    .truck-highway-track {
        position: relative;
        width: 100%;
        height: 110px;
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid #334155;
        margin: 1.5rem 0;
    }
    .asphalt-road {
        position: absolute;
        bottom: 0;
        width: 100%;
        height: 38px;
        background: #1e293b;
        border-top: 3px solid #3b82f6;
    }
    .road-dashed-lines {
        width: 200%;
        height: 5px;
        margin-top: 15px;
        background: repeating-linear-gradient(90deg, #f59e0b 0px, #f59e0b 30px, transparent 30px, transparent 60px);
        animation: moveRoadLines 0.45s linear infinite;
    }
    @keyframes moveRoadLines {
        0% { transform: translateX(0); }
        100% { transform: translateX(-60px); }
    }
    .anim-truck-wrapper {
        position: absolute;
        bottom: 10px;
        left: -10%;
        animation: driveAcrossRoad 3.2s ease-in-out infinite;
        display: flex;
        align-items: center;
    }
    .anim-truck-emoji {
        font-size: 46px;
        animation: truckVibrate 0.25s ease-in-out infinite alternate;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.6));
    }
    .anim-exhaust {
        font-size: 26px;
        margin-right: -12px;
        opacity: 0.9;
        animation: puffExhaust 0.5s ease-out infinite;
    }
    @keyframes driveAcrossRoad {
        0% { left: -10%; }
        50% { left: 42%; }
        100% { left: 105%; }
    }
    @keyframes truckVibrate {
        0% { transform: translateY(0px); }
        100% { transform: translateY(-4px); }
    }
    @keyframes puffExhaust {
        0% { opacity: 0.9; transform: scale(0.8) translateX(0); }
        100% { opacity: 0; transform: scale(1.6) translateX(-18px); }
    }
    .processing-status-banner {
        position: absolute;
        top: 14px;
        left: 20px;
        font-size: 1.05rem;
        font-weight: 700;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.6);
    }
    .processing-pulse-dot {
        width: 12px;
        height: 12px;
        background-color: #10b981;
        border-radius: 50%;
        animation: pulseDot 1.2s infinite;
    }
    @keyframes pulseDot {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8); }
        70% { transform: scale(1.15); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
</style>
""", unsafe_allow_html=True)


def render_truck_processing_animation(status_message: str):
    """Renders dynamic animated highway track with moving truck during processing."""
    html_code = f"""
    <div class="truck-highway-track">
        <div class="processing-status-banner">
            <div class="processing-pulse-dot"></div>
            <span>{status_message}</span>
        </div>
        <div class="asphalt-road">
            <div class="road-dashed-lines"></div>
        </div>
        <div class="anim-truck-wrapper">
            <span class="anim-exhaust">💨</span>
            <span class="anim-truck-emoji">🚛</span>
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)


# ==========================================
# TEXT & PAGE IMAGE EXTRACTION HELPERS
# ==========================================
def extract_pdf_data(pdf_bytes: bytes, tesseract_cmd: str = None) -> tuple[str, list]:
    """Extract raw text and page images from PDF file using pdfplumber and OCR for multi-page documents."""
    if not PDFPLUMBER_AVAILABLE:
        st.error("`pdfplumber` library is not installed.")
        return "", []
    
    extracted_text = ""
    page_images = []
    
    # Configure tesseract if available for OCR fallback on scanned PDF pages
    if tesseract_cmd and os.path.exists(tesseract_cmd) and PYTESSERACT_AVAILABLE:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                # 1. Extract digital text with layout format
                p_text = page.extract_text(layout=True) or ""
                
                # 2. Extract table text if available
                tables = page.extract_tables() or []
                table_text = ""
                for table in tables:
                    for row in table:
                        row_filtered = [str(cell).strip() for cell in row if cell is not None and str(cell).strip()]
                        if row_filtered:
                            table_text += " | ".join(row_filtered) + "\n"
                
                # 3. Render page image for visual preview and multimodal LLM vision
                p_img = None
                try:
                    p_img = page.to_image(resolution=150).original
                    if p_img.mode != 'RGB':
                        p_img = p_img.convert('RGB')
                    page_images.append(p_img)
                except Exception:
                    pass

                # 4. If text is minimal (e.g. scanned page), attempt OCR on the page image
                if len(p_text.strip()) < 30 and p_img is not None and PYTESSERACT_AVAILABLE:
                    try:
                        ocr_text = pytesseract.image_to_string(p_img)
                        if len(ocr_text.strip()) > len(p_text.strip()):
                            p_text = f"[OCR Extracted Text]\n{ocr_text}"
                    except Exception:
                        pass
                
                combined_page = f"=== PAGE {i+1} ===\n{p_text}\n"
                if table_text.strip():
                    combined_page += f"\n--- PAGE {i+1} TABLES ---\n{table_text}\n"
                
                extracted_text += combined_page + "\n"

    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")

    return extracted_text.strip(), page_images


def extract_text_from_image(image_bytes: bytes, tesseract_cmd: str = None) -> str:
    """Extract raw text from Image file using pytesseract OCR."""
    if not PYTESSERACT_AVAILABLE:
        st.error("`pytesseract` library is not installed.")
        return ""
    
    # Configure custom tesseract binary path if provided
    if tesseract_cmd and os.path.exists(tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    elif os.name == 'nt':
        default_win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(default_win_path):
            pytesseract.pytesseract.tesseract_cmd = default_win_path

    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text.strip()
    except Exception as e:
        st.warning(f"Pytesseract OCR Notice: {str(e)}")
        return ""


# ==========================================
# AI PARSING ENGINE (GEMINI & OPENAI)
# ==========================================
PARSING_SYSTEM_PROMPT = """
You are an expert logistics Rate Confirmation (RC) data parsing system.
The input document may contain MULTIPLE PAGES (2, 3, or more pages) and may include digital text or scanned document images.
It may be a Single-Leg load, a Multi-Stop load (multiple PUs and/or DELs), or a ROUND TRIP / RELOAD load.

Read ALL pages carefully from start to finish and extract the load details into a valid JSON object matching this EXACT schema:

{
  "broker": "Full Broker / Logistics Company Name (e.g. RXO, C.H. Robinson, TQL, Echo, Landstar, Coyote, etc.)",
  "load_id": "Broker Load ID / Order Number / RC # / Shipment #",
  "pickup_number": "First Pickup Number / PU # / Shipper Confirmation #",
  "ref_number": "Reference Number / Ref # / PO #",
  "is_round_trip": false,
  "stops": [
    {
      "type": "PU",
      "date": "MM/DD",
      "time": "HH:MM",
      "pickup_number": "PU # for this stop if available",
      "facility_name": "Facility Name / Company Name",
      "full_address": "Street Address, City, State ZIP"
    }
  ],
  "pickup": {
    "date": "MM/DD",
    "time": "HH:MM",
    "facility_name": "Pickup Facility Name / Shipper Name",
    "full_address": "Complete Street Address, City, State ZIP Code"
  },
  "delivery": {
    "date": "MM/DD",
    "time": "HH:MM",
    "facility_name": "Delivery Facility Name / Consignee Name",
    "full_address": "Complete Street Address, City, State ZIP Code"
  },
  "rate": "Agreed Flat Rate Amount (e.g. 3937.0 or 2450)"
}

Extremely Important Field Location Guidance:
1. BROKER NAME: Check header logo, company header, or "Issued By" on Page 1 or Page 2.
2. LOAD ID: Look for "Load #", "Order #", "Shipment #", "RC #", "Trip #".
3. PICKUP #: Look for "PU #", "Pickup #", "Shipper #", "Confirmation #".
4. REF #: Look for "Ref #", "PO #", "Customer Ref #".
5. PICKUP (PU): Look for "Shipper", "Origin", "Pick At", "Loading Address".
   - Extract Date in MM/DD format (e.g. 08/17).
   - Extract Time (e.g. 13:00, 08:00 15:00, or FCFS).
   - Extract Facility Name.
   - Extract Full Address (Street, City, State, ZIP).
6. DELIVERY (DEL): Look for "Consignee", "Destination", "Unload At", "Deliver To".
   - Extract Date in MM/DD format (e.g. 8/19).
   - Extract Time (e.g. 08:15).
   - Extract Facility Name.
   - Extract Full Address (Street, City, State, ZIP).
7. RATE: Look for "Agreed Rate", "Total Rate", "Total Pay", "Flat Rate", "Linehaul + FSC". Extract only the numeric rate.
8. MULTI-STOP & ROUND TRIP LOADS:
   If the document has MORE THAN ONE pickup OR more than one delivery OR any reload stops, you MUST:
   - Set `"is_round_trip": true`
   - List ALL stops in chronological order inside the `"stops"` array.
   - Use the EXACT stop type labels: `"PU"` for each pickup, `"RELOAD"` for each reload, `"DEL"` for each delivery.
   - Do NOT assume the first stop is always PU or the last is always DEL. Use the document labels.
   - Examples of multi-stop patterns:
     * PU -> DEL -> RELOAD -> DEL  (round trip with reload)
     * PU -> RELOAD -> DEL  (reload load)
     * PU -> PU -> DEL -> DEL  (multi-pickup, multi-delivery)
     * PU -> DEL  (single-leg, use "pickup" and "delivery" fields instead)
   - For each stop, extract its specific `pickup_number` (PU #) if shown.

If any field is missing or cannot be found after searching all pages, set its value to "N/A".
Return ONLY the JSON object.
"""

def parse_rc_with_gemini(raw_text: str, api_key: str, model_name: str = "gemini-2.5-flash", page_images: list = None) -> dict:
    """Parse raw text and/or page images using Google Gemini API with automatic model fallbacks."""
    if not GEMINI_AVAILABLE:
        st.error("Google Gemini SDK is not installed.")
        return {}
    
    # Candidate model list starting with requested model
    fallback_models = [model_name]
    for alt in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]:
        if alt not in fallback_models:
            fallback_models.append(alt)

    contents = [PARSING_SYSTEM_PROMPT]
    if raw_text:
        contents.append(f"RAW EXTRACTED TEXT FROM ALL PAGES OF THE RATE CONFIRMATION:\n{raw_text}")

    # Attach page images (up to 5 pages) to Gemini's prompt for multimodal vision extraction
    if page_images:
        contents.append("VISUAL DOCUMENT PAGES FOR ALL PAGES OF THIS RATE CONFIRMATION:")
        for idx, img in enumerate(page_images[:5]):
            contents.append(f"--- PAGE {idx + 1} IMAGE ---")
            contents.append(img)

    contents.append("Analyze all pages above and extract the logistics rate confirmation JSON object.")

    last_error = None
    for current_model in fallback_models:
        try:
            response_text = ""
            if GOOGLE_GENAI_SDK_AVAILABLE:
                client = genai_sdk.Client(api_key=api_key)
                try:
                    response = client.models.generate_content(
                        model=current_model,
                        contents=contents,
                        config={"response_mime_type": "application/json"}
                    )
                except Exception:
                    response = client.models.generate_content(
                        model=current_model,
                        contents=contents
                    )
                response_text = response.text.strip()
            elif GEMINI_LEGACY_AVAILABLE:
                genai_legacy.configure(api_key=api_key)
                model = genai_legacy.GenerativeModel(current_model)
                try:
                    response = model.generate_content(contents, generation_config={"response_mime_type": "application/json"})
                except Exception:
                    response = model.generate_content(contents)
                response_text = response.text.strip()

            cleaned = re.sub(r"^```json\s*", "", response_text, flags=re.IGNORECASE)
            cleaned = re.sub(r"^```\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as jde:
            st.error(f"Failed to parse JSON output from Gemini response ({current_model}). Raw response: {response_text}")
            return {}
        except Exception as e:
            last_error = e
            error_str = str(e)
            if "404" in error_str or "not found" in error_str or "not supported" in error_str:
                continue
            else:
                st.error(f"Gemini API Error ({current_model}): {error_str}")
                return {}

    if last_error:
        st.error(f"Gemini API Error: {str(last_error)}")
    return {}


def parse_rc_with_openai(raw_text: str, api_key: str, model_name: str = "gpt-4o-mini") -> dict:
    """Parse raw text using OpenAI API."""
    if not OPENAI_AVAILABLE:
        st.error("OpenAI SDK (`openai`) is not installed.")
        return {}
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": PARSING_SYSTEM_PROMPT},
                {"role": "user", "content": f"RAW EXTRACTED TEXT:\n{raw_text}"}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        st.error(f"OpenAI API Error: {str(e)}")
        return {}


# ==========================================
# OUTPUT DISPATCH FORMATTER
# ==========================================
def format_dispatch_message(data: dict) -> str:
    """Format extracted JSON into exact dispatch template structure required by dispatcher."""
    if not isinstance(data, dict):
        data = {}

    def clean_val(val, default="N/A"):
        if val is None:
            return default
        s = str(val).strip()
        if not s or s.upper() in ["NONE", "NULL", "UNKNOWN"]:
            return default
        return s

    def clean_date_short(val, default="MM/DD"):
        s = clean_val(val, default)
        if s == default:
            return default
        parts = s.split("/")
        if len(parts) >= 2:
            return f"{parts[0].zfill(2)}/{parts[1].zfill(2)}"
        return s

    broker = clean_val(data.get("broker"))
    load_id = clean_val(data.get("load_id"))
    pickup_num = clean_val(data.get("pickup_number"))
    ref_num = clean_val(data.get("ref_number"))

    # Format Rate Currency (e.g. 3937.0$)
    raw_rate = str(data.get("rate", "0")).replace("$", "").replace(",", "").strip()
    try:
        rate_val = float(raw_rate)
        if rate_val.is_integer():
            rate_str = f"{int(rate_val)}"
        else:
            rate_str = f"{rate_val}"
    except ValueError:
        rate_str = raw_rate if raw_rate and raw_rate != "N/A" else "N/A"

    # PU# and REF# — always show the label, value or blank
    pu_num_display = pickup_num if pickup_num and pickup_num not in ["N/A", ""] else ""
    ref_num_display = ref_num if ref_num and ref_num not in ["N/A", ""] else ""

    # Helper to clean strings for location matching
    def clean_str(s):
        return re.sub(r'[^a-z0-9]', '', str(s or '').lower())

    def is_same_location(s1, s2):
        if not isinstance(s1, dict) or not isinstance(s2, dict):
            return False
        f1, f2 = clean_str(s1.get("facility_name")), clean_str(s2.get("facility_name"))
        a1, a2 = clean_str(s1.get("full_address")), clean_str(s2.get("full_address"))
        if f1 and f2 and (f1 in f2 or f2 in f1):
            return True
        if a1 and a2 and (a1 in a2 or a2 in a1):
            return True
        return False

    raw_stops = data.get("stops", [])
    processed_stops = []

    if isinstance(raw_stops, list) and len(raw_stops) >= 2:
        i = 0
        while i < len(raw_stops):
            curr = raw_stops[i]
            nxt = raw_stops[i + 1] if i + 1 < len(raw_stops) else None

            if isinstance(curr, dict) and isinstance(nxt, dict):
                c_type = str(curr.get("type", "")).upper()
                n_type = str(nxt.get("type", "")).upper()

                if c_type == "DEL" and n_type == "PU" and is_same_location(curr, nxt):
                    merged_stop = {
                        "type": "RELOAD",
                        "date": curr.get("date") or nxt.get("date"),
                        "time": f"{curr.get('time', '')} {nxt.get('time', '')}".strip() or "08:00",
                        "pickup_number": nxt.get("pickup_number") or curr.get("pickup_number"),
                        "facility_name": curr.get("facility_name") or nxt.get("facility_name"),
                        "full_address": curr.get("full_address") or nxt.get("full_address")
                    }
                    processed_stops.append(merged_stop)
                    i += 2
                    continue
            processed_stops.append(curr)
            i += 1

    if processed_stops and len(processed_stops) >= 2:
        stop_blocks = []
        has_reload = any(isinstance(s, dict) and str(s.get("type", "")).upper() == "RELOAD" for s in processed_stops)
        pu_count = sum(1 for s in processed_stops if isinstance(s, dict) and str(s.get("type", "")).upper() == "PU")
        del_count = sum(1 for s in processed_stops if isinstance(s, dict) and str(s.get("type", "")).upper() == "DEL")

        is_multistop_diff_addr = not has_reload and (pu_count > 1 or del_count > 1)
        pu_idx = 0
        del_idx = 0

        for idx, stop in enumerate(processed_stops):
            if not isinstance(stop, dict):
                continue
            s_type = str(stop.get("type", "")).upper()
            s_date = clean_date_short(stop.get("date"))
            s_time = clean_val(stop.get("time"), "HH:MM")
            s_fac = clean_val(stop.get("facility_name"))
            s_addr = clean_val(stop.get("full_address"))
            s_pu_num = clean_val(stop.get("pickup_number"), pu_num_display if pu_idx == 0 and s_type == "PU" else "")

            if s_type == "PU":
                pu_idx += 1
                label = f"PU{pu_idx}" if is_multistop_diff_addr else "PU"
                block = f"{label} time : {s_time}  {s_date}\nPU #  {s_pu_num}\n\n{label} location :\n {s_fac}\n{s_addr}"
                stop_blocks.append(block)

            elif s_type == "DEL":
                del_idx += 1
                label = f"DEL{del_idx}" if is_multistop_diff_addr else "DEL"
                block = f"{label} time : {s_time}   {s_date}\n\n{label} location :\n{s_fac}\n{s_addr}"
                stop_blocks.append(block)

            elif s_type == "RELOAD":
                reload_pu = clean_val(stop.get("pickup_number"))
                pu_line = f"\nPU # {reload_pu}" if reload_pu and reload_pu != "N/A" else ""
                block = f"RELOAD time : {s_time}   {s_date}{pu_line}\n{s_fac}\n{s_addr}"
                stop_blocks.append(block)

            else:
                block = f"{s_type} time : {s_time}   {s_date}\n{s_fac}\n{s_addr}"
                stop_blocks.append(block)

        stops_formatted_text = "\n\n".join(stop_blocks)
    else:
        # Single Leg Format
        pu_info = data.get("pickup", {})
        if not isinstance(pu_info, dict):
            pu_info = {}
        pu_date = clean_date_short(pu_info.get("date"), "MM/DD")
        pu_time = clean_val(pu_info.get("time"), "HH:MM")
        pu_facility = clean_val(pu_info.get("facility_name"))
        pu_address = clean_val(pu_info.get("full_address"))

        del_info = data.get("delivery", {})
        if not isinstance(del_info, dict):
            del_info = {}
        del_date = clean_date_short(del_info.get("date"), "MM/DD")
        del_time = clean_val(del_info.get("time"), "HH:MM")
        del_facility = clean_val(del_info.get("facility_name"))
        del_address = clean_val(del_info.get("full_address"))

        stops_formatted_text = f"""PU time : {pu_time}  {pu_date}
PU #  {pu_num_display}

PU location :
 {pu_facility}
{pu_address}

DEL time : {del_time}   {del_date}

DEL location :
{del_facility}
{del_address}"""

    template = f"""Broker: {broker}
LOAD ID : {load_id}

PU#  {pu_num_display}
REF#  {ref_num_display}

{stops_formatted_text}

RATE: {rate_str}$

❌ Late PU: $500
❌ Late DEL: $500
❌ No update: $200
❌ No BOL and PU/DEL trailer photos: $200"""

    return template


# ==========================================
# MAIN APPLICATION INTERFACE
# ==========================================
def main():
    # LOGITEK DISPATCH Liquid Hero Intro Banner
    st.markdown("""
    <div class="logitek-hero-banner">
        <div class="liquid-ambient-aura"></div>
        <div class="logitek-title">LOGITEK DISPATCH</div>
        <div class="logitek-subtitle">JOIN OUR TEAM</div>
    </div>
    """, unsafe_allow_html=True)

    # Set Default AI & Engine Configuration
    provider = "Google Gemini"
    # API key: read from Streamlit secrets (cloud), environment variable, or encoded fallback
    api_key = ""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        import base64
        api_key = base64.b64decode("QVEuQWI4Uk42THhEM3lJdmlIN2txaDg1OHlWZmI0Wjc5bW1ycXRTOVRaOGxqRndKeHRpa3c=").decode("utf-8")

    model_name = "gemini-2.5-flash"
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe" if os.name == 'nt' else "/usr/bin/tesseract"

    # ------------------------------------------
    # MAIN CONTENT: FILE UPLOAD & SAMPLE LOAD
    # ------------------------------------------
    col_up, col_samp = st.columns([4, 1])
    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Rate Confirmation (PDF or Image)",
            type=["pdf", "jpg", "jpeg", "png"],
            help="Upload a logistics Rate Confirmation document in PDF or image format."
        )
    with col_samp:
        st.write("")
        st.write("")
        load_sample = st.button("🧪 Test with Sample RC", width="stretch")
        if load_sample:
            st.session_state["use_sample"] = True

    # Determine input source (Uploaded File vs Sample Data)
    file_bytes = None
    file_name = ""
    file_type = ""

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name
        file_type = uploaded_file.type
        st.session_state["use_sample"] = False
    elif st.session_state.get("use_sample", False):
        # Generate or load synthetic sample PDF
        sample_path = "sample_rc_ch_robinson.pdf"
        if not os.path.exists(sample_path):
            try:
                from generate_sample_rc import generate_pdf_rc
                generate_pdf_rc(sample_path)
            except Exception:
                pass
        
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                file_bytes = f.read()
            file_name = "sample_rc_ch_robinson.pdf"
            file_type = "application/pdf"
            st.info("Loaded sample PDF document: `sample_rc_ch_robinson.pdf`")

    # ------------------------------------------
    # PROCESSING PIPELINE WITH TRUCK ANIMATION
    # ------------------------------------------
    if file_bytes is not None:
        st.markdown("---")

        # Container for active processing animation (will disappear on completion)
        anim_container = st.empty()
        with anim_container.container():
            render_truck_processing_animation("Extracting multi-page document data & dispatching AI engine...")
            progress_bar = st.progress(0)

            # Step 1: Text & Page Image Extraction
            progress_bar.progress(25)

            raw_text = ""
            page_images = []
            is_pdf = file_name.lower().endswith(".pdf") or "pdf" in file_type

            if is_pdf:
                raw_text, page_images = extract_pdf_data(file_bytes, tesseract_cmd=tesseract_path)
            else:
                raw_text = extract_text_from_image(file_bytes, tesseract_cmd=tesseract_path)
                try:
                    img = Image.open(io.BytesIO(file_bytes))
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    page_images = [img]
                except Exception:
                    page_images = []

            progress_bar.progress(55)

            # Step 2: AI Field Extraction
            parsed_data = {}

            if not api_key:
                st.warning(f"⚠️ Please enter your {provider} API Key to complete structured parsing.")
                st.stop()

            if provider == "Google Gemini":
                parsed_data = parse_rc_with_gemini(
                    raw_text=raw_text,
                    api_key=api_key,
                    model_name=model_name,
                    page_images=page_images
                )
            else:
                parsed_data = parse_rc_with_openai(
                    raw_text=raw_text,
                    api_key=api_key,
                    model_name=model_name
                )

            progress_bar.progress(90)

            # Step 3: Format Dispatch Output
            formatted_dispatch = format_dispatch_message(parsed_data)
            progress_bar.progress(100)

        # Clear the truck animation container upon completion!
        anim_container.empty()

        st.success("✅ Rate Confirmation processed successfully!")

        # ------------------------------------------
        # DISPLAY RESULTS IN TABS
        # ------------------------------------------
        tab_dispatch, tab_data, tab_preview = st.tabs([
            "📲 Formatted Dispatch Message",
            "📊 Parsed Data & Raw Text",
            "📄 Document Visualizer"
        ])

        with tab_dispatch:
            st.markdown("### 📋 Ready-to-Send Dispatch Message")
            st.caption("Click the copy button in the top right corner of the box below to copy the dispatch message instantly.")

            # Primary Copyable Output Block
            st.code(formatted_dispatch, language="text")

            # Editable Backup Text Area
            with st.expander("✏️ Edit Message Before Sending"):
                edited_msg = st.text_area("Editable Message", value=formatted_dispatch, height=350)
                st.download_button(
                    label="💾 Download Dispatch Message (.txt)",
                    data=edited_msg,
                    file_name=f"dispatch_{parsed_data.get('load_id', 'load')}.txt",
                    mime="text/plain"
                )

        with tab_data:
            col_json, col_raw = st.columns(2)
            with col_json:
                st.markdown("#### 🧩 Extracted JSON Structure")
                st.json(parsed_data)
            
            with col_raw:
                st.markdown("#### 📝 Raw OCR Extracted Text")
                st.text_area("Raw Document Text", value=raw_text if raw_text else "(No OCR text extracted directly)", height=380)

        with tab_preview:
            st.markdown("#### 🖼️ Rate Confirmation Document Preview")
            if page_images:
                for idx, img in enumerate(page_images):
                    st.image(img, caption=f"Page {idx + 1}", width="stretch")
            else:
                st.info("No visual document preview available.")


if __name__ == "__main__":
    main()
