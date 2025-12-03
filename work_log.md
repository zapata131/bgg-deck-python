# Work Log

## [2025-11-25] Project Initialization

- Created project structure based on `FLASK_INSTRUCTIONS.md`.
- Initialized `README.md`, `tasks.md`, and `context.md`.
- Setting up Flask application skeleton.
- Implemented backend core (config, app factory, models, auth).
- Implemented services (BGG, PDF).
- Implemented frontend (templates, styles).
- Implemented routes (main, auth).
- Verified application runs successfully with SQLite.
- Fixed BGG API authentication issue by adding API key.
- Implemented print styling (gutters, cut markers, squared corners).
- Enhanced card details (added artists, increased image size).
- Implemented PDF download feature and increased game limit to 50.
- Added automated testing infrastructure with `pytest`.
- Fixed "blank page" issue by correctly handling BGG API 202 Accepted responses.
- Debugged collection fetch timeout: Reduced game limit from 50 to 12 to prevent timeouts caused by sequential scraping of game descriptions.
- Implemented **Parallel Processing**: Used `concurrent.futures` to scrape game descriptions in parallel, reducing fetch time for 50 games from ~50s to ~4.5s.
- Implemented **Database Caching**: Added `Game` model and updated `app/services/bgg.py` to cache game details. Subsequent fetches for the same games are now near-instant (~0.01s processing time).
- Fixed BGG API limit issue by chunking `/thing` requests into batches of 20.

## [2025-12-03] UI/UX & Collection Tracking

- **Removed Google OAuth**: Simplified the application by removing user authentication. It is now open for any BGG user.
- **UI/UX Improvements**:
    - Redesigned Landing Page with a modern Hero section.
    - Enhanced Collection View with a grid layout, "Select All" functionality, and a card detail modal.
    - Added loading states to buttons.
- **Collection Tracking Reliability**:
    - Implemented **Pagination** (24 games per page) to handle large collections efficiently.
    - Added a **Processing Page** (`processing.html`) to gracefully handle BGG's 202 Accepted status with auto-retry.
    - Verified fetching for large collections (e.g., user `zapata131`).
- **Documentation**: Updated `README.md` with detailed Run/Stop instructions.
- **Verification**: Added unit tests for pagination and route logic. All tests passed.
