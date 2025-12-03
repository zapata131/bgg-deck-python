# Project Context

## Overview
"La Matatena" is a BGG Card Deck Generator. It fetches board game data from BoardGameGeek (BGG) and generates printable cards.

## Architecture
- **Backend**: Flask (Python)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Authentication**: Google OAuth (Authlib + Flask-Login)
- **PDF Generation**: Playwright (Python)
- **Frontend**: Jinja2 Templates + TailwindCSS

## Key Decisions
- **Flask**: Chosen for simplicity and flexibility.
- **Playwright**: Used for high-fidelity PDF generation from HTML/CSS.
- **TailwindCSS**: Used for styling to match the "La Matatena" brand.
- **BGG API**: XMLAPI2 used for fetching collection and game details.
- **Scraping**: Fallback scraping used for game descriptions as they are not always available or optimal in the API.

## Directory Structure
See `README.md` or `FLASK_INSTRUCTIONS.md` for the detailed directory structure.

## Branching Strategy
We follow a **Feature Branch Workflow**:
-   **`main`**: Production-ready code. No direct commits.
-   **`feature/*`**: New features. Merge to `main` via PR/Merge.
-   **`bugfix/*`**: Bug fixes. Merge to `main`.
-   **`hotfix/*`**: Critical production fixes.
See `BRANCHING_STRATEGY.md` for details.
