# Amazon Auto Lister

Amazon Auto Lister is a web application designed to automatically generate Amazon listing templates from item directories and master sheets using smart mapping, custom value translations, and category-specific rules.

The system is split into:
1. **Frontend**: Next.js (React) application built with Tailwind CSS.
2. **Backend**: FastAPI (Python) backend using SQLAlchemy (SQLite/PostgreSQL) and openpyxl/pandas for spreadsheet processing.

---

## Repository Structure

```
├── backend/                  # Python API Service (FastAPI)
│   ├── main.py               # API routes and task triggers
│   ├── database.py           # SQL Alchemy database configs
│   ├── models.py             # DB Schema (tasks, source files, mappings, rules)
│   ├── requirements.txt      # Python dependencies
│   └── services/             # Core engines (generation, validation, rule matching)
├── frontend/                 # Next.js Web App
│   ├── src/app/              # Next.js routing and UI components
│   ├── package.json          # Node dependencies
│   └── tsconfig.json         # TypeScript configuration
├── Procfile                  # Startup command for web hosting
├── docker-compose.yml        # Development environment runner
└── requirements.txt          # Root Python dependencies for Railway auto-detection
```

---

## Local Setup

### Prerequisite:
- Python 3.10+
- Node.js 18+

### 1. Run the Backend API

Navigate to the `backend/` directory or run from the root:

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start the development server (default port: 8001)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

The API will be accessible at `http://localhost:8001`. You can view the interactive documentation at `http://localhost:8001/docs`.

### 2. Run the Frontend App

Navigate to the `frontend/` directory:

```bash
cd frontend

# Install packages
npm install

# Start Next.js development server
npm run dev
```

The frontend will run at `http://localhost:3000`.

---

## Production Deployment on Railway

This repository is optimized for quick, two-click deployments to **Railway**.

### 1. Host the Backend API
1. Deploy a new service from your GitHub repository `MNegi17/Amazon-AutoLister`.
2. Under the service settings, mount a **Persistent Volume** to `/app/data` (to persist database rows, uploaded templates, and outputs).
3. Set the following **Environment Variables**:
   - `UPLOAD_DIR` = `/app/data/uploads`
   - `OUTPUT_DIR` = `/app/data/outputs`
   - `DATABASE_URL` = `sqlite:////app/data/amazon_autolister.db`
4. Under **Networking**, click **Generate Domain** and copy the public URL.

### 2. Host the Frontend Web App
1. In the same project, deploy another service from the same GitHub repository.
2. Under its **Settings**, set the **Root Directory** to `/frontend`.
3. Set the following **Environment Variables**:
   - `NEXT_PUBLIC_API_URL` = `<your_backend_domain_url>`
4. Under **Networking**, click **Generate Domain** to access your public frontend application!
