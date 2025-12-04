# Project Context: La Matatena - BGG Deck Generator

## 1. Executive Summary
**Project Name:** La Matatena
**Objective:** Build a Flask web application that allows users to log in, fetch their board game collection from BoardGameGeek (BGG), and generate a high-quality, printable PDF deck of cards representing their games.
**Core Constraint:** The system must use **WeasyPrint** for PDF generation (not Playwright/Selenium) and **Tailwind CSS** (via CLI) for styling to ensure low resource usage.

### Technical Stack
*   **Backend:** Python 3.11+, Flask.
*   **Database:** SQLAlchemy (SQLite for dev, Postgres for prod).
*   **Auth:** Flask-Login + Werkzeug Security (Local Email/Password).
*   **Styles:** TailwindCSS (Standalone CLI).
*   **PDF Engine:** WeasyPrint (Requires server-side rendering of CSS).
*   **External API:** BGG XML API2.

## 2. Directory Structure (Strict Enforcement)
```
bgg-deck-flask/
├── app/
│   ├── __init__.py          # App factory pattern
│   ├── models.py            # User Model
│   ├── auth.py              # Auth routes & logic
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py          # UI Routes
│   │   └── api.py           # HTMX/Fetch endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bgg.py           # XML Parsing & Fetching
│   │   └── pdf.py           # WeasyPrint Logic
│   ├── static/
│   │   ├── src/
│   │   │   └── input.css    # Input CSS
│   │   ├── dist/            # Compiled CSS (Target for WeasyPrint)
│   │   │   └── output.css
│   │   └── images/
│   ├── templates/
│   │   ├── layouts/
│   │   │   ├── base.html
│   │   │   └── pdf.html     # PDF-specific layout (no navbar)
│   │   ├── components/
│   │   │   └── card.html    # Jinja2 Macro for the card
│   │   ├── index.html
│   │   ├── login.html       # Login page
│   │   └── register.html    # Registration page
├── config.py
├── run.py
├── requirements.txt
└── tailwind.config.js
```

## 3. Implementation Phases

### Phase 1: Scaffolding & Configuration
*   Initialize Flask App Factory.
*   Setup `config.py`.
*   Setup `tailwind.config.js` and Tailwind CLI watcher.

### Phase 2: Database & Authentication (Local)
*   **User Model:** Inherit from `flask_login.UserMixin`. Fields: `id`, `email`, `name`, `password_hash`.
*   **Auth:** Implement `LoginManager`, `register`, `login`, `logout` routes.

### Phase 3: The BGG Service (Data Layer)
*   **fetch_collection(username):** Handle HTTP 202 (Queued) responses.
*   **fetch_game_details(ids):** Chunk requests (max ~20 IDs).
*   **Parsing:** Use `xmltodict` with robust error handling.

### Phase 4: Frontend & Card Design
*   **Card Macro:** Strict dimensions (63.5mm x 88.9mm).
*   **Collection View:** Grid display.
*   **Styling:** Verify Tailwind classes.

### Phase 5: PDF Generation (The Critical Path)
*   **Layout:** `pdf.html` (no navbar, white background).
*   **Service:** Use `weasyprint.HTML(string=html).write_pdf(stylesheets=[CSS(filename=...)])`.
*   **Base URL:** Ensure local images resolve correctly.

## 4. Branching Strategy
This project follows a **Feature Branch Workflow**.

### Branches
*   **`main`**: The source of truth. Contains production-ready code. Direct commits are discouraged.
*   **`feature/*`**: Developing new features (e.g., `feature/user-auth`, `feature/pdf-export`). Branch off `main`, merge back via PR.
*   **`bugfix/*`**: Fixing bugs. Branch off `main`.
*   **`hotfix/*`**: Critical fixes for production.

### Workflow
1.  **Start**: `git checkout -b feature/my-new-feature`
2.  **Work**: Make changes and commit frequently.
3.  **Verify**: Run tests.
4.  **Merge**: `git checkout main` -> `git merge feature/my-new-feature`
5.  **Cleanup**: `git branch -d feature/my-new-feature`
