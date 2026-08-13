# Mantask

Mantask is a task management application designed to help users organize and prioritize their tasks effectively. It offers features such as task creation, categorization, and deadline tracking, allowing users to stay on top of their responsibilities and improve productivity. With an intuitive interface and customizable options, Mantask aims to provide a seamless experience for managing daily tasks and long-term projects.

## Local Development

Requirements: Docker, Python 3.12+, Node.js 20.19+ (or 22.12+), and npm.

1. Create `.env` from the example if it does not already exist. Set `BOOTSTRAP_SECRET` to a long random value.

   ```bash
   cp .env.example .env
   ```

2. Start PostgreSQL:

   ```bash
   docker compose up -d db
   ```

3. Create the backend virtual environment and install dependencies if needed:

   ```bash
   python3 -m venv backend/.venv
   backend/.venv/bin/python -m pip install -r backend/requirements.txt
   ```

4. Apply database migrations:

   ```bash
   backend/.venv/bin/python -m alembic upgrade head
   ```

5. Run the backend from the repository root:

   ```bash
   backend/.venv/bin/python -m uvicorn backend.app.main:app --reload
   ```

6. In another terminal, install frontend dependencies and start Vite:

   ```bash
   cd frontend
   npm ci
   npm run dev
   ```

Open `http://localhost:5173`. On the first run, complete the setup form using the `BOOTSTRAP_SECRET` from `.env`.

The backend health check is available at `http://localhost:8000/health`.

## Bootstrap

Set `BOOTSTRAP_SECRET` in your deployment environment before first launch. Use a long random value, and have the initial setup screen send the same secret with the bootstrap request.

## Notes

- When you have a task where user is assigned as assignee, then only that user can work with the task.
-> Have simple if check at each task operation that throws errors early.
