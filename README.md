# La Matatena - BGG Card Deck Generator

A web application to generate printable cards from a BoardGameGeek (BGG) collection.

## Tech Stack

*   **Backend**: Flask (Python)
*   **Database**: SQLite (Dev) / PostgreSQL (Prod) + SQLAlchemy
*   **PDF Engine**: Playwright (Python)
*   **Frontend**: Jinja2 Templates + TailwindCSS

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation
1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```
4.  Set up environment variables:
    - Copy `.env.example` to `.env` (or create one)
    - Add your `BGG_API_KEY` (optional, but recommended for better rate limits)

### Running the App
1.  Initialize the database:
    ```bash
    flask db upgrade
    ```
2.  Start the server:
    ```bash
    python run.py
    ```
3.  Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### How to Use
1.  **Enter Username**: On the landing page, enter a BGG username (e.g., `zapata131` or `rahdo`).
2.  **Wait for Processing**: If it's a large collection or the first fetch, you might see a "Processing" screen. Wait for it to complete.
3.  **Browse Collection**: Use the pagination controls to browse games.
4.  **Select Games**: Click cards to select them (or use "Select All").
5.  **Generate PDF**: Click "Download PDF" to get a printable file.

### Stopping the App
- Press `Ctrl + C` in the terminal where the server is running.
