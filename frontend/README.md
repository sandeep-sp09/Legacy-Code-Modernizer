# Frontend / User Interface

The **Legacy Code Modernizer** frontend provides an intuitive, high-performance user interface for transforming legacy Pascal and C source code into idiomatic modern C++.

## Options Available

### Option 1: Modern Web Application (Recommended)
A rich, responsive Web UI with dark mode, glassmorphism, animated pipeline stepper, drag-and-drop file ingestion, physics-based interactive call-graph visualization, side-by-side diff comparison, and live telemetry.

- **Location**: `frontend/index.html`, `frontend/style.css`, `frontend/app.js`
- **Features**:
  - **Pipeline Stepper**: Visual tracking of Source Ingestion &rarr; AST & IR Extraction &rarr; Call Graph Analysis &rarr; LLM Synthesis &rarr; Validation & Diff.
  - **Interactive Call Graph**: HTML5 Canvas force-directed graph with pan, zoom, node drag, node inspector drawer, and caller/callee inspection.
  - **Side-by-Side Diff**: Synchronized dual-pane diff comparison and unified patch mode.
  - **Quick-Load Samples**: Built-in Pascal (`sample1.pas`, loop matrix) and C (`sample1.c`) presets.
  - **Direct Backend Integration**: Connects to FastAPI backend (`http://localhost:8000`) with auto-fallback to offline Demo Mode.
  - **Modern C++ Actions**: 1-click clipboard copy and `.cpp` file download.

#### How to run:
Simply open `frontend/index.html` in any modern web browser, or serve via any static web server:
```bash
# Using Python
python -m http.server 3000 --directory frontend

# Or using Node / npx
npx serve frontend
```
Then visit `http://localhost:3000`.

---

### Option 2: Streamlit Application
A Python-based dashboard for rapid data science and experimentation.

- **Location**: `frontend/app.py`
- **Features**:
  - Sidebar configuration with backend health checks.
  - File uploader and quick sample selector.
  - Matplotlib / NetworkX call graph visualization.
  - Side-by-side legacy vs. modern C++ comparison columns.
  - Unified diff view and `.cpp` file download button.

#### How to run:
```bash
pip install streamlit networkx matplotlib requests
streamlit run frontend/app.py
```

---

## Backend API Endpoints Used
The frontend communicates with the FastAPI service:
- `GET /health` &mdash; Connection health check.
- `POST /upload` &mdash; Ingests `.pas`, `.pp`, `.dpr`, `.lpr`, `.c`, or `.h` source file.
- `POST /process/{file_id}` &mdash; Executes AST extraction, dependency graph generation, and LLM modernizer pipeline.
- `GET /result/{file_id}` &mdash; Retrieves cached processing results.

## Upload only the browser frontend to GitHub

For a frontend-only GitHub repository, upload these three files:

```text
index.html
style.css
app.js
```

Do not upload `backend/`, `.venv/`, `__pycache__/`, tests, or `frontend/app.py` unless
you also want to publish the optional Streamlit application. The browser frontend
works without the backend: it automatically uses the local Offline Demo Mode and
shows a notification when FastAPI is unavailable.

### GitHub upload from the command line

From inside the `frontend` directory:

```bash
git init
git add index.html style.css app.js
git commit -m "Add frontend web application"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repository>.git
git push -u origin main
```

Replace the placeholder repository URL with your GitHub repository URL. To run
the uploaded frontend locally, use a static server (for example
`python -m http.server 3000`) from the same directory and open
`http://localhost:3000`.
