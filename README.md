# La Matatena - BGG Card Deck Generator

A web application to generate printable cards from a BoardGameGeek (BGG)
collection.

## Tech Stack

*   **Backend**: Flask (Python)
*   **Database**: SQLite (Dev) / PostgreSQL (Prod) + SQLAlchemy
*   **Auth**: Flask-Login + Werkzeug Security (Local Email/Password)
*   **PDF Engine**: WeasyPrint (Python)
*   **Frontend**: Jinja2 Templates + TailwindCSS (Standalone CLI)

## Quick Start

### Prerequisites
- Python 3.11+
- pip
- npm (for Tailwind CSS)

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
    npm install
    ```
4.  Build Tailwind CSS:
    ```bash
    npm run build
    ```
5.  Set up environment variables:
    - Copy `.env.example` to `.env` (or create one)
    - Add your `BGG_API_KEY` (optional, but recommended for better rate limits)

### Running the App
1.  Initialize the database:
    ```bash
    flask db upgrade
    ```
    *Or in dev shell:* `db.create_all()`
2.  Start the server:
    ```bash
    flask run
    ```
3.  Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Running with Docker (Optional)
1.  Build and start the container:
    ```bash
    docker-compose up --build
    ```
2.  Open your browser and navigate to: [http://localhost:5000](http://localhost:5000)


### How to Use
1.  **Register/Login**: Create an account to save your data.
2.  **Enter Username**: On the collection page, enter a BGG username (e.g.,
    `zapata131`).
3.  **Wait for Processing**: If it's a large collection or the first fetch, you
    might see a "Processing" status.
4.  **Browse Collection**: Use the pagination controls to browse games.
5.  **Select Games**: Click cards to select them (or use "Select All").
6.  **Generate PDF**: Click "Download PDF" to get a printable file.

### Stopping the App
- Press `Ctrl + C` in the terminal where the server is running.
