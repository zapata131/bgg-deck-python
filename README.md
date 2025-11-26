# La Matatena - BGG Card Deck Generator

A web application to generate printable cards from a BoardGameGeek (BGG) collection.

## Tech Stack

*   **Backend**: Flask (Python)
*   **Database**: PostgreSQL + SQLAlchemy
*   **Auth**: Google OAuth (Authlib + Flask-Login)
*   **PDF Engine**: Playwright (Python)
*   **Frontend**: Jinja2 Templates + TailwindCSS

## Setup

1.  Clone the repository.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Set up environment variables in `.env`.
4.  Run migrations: `flask db upgrade`
5.  Run the application: `python run.py`
