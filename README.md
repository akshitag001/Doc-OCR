# Doc-OCR 📄🤖

Doc-OCR is a state-of-the-art, production-ready, full-stack document understanding system designed to automatically transform raw, unstructured academic certificates, marksheets, and official credentials into highly structured, verified academic records in clean JSON format. 

By utilizing advanced **Computer Vision**, a hybrid multi-engine **OCR pipeline**, and modern **Large Language Model (LLM)** semantic reasoning, Doc-OCR automates manual document processing and data-entry tasks for registrar, verification, and HR teams.

---

## 🌟 Key Features

*   **Multi-Format Document Ingestion**: Upload PDFs, PNGs, and JPEGs up to 10MB. Multi-page PDFs are automatically split, processed, and merged.
*   **Dual-Engine OCR Pipeline**: A hybrid OCR framework combining EasyOCR (deep-learning-based) and Tesseract (pattern-matching-based fallback) for high-accuracy text extraction.
*   **Semantic Entity Extraction**: High-fidelity semantic understanding via the Gemini API to extract complex fields (holder details, credentials, CGPA/SGPA, issuer credentials) directly from OCR spatial layout.
*   **Zero-Dependency Fallback Mode**: Even without a Gemini API key, a robust rule-based NLP parser extracts core data so the system remains fully operational locally.
*   **Modern Real-Time UI**: A premium user interface complete with interactive drag-and-drop uploads, real-time status trackers, progress steps, dynamic previews, and interactive JSON schemas.
*   **Completely Dockerized**: A fully orchestrated microservices layout using `docker-compose` for rapid, production-ready deployment.

---

## 🏗️ Architecture & Data Flow

The platform is designed with a modern, decoupled microservices architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        NEXT.JS FRONTEND (APP ROUTER)                   │
│  - Premium Tailwind UI                                                │
│  - Drag & Drop Zone                                                    │
│  - Real-Time API Proxy (Next.js API route handlers)                    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │  HTTP / POST
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                                │
│  - Asynchronous background jobs                                        │
│  - Job runner state management                                         │
│  - Local disk storage (highly secure & configurable)                    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │  Internal Pipeline Execution
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       AI & EXTRACTOR PIPELINE                         │
│  1. Preprocessing: Resizing, deskewing, binarization                   │
│  2. OCR Engine: EasyOCR + Tesseract Fallback Engine                    │
│  3. LLM Service: Semantic extraction & structure with Google Gemini    │
│  4. Rule-Based Fallback: Smart heuristic-based pattern matching        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Deep Dive: How the AI/ML Works

Doc-OCR's backend relies on a pipeline of advanced machine learning and computer vision techniques:

### 1. Computer Vision Preprocessing
Before character recognition begins, the upload undergoes quality-enhancement steps to maximize accuracy:
*   **Image Binarization & Thresholding**: Adjusts contrast and converts grayscale pages to high-contrast binary structures to isolate text from noisy watermarks and colored backgrounds.
*   **Deskewing**: Detects horizontal text lines and computes orientation skew, automatically rotating the document back to `0` degrees.
*   **Resolution Upscaling**: Low-DPI documents are upscaled using bicubic interpolation to refine character edges.

### 2. Dual-Engine OCR Framework
*   **Primary OCR (EasyOCR)**: Uses a deep learning approach featuring a **ResNet** or **VGG** backbone for feature extraction, combined with a **BiLSTM** sequence labeler and **CTC (Connectionist Temporal Classification)** decoding. This model excels on modern, styled certificates.
*   **Fallback OCR (Tesseract)**: If character-level confidence drops below a threshold, the engine invokes **Tesseract OCR**, which uses traditional line finding, baseline fitting, and character cell segmentation alongside an LSTM character recognizer.

### 3. LLM-Based Semantic Synthesis (Gemini)
Traditional OCR gives you a bag of words with page coordinates. To turn this into intelligent database columns (e.g., separating "Cumulative Grade Point Average" from "Subject Grades"), Doc-OCR passes the spatial OCR blocks and text flow to **Gemini**:
*   The raw text and word-bounding coordinates are structured into a prompt instructing Gemini to act as a structured extraction agent.
*   It automatically handles complex, variable certificate layouts, spelling corrections of misread characters, and translates SGPA/CGPA formulas into standard decimal scores.
*   The system parses the output into a precise, typed JSON schema.

---

## 🛠️ Local Installation & Setup

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Tesseract OCR engine installed on your system path (if running locally without Docker).

---

### Root Environment Variables
Create a `.env` file at the root of the project (refer to `.env.example`).
> [!IMPORTANT]
> The space for `GEMINI_API_KEY` is left blank by default. Please paste your own API key to enable LLM semantic features.

```env
# Root .env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

### Step-by-Step Local Deployment

#### 1. Backend Setup
```bash
cd backend
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*The backend server will run at: `http://localhost:8000`*

#### 2. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
*The web interface will run at: `http://localhost:3000`*

---

### 🐳 Run with Docker (Recommended)
You do not need to install Python, Node, or Tesseract on your system when deploying through Docker.

1. Create your root `.env` and fill in your `GEMINI_API_KEY`.
2. Spin up the entire environment with a single command:
   ```bash
   docker-compose up --build
   ```
3. Open your browser and navigate to: `http://localhost:3000`.

---

## 📂 API Specifications

### `POST /api/documents/process`
Uploads a document to start an extraction job.
*   **Payload**: `multipart/form-data` containing `file`.
*   **Response**:
    ```json
    {
      "job_id": "8f2a9c14-5d3e-4b6f-8a1c-9d0e2b4f6a8c",
      "status": "PROCESSING"
    }
    ```

### `GET /api/documents/{id}/result`
Fetches the current status and extracted JSON for a specific job.
*   **Response**:
    ```json
    {
      "job_id": "8f2a9c14-5d3e-4b6f-8a1c-9d0e2b4f6a8c",
      "status": "COMPLETED",
      "result": {
        "holder": {
          "name": "Jane Doe",
          "dob": "1998-05-15"
        },
        "credential": {
          "degree": "Bachelor of Technology in Computer Science",
          "institution": "State University of Technology",
          "year": "2020",
          "cgpa": "9.2"
        },
        "documentType": "DEGREE_CERTIFICATE"
      }
    }
    ```

---

## 🔮 Future Roadmap & Ideas

We are actively designing the next phase of Doc-OCR. Future improvements include:

*   **Layout-Aware Deep Extraction**: Implement spatial Transformer models (like LayoutLMv3) to recognize and extract multi-column tables, grids of marks, and individual subject credits natively.
*   **Multi-Language OCR Support**: Integrate script-specific OCR packages to support documents in Hindi, Spanish, Arabic, Japanese, and other regional scripts.
*   **Blockchain-Based Digital Verifications**: Align outputs to W3C Verifiable Credentials (VCs) standardizing automatic cryptographic matches against registrar signatures.
*   **Automated QR-Code Cross-Reference**: Instantly decode embedded security QR codes on certificates and verify that the printed text matches the QR-encoded payload exactly.
*   **Distributed Processing Queue**: Integrate **Celery & Redis** to handle massive, concurrent batch uploads (thousands of files at once) without bottlenecking the API threads.
