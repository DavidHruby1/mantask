## Project Purpose

Mantask is a lightweight, self-hosted task and workflow management application for small teams. It helps teams organize work through shared Kanban and list views, structured Inbox triage, explicit work-in-progress limits, reviews, debriefs, and blocker handshakes. The product is intended to reduce coordination overhead while keeping ownership, priorities, and workflow state visible. It is designed to be fast, keyboard-oriented, and practical to operate on a small self-hosted environment.

## Tech Stack & Dependencies

**Backend (Python 3.12.3):**

- Runtime: FastAPI 0.136.1, SQLAlchemy 2.0.49, Pydantic 2.13.4, Pydantic Settings 2.14.0, email-validator 2.3.0, python-dotenv 1.2.2, argon2-cffi 25.1.0, and psycopg 3.3.4 with its binary package.
- Database migrations: Alembic 1.18.4.
- Testing: pytest 9.1.1 and pytest-cov 7.1.0.
- Development server: Uvicorn 0.51.0 is installed in the local virtual environment but is not currently declared in `backend/requirements.txt`.

**Frontend (Node 24.14.1; supported range `^20.19.0 || >=22.12.0`):**

- Runtime and UI: Vue ^3.5.29, Vue Router ^5.0.3, Pinia ^3.0.4, Tailwind CSS ^4.2.1, `@tailwindcss/vite` ^4.2.1, class-variance-authority ^0.7.1, clsx ^2.1.1, and tailwind-merge ^3.6.0.
- Build and type checking: Vite ^7.3.1, TypeScript ~5.9.3, vue-tsc ^3.2.5, `@vitejs/plugin-vue` ^6.0.4, `@tsconfig/node24` ^24.0.4, `@types/node` ^24.11.0, and `@vue/tsconfig` ^0.8.1.
- Linting and formatting: ESLint ^10.0.2, Oxlint ~1.50.0, Prettier 3.8.1, and their Vue, TypeScript, Prettier, and Oxlint ESLint integrations.
- Development tooling: vite-plugin-vue-devtools ^8.0.6, npm-run-all2 ^8.0.4, and jiti ^2.6.1.

**Database:** PostgreSQL via `psycopg[binary]`.

## Commands

- `python -m venv backend/.venv` - create the backend virtual environment.
- `backend/.venv/bin/python -m pip install -r backend/requirements.txt` - install backend dependencies.
- `backend/.venv/bin/python -m uvicorn backend.app.main:app --reload` - run the backend development server from the repository root.
- `backend/.venv/bin/python -m pytest backend/tests` - run the backend test suite.
- `backend/.venv/bin/python -m pytest --cov=backend backend/tests` - run backend tests with coverage.
- `backend/.venv/bin/python -m alembic upgrade head` - apply all database migrations from the repository root.
- `backend/.venv/bin/python -m alembic revision --autogenerate -m "description"` - generate a database migration after model changes.
- `npm ci` - install frontend dependencies from `frontend/`.
- `npm run dev` - run the frontend development server from `frontend/`.
- `npm run build` - type-check and build the frontend from `frontend/`.
- `npm run type-check` - run the frontend TypeScript and Vue type checks from `frontend/`.
- `npm run lint` - run Oxlint and ESLint with automatic fixes from `frontend/`.
- `npm run format` - format frontend source files from `frontend/`.
- `npm run preview` - preview the production frontend build from `frontend/`.

## Progressive Disclosure

- Start with [docs/onboarding.md](docs/onboarding.md) for onboarding and documentation navigation.
- Start with [README.md](README.md) for the project overview and bootstrap requirement.
- Read [PRD.md](PRD.md) for product scope, workflows, roles, and expected behavior.
- Follow [.opencode/docs/CONVENTIONS.md](.opencode/docs/CONVENTIONS.md) when editing source code.
