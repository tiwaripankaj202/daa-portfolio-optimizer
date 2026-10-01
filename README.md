# Portfolio Lab: 0/1 Knapsack

An educational full-stack portfolio optimizer comparing recursive brute force with bottom-up dynamic programming. It reports selected assets, expected return, measured runtime, and a log-scale benchmark chart.

## Project Layout

```text
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── optimizer.py
│   ├── requirements.txt
│   └── tests/test_optimizer.py
├── frontend/
│   ├── src/App.jsx
│   ├── src/main.jsx
│   ├── src/styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── render.yaml
└── README.md
```

## Phase 1: VS Code Setup

Open this project folder in VS Code. Install the Python and Pylance extensions (`ms-python.python` and `ms-python.vscode-pylance`). Thunder Client or REST Client is optional for testing the API from VS Code.

Install Node.js LTS and Git from their official installers, then restart VS Code so its terminals pick up the new PATH. Verify they are available:

```powershell
node --version
npm --version
git --version
```

In PowerShell, create and activate a virtual environment, then install backend dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. Install Node.js 20 or newer and Git if they are not already available. Initialize version control from the project root:

```powershell
git init
git add .
git commit -m "Build portfolio optimizer app"
```

The `.gitignore` excludes virtual environments, generated frontend files, local env files, and Python caches.

## Phase 2: FastAPI Backend

`backend/app/optimizer.py` implements both algorithms and uses `time.perf_counter()` around the full solve, including reconstruction of selected items.

- `POST /api/optimize` accepts `{ "assets": [{"name":"Fund", "cost":100, "expected_return":25}], "budget":100, "algorithm":"dp" }`. Use `brute_force` for the recursive solver. Response includes maximum expected return, selected assets, total cost, runtime, and complexity labels.
- `POST /api/benchmark` accepts `{ "max_assets":19, "budget":1000 }` and returns samples for N = 5, 7, 9, ... . Asset pools are deterministic per N so the chart is reproducible.
- `GET /api/health` is the deployment health check.

The benchmark caps N at 23 to bound exponential work. DP reconstructs an optimal set using divide-and-conquer and one-dimensional knapsack arrays: O(N * B) time, O(B) DP working memory, plus O(log N) reconstruction stack and O(N) returned items. Brute force uses O(2^N) time and O(N) recursion/selection state.

## Phase 3: React/Vite Frontend

The UI lets you edit the candidate pool and budget, choose an algorithm, inspect its solution and empirical runtime, then request a benchmark. Recharts renders the returned runtime values on a logarithmic Y axis. The default API address is `http://127.0.0.1:8000`; deployments use `VITE_API_BASE_URL` (the older `VITE_API_URL` name remains a fallback).

## Phase 4: Run Locally

Open two VS Code terminals at the project root.

Terminal 1, backend:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Terminal 2, frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (usually `http://localhost:5173`). FastAPI's interactive API docs are at `http://127.0.0.1:8000/docs`.

Verify health and try a request from PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
$body = '{"assets":[{"name":"Index fund","cost":6,"expected_return":30},{"name":"Bond fund","cost":3,"expected_return":14},{"name":"Growth fund","cost":4,"expected_return":16}],"budget":9,"algorithm":"dp"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/optimize -ContentType 'application/json' -Body $body
```

Run the algorithm tests from the root:

```powershell
python -m unittest discover -s backend\tests
```

CORS allows the local Vite origins by default. For production, set backend `CORS_ORIGINS` to the exact deployed frontend origin (no trailing slash). Never use `*` with credentials enabled.

## Phase 5: Deploy

### Push to GitHub

Create an empty GitHub repository, then from the project root:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/portfolio-lab.git
git branch -M main
git push -u origin main
```

### Backend on Render

1. In Render, create a new Blueprint and select the GitHub repository. The checked-in `render.yaml` configures the Python service, `backend` root, build command, Uvicorn start command, and health check.
2. Set `CORS_ORIGINS` to the frontend's eventual production origin, for example `https://portfolio-lab.vercel.app`. Render will prompt for this because it is marked `sync: false`.
3. Deploy. Verify `https://YOUR-API.onrender.com/api/health` returns `{"status":"ok"}`. Copy the service URL.

Alternatively create a Render Web Service manually with root directory `backend`, build command `pip install -r requirements.txt`, and start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set `CORS_ORIGINS` in its environment.

### Frontend on Vercel

1. Import the same GitHub repository into Vercel and set the project root to `frontend`.
2. Set `VITE_API_BASE_URL` to the Render service URL, such as `https://YOUR-API.onrender.com` (no trailing slash).
3. Deploy. Copy the resulting `https://...vercel.app` origin and add that exact origin to the backend's `CORS_ORIGINS`, then redeploy/restart the backend.

For Netlify, choose `frontend` as the base directory, `npm run build` as the build command, `dist` as the publish directory, and configure the same `VITE_API_BASE_URL` environment variable. Add the resulting Netlify origin to backend CORS.

## Phase 6: Production Verification

Open the deployed frontend, optimize the starter assets with each algorithm, add/remove an asset, and run the benchmark. Check the browser Network panel for successful `POST /api/optimize` and `POST /api/benchmark` responses, and confirm the chart has both series. If requests fail, verify `VITE_API_BASE_URL`, backend availability, and the exact frontend origin in `CORS_ORIGINS`; rebuild/redeploy the frontend after changing its Vite environment variable.

Cold-start services on free hosting may take a short while to respond. Benchmark timings are machine- and workload-dependent measurements, not formal proofs of asymptotic complexity.
