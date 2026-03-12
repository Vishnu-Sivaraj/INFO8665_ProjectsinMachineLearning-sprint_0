# 🎙️ INSIGHT-311: AI-Driven Voice Assistant

**INSIGHT-311** is an automated voice-driven assistant designed to streamline 311 municipal service requests. By leveraging Speech-to-Text (STT) and Natural Language Understanding (NLU), it automates the intake, classification, and prioritization of citizen reports through a multi-turn conversational interface.

---

## 🏗️ System Architecture

The project has been restructured into a Monorepo containing the following components:

### 1. **Backend API Service** (`backend/src/api/ml_service.py`)
* A Flask-based backend that manages the lifecycle of a call.
* Exposes endpoints for NLU processing, orchestration logic, and STT/TTS integration.

### 2. **Dialog Orchestrator** (`backend/src/ai_orchestration/orchestrator.py`)
* Acts as the "Brain" of the conversation using slot-filling techniques.
* Manages required fields: `category`, `location`, `description`, `caller_name`, and `phone_number`.
* Implements confidence-based logic to handle clarifications and final ticket submission.

### 3. **React Web UI** (`frontend/web-agent/`)
* A Vite + React web portal for agents to view incoming 311 tickets and listen to the recorded calls.

### 4. **Call Simulation Engine** (`backend/tests/test_call.py`)
* A CLI utility that simulates a real-world phone interaction.
* Captures user voice input, displays real-time NLU confidence scores, and executes orchestrated responses.

---

## 🚀 Getting Started

### **Prerequisites**
- **Python 3.10+**
- **PostgreSQL Database** with `tickets` and `sessions` tables.
- **Virtual Environment** setup:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/activate

pip install -r requirements.txt
```

### **Environment Configuration (Mandatory)**
Because database credentials are intentionally excluded from version control, you must create a `.env` file in the **root** of the project before running:
```env
NEON_DB_URL="postgresql://<username>:<password>@<host>/neondb?sslmode=require"
```

### **NLU Model Training (Mandatory)**
Model artifacts are local and ignored by Git. You must train the DistilBERT classifier before first use:

1. Ensure training data exists in `data/models/training_data.json`.
2. Execute training script:
   ```bash
   cd scripts
   python train_nlu_model.py
   ```
   ```
3. Artifacts will be saved to `ml_models/saved_models/category_classifier/`.

---

## 🛠️ Usage Guide

To run the full simulation, you need to start both local servers and the CLI script:

### **Terminal 1: The API Server**
```bash
python backend/src/api/ml_service.py
```

### **Terminal 2: The React Web Dashboard**
```bash
cd frontend/web-agent
npm install
npm run dev
```

### **Terminal 3: Demo the Voicebot (CLI)**
```bash
python backend/tests/test_call.py
```

---

## 📊 Database Schema

The `tickets` table in PostgreSQL should include the following schema to ensure compatibility with `update_ticket()`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `ticket_id` | VARCHAR | Unique ID (e.g., TKT-2026...) |
| `category` | VARCHAR | Extracted 311 service category |
| `location` | TEXT | Physical location of the issue |
| `description` | TEXT | Detailed incident description |
| `caller_name` | VARCHAR | Citizen's full name |
| `phone_number`| VARCHAR | Contact information |
| `confirmed` | BOOLEAN | Submission status |

---

## 🔍 NLU Categories
The system is trained to recognize the following official categories:
* `graffiti`, `illegal_sign`, `litter`, `needles`, `parking_complaint`, `property_standards`, `pothole`, `sidewalk_snow`, `sidewalk_hazard`, `trail_maintenance`.

---

## 📝 Confidence Calculation
The orchestrator computes the reliability of an intake session using the following formula:

$$Overall = \frac{1}{n} \sum_{i=1}^{n} Confidence_i$$

Where $n$ represents the number of required fields.

---

## 💡 Team Notes
- **API/Orchestrator changes:** Restart Terminal 1 to reload logic.
- **Script-only changes:** Simply re-run Terminal 2.
- **Database Errors:** If you see "column does not exist," verify your PostgreSQL schema matches the table above.