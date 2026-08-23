# 🚛 Logistika Dispatch - Rate Confirmation (RC) Data Extractor

A modern, full-stack Python Streamlit web application designed for logistics dispatchers to automate data extraction from Rate Confirmation (RC) PDF and Image files (.pdf, .jpg, .jpeg, .png) and instantly format them into standardized dispatch messages.

---

## 🌟 Key Features

- **Document Processing**:
  - **PDF Documents**: Raw text extraction using `pdfplumber`.
  - **Image Documents**: OCR text extraction using `pytesseract` with automatic image pre-processing.
- **AI Parsing Engine**:
  - Structured extraction using **Google Gemini** (`google-generativeai`) or **OpenAI** (`openai`).
  - Extracted JSON schema: Broker, Load ID, Pickup #, Reference #, Pickup (Date, Time, Facility, Address), Delivery (Date, Time, Facility, Address), and Agreed Rate.
- **1-Click Copy Dispatch Template**:
  - Standardized formatting with precise whitespace, bold headers, and penalty disclosures.
  - Interactive `st.code()` with single-click copy button.
  - Editable text box and `.txt` file download option.
- **Document & Data Visualizer**:
  - Inspect structured JSON output and raw OCR text side-by-side.
  - Visual preview of PDF pages and uploaded images.
- **Built-in Test Drive**:
  - Generate and test synthetic Rate Confirmation documents instantly.

---

## 📋 Required Formatting Output

The application formats extracted data into this exact structure:

```text
Broker: [Broker Name]
LOAD ID: [Load ID]

PICKUP# [Pickup Number]
REF# [Reference Number]

PU: [MM/DD/YYYY] [HH:MM]
[Pickup Facility]
[Pickup Full Address]

DEL1: [MM/DD/YYYY] [HH:MM]
[Delivery Facility]
[Delivery Full Address]

RATE: $[Rate]

❌ Late PU: $500
❌ Late DEL: $500
❌ No update: $200
❌ No BOL and PU/DEL trailer photos: $200
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation

Ensure Python 3.10+ is installed on your system.

Install Python dependencies:

```bash
pip install -r requirements.txt
```

*(Optional for Image OCR)*: Install Tesseract OCR on your system:
- **Windows**: Download installer from [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki) (default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

### 2. Generate Sample Rate Confirmations (Optional)

To test the application without uploading real sensitive documents, generate sample PDF and PNG files:

```bash
python generate_sample_rc.py
```

### 3. Set API Keys (Optional)

You can set your API key as an environment variable or enter it directly in the app sidebar:

- **Google Gemini**: `export GEMINI_API_KEY="your-gemini-api-key"`
- **OpenAI**: `export OPENAI_API_KEY="your-openai-api-key"`

### 4. Run the Streamlit Web Application

Launch the app locally:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
logistika dispatch/
├── app.py                   # Main Streamlit application
├── generate_sample_rc.py    # Synthetic PDF & PNG RC generator
├── requirements.txt         # Python package requirements
└── README.md                # Documentation & usage guide
```
