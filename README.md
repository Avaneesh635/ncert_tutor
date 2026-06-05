# NCERT Class 12 Tutor Assignment

Starter for a local AI tutor assignment. The API runs once configured with an OpenAI key, but it does not yet know the NCERT books. Teach the bot Class 12 CBSE Mathematics, Physics, and Chemistry.

## Setup

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

Set `OPENAI_API_KEY` in `backend/.env`, then:

```bash
PYTHONPATH=. uvicorn backend.main:app --reload --port 8000
```

## Chat API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Explain definite integrals."}]}'
```

## Data

See `data/README.md`. Download the six NCERT PDFs into `data/raw/`.

## Evals

With the backend running:

```bash
PYTHONPATH=. python -m evals.run_evals
```

Reports are written to `evals/reports/`.

## Frontend

Optional. See `frontend/README.md`.

## Submission

Do not push your solution to this starter repo. Create a new private GitHub repo, push your completed solution there, invite `abhishektayal2802` as a collaborator, and send us the repo URL.

