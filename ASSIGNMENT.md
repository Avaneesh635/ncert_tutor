# Founding Engineer Take-Home: NCERT Class 12 Tutor

## Goal

Build a local AI tutor that knows Class 12 CBSE Mathematics, Physics, and Chemistry.

You will start from a small chat API. Download the official NCERT PDFs and teach the bot the syllabus.

## What You Are Given

- A FastAPI backend with a small OpenAI-backed starter agent.
- An optional `frontend/` placeholder.
- A manifest of the required Class 12 NCERT books.
- A visible eval prompt suite you can run locally.

The starter agent does not know the books yet. By the end, it should.

## Data

Download the Class 12 PDFs from [NCERT](https://ncert.nic.in/textbook.php).

Use `data/manifest.json` for the required books and suggested filenames under `data/raw/`.

## Required

- Run locally.
- Answer Class 12 Math, Physics, and Chemistry questions using the downloaded NCERT books.
- Refuse or redirect questions clearly outside Class 12 PCM.
- Include a README with setup, architecture, tradeoffs, limitations, and how to run evals.

## Model Policy

The starter defaults to OpenAI. You may use another hosted or local model if your README explains the tradeoff.

- Use your own API keys.
- Do not commit secrets.
- Local-only is enough.

## Bonus

- Source citations.
- Frontend.
- Rerunnable setup from raw PDFs.

## Evaluation

We will review:

- Fresh setup.
- Whether the bot knows the NCERT books.
- Out-of-scope behavior.
- Code clarity and extensibility.
- README quality.
- Visible eval results.

We will also run private prompts and discuss your design in a walkthrough.

## Submission

Submit a GitHub repo or zip with:

- Final code.
- README.
- Visible eval outputs or a short eval summary.
- Brief worklog with AI tools used and key design decisions.

Do not include API keys, `.env` files, virtual environments, or large downloaded PDFs.
