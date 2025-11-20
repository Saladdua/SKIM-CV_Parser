<div align="center">

<img src="assets/banner.png" alt="SKIM App Icon" width="100%" />

# SKIM: CV Parser

[Download](#download) ✦ [Features](#features) ✦ [Use Cases](#use-cases) ✦ [How to Install](#installation-for-developers) ✦ [License](#license)

**System for Knowledge Identification & Management.**
A powerful desktop application designed to streamline the process of extracting structured data from unstructured documents (PDF, DOCX) and seamlessly uploading it to Google Sheets[cite: 289].

SKIM is specifically optimized for **Recruitment** workflows, featuring intelligent candidate filtering based on Job Descriptions (JD).

</div>

<br>

<div align="center">
    
[![Download](https://img.shields.io/badge/Download-Google%20Drive-0F9D58?labelColor=black&logo=google-drive&style=for-the-badge)](https://drive.google.com/file/d/1zcVNYadhuWsKsUGAKjtAkegBorvdCqZf/view?usp=sharing)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blueviolet?style=for-the-badge&logo=python)](https://www.python.org/)
[![Powered by LandingAI](https://img.shields.io/badge/Powered%20by-LandingAI-orange?style=for-the-badge)](https://landing.ai/)

</div>

> [!IMPORTANT]
> **Agentic Document Extraction (ADE)**: SKIM leverages advanced AI from LandingAI to allow users to define custom data schemas. This ensures highly accurate and tailored data extraction for various use cases, from CV parsing to invoice processing.

## 🌟 Features

SKIM is built to make data extraction effortless and efficient. Here are the key capabilities:

-   **🧠 Agentic Document Extraction (ADE):** Utilizes LandingAI's sophisticated AI to "read" and understand documents like a human, extracting information based on your defined schema[cite: 292].
-   **🎯 Smart Candidate Filtering:**
    -   Automatically filters out CVs that do not meet Job Description (JD) requirements.
    -   Supports filtering by: **Years of Experience** (Min/Max) and **University** (Preferred/Excluded).
    -   Users can create, edit, and delete JD filters directly within the app.
-   **⚙️ Flexible Schema Customization:**
    -   Define exactly what data needs to be extracted (e.g., "Candidate Name", "Skills", "Recent Projects").
    -   Easily Add, Edit, or Remove fields via an intuitive GUI.
-   **📂 Configuration Import/Export:** Easily share filter sets and schemas with colleagues via `.json` files without exposing sensitive information like API Keys.
-   **📊 Google Sheets Integration:** Automatically uploads extracted and filtered data to a specified Google Sheet, organized into columns matching your schema.
-   **📄 Multi-Format Support:** Process both **PDF** and **DOCX** files seamlessly.
-   **💸 Credit Cost Optimization:** Automatically detects and splits PDF files (processing only the first few pages containing key info) to save AI credits when handling applications with long portfolios.
-   **🖥️ Intuitive User Interface:** A clean and easy-to-use desktop application built with Tkinter.

## 🔭 Use Cases

SKIM is versatile and can be adapted for various industries:

| Use Case | Description |
| :--- | :--- |
| **CV Parsing & Filtering** | **(Primary)** Automatically extract candidate details from batches of CVs. Filter out candidates matching specific recruitment criteria (Experience, Education) before pushing valid profiles to the management system.  |
| **Invoice Processing** | Automate data entry for invoice numbers, dates, line items, and totals from scanned or PDF invoices. |
| **Project Data Collection** | Extract specific project details (contractor, scope, investor) from capability profiles or reports.  |
| **Research Data Aggregation** | Automatically collect specific data points from academic papers or market reports.  |

## 🔰 Getting Started

### 💻 Prerequisites

Before you begin, ensure you have the following:

| Component | Requirement |
| :--- | :--- |
| **Python** | Version 3.8+ installed on your system.  |
| **Google Cloud** | A Project with **Sheets API** & **Drive API** enabled. You need the `credentials.json` file (OAuth 2.0 Client ID).  |
| **LandingAI** | A LandingAI account and **API Key** for the extraction service.  |

### ⚙ Installation (For Developers)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Saladdua/SKIM-CV_Parser.git](https://github.com/Saladdua/SKIM-CV_Parser.git)
    cd SKIM-CV_Parser
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate # Windows
    # source venv/bin/activate # macOS/Linux
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(If `requirements.txt` is missing, manually install: `pip install tk tooltip requests google-api-python-client google-auth-oauthlib google-auth-httplib2 pypdf`)* 

## 🕹 Usage

### Configuration and Running

1.  **Preparation:** Place your `credentials.json` file (from Google Cloud) in the project root directory (or select the path in Settings.
2.  **Run the application:** 
    ```bash
    python main_app.py
    ```
3.  **First-time Setup (Setup Wizard):**
    * The app will automatically open the Setup Wizard if no configuration is found.
    * Enter your **LandingAI API Key**.
    * Select your **Google Credentials** file (`credentials.json`).
    * Enter the **Google Sheet ID** and **Sheet Name** (Tab name).
    * Click "Save & Finish".

4.  **Workflow:**
    * **Step 1: Login:** Click "Login to Google" to authorize write access to your Sheet.
    * **Step 2: Select Files:** Choose one or multiple CV files (PDF/DOCX.
    * **Step 3: Process AI (ADE):** Click "Process ADE" to let the AI analyze the documents.
    * **Step 4: Filter & Upload:**
        * Select a Job Position (Filter) from the dropdown menu (e.g., "Structural Engineer").
        * Click "Filter & Upload". The system will automatically reject candidates who don't meet the criteria and upload only "PASS" candidates to Google Sheets.

5.  **Advanced Management:**
    * **⚙️ Schema:** Open to add/remove data fields you want the AI to extract.
    * **⚙️ Filters (Gear Icon):** Open to create new Job Positions with specific filtering criteria (Experience range, Target Universities).
    * **File Menu:** Use **Import/Export Config** to backup or share your filters and schemas with colleagues.

## ⚒ Building an Executable (For End-Users)

To create a standalone `.exe` file that users can run without installing Python:

1.  **Install PyInstaller:** `pip install pyinstaller`
2.  **Navigate to your project root** in the terminal.
3.  **Run the build command:** 
    ```bash
    pyinstaller --noconsole --onefile --icon=app_icon.ico --add-data "app_icon.ico;." main_app.py
    ```
4.  The executable `SKIM - CV Parser.exe` will be located in the `dist` folder.

## 🧾 License

This project is open-source and available under the [MIT License](LICENSE).
