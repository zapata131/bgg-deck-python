# Flask Implementation Guide: La Matatena - BGG Card Deck Generator

This document is a **complete, self-contained guide** to building the "La Matatena" BGG Card Deck Generator using **Flask**. It contains all necessary code snippets, design specifications, and logic to build the application from scratch without referencing any other files.

## 1. Project Overview & Stack

We are building a web application to generate printable cards from a BoardGameGeek (BGG) collection.

*   **Backend**: Flask (Python)
*   **Database**: PostgreSQL + SQLAlchemy
*   **Auth**: Google OAuth (Authlib + Flask-Login)
*   **PDF Engine**: Playwright (Python)
*   **Frontend**: Jinja2 Templates + TailwindCSS (via CDN or local build)

## 2. Project Setup

### Directory Structure
```
bgg-deck-flask/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # Database models
│   ├── auth.py              # Authentication logic
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py          # UI routes
│   │   ├── api.py           # API routes
│   ├── services/
│   │   ├── bgg.py           # BGG API & Scraper
│   │   └── pdf.py           # PDF generation
│   ├── static/
│   │   ├── style.css        # Custom styles
│   ├── templates/
│   │   ├── base.html        # Base layout
│   │   ├── card_macro.html  # Card component macro
│   │   └── index.html       # Main page
├── migrations/              # Alembic migrations
├── config.py                # Config classes
├── run.py                   # Entry point
├── requirements.txt
└── .env
```

### Dependencies (`requirements.txt`)
```text
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
Authlib
requests
xmltodict
beautifulsoup4
playwright
psycopg2-binary
python-dotenv
```

## 3. Database Models

We use a schema compatible with NextAuth to allow for potential future interoperability, but adapted for Flask-Login.

**`app/models.py`**:
```python
from . import db
from flask_login import UserMixin
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    accounts = db.relationship('Account', backref='user', lazy=True)

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String, nullable=False)
    provider_account_id = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String)
    refresh_token = db.Column(db.String)
    expires_at = db.Column(db.Integer)
    
    __table_args__ = (db.UniqueConstraint('provider', 'provider_account_id', name='_provider_unique'),)
```

## 4. BGG Integration (The "Brain")

This section contains **all** the logic needed to fetch and parse data from BGG.

**`app/services/bgg.py`**:
```python
import requests
import xmltodict
from bs4 import BeautifulSoup
from functools import lru_cache

BGG_API_BASE = "https://boardgamegeek.com/xmlapi2"
# CRITICAL: BGG blocks requests without a custom User-Agent
HEADERS = {
    "User-Agent": "LaMatatena/1.0 (contact@example.com)" 
}

def fetch_collection(username):
    """Fetches owned games for a user."""
    url = f"{BGG_API_BASE}/collection"
    params = {
        "username": username,
        "own": 1,
        "excludesubtype": "boardgameexpansion"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    
    if response.status_code == 202:
        return {"status": 202, "message": "Queued. Please try again."}
    
    if response.status_code == 200:
        # force_list ensures 'item' is always a list, even if only 1 game exists
        return xmltodict.parse(
            response.content, 
            force_list=('item', 'link', 'name', 'poll', 'result')
        )
    return None

def fetch_things(ids):
    """Fetches detailed stats for a list of game IDs."""
    id_str = ",".join(map(str, ids))
    url = f"{BGG_API_BASE}/thing"
    params = {"id": id_str, "stats": 1}
    
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return xmltodict.parse(
            response.content,
            force_list=('item', 'link', 'name', 'poll', 'result')
        )
    return None

@lru_cache(maxsize=500)
def scrape_description(bgg_id):
    """Scrapes the short meta description from the BGG website."""
    url = f"https://boardgamegeek.com/boardgame/{bgg_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code != 200:
            return None
            
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Priority 1: Standard meta description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
            
        # Priority 2: OpenGraph description
        meta = soup.find('meta', attrs={'property': 'og:description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
            
        return None
    except Exception as e:
        print(f"Error scraping {bgg_id}: {e}")
        return None
```

## 5. Frontend & Styling (The "Look")

We use **TailwindCSS** for styling. You can use the CDN for simplicity in development.

### 5.1 CSS Variables & Custom Styles
Add this to `app/static/style.css`. These colors define the "La Matatena" brand.

```css
:root {
  --background: #F5F0E9;
  --foreground: #3A3A3A;
  --card: #FFFFFF;
  --primary: #8367C7; /* Purple */
  --primary-foreground: #FFFFFF;
  --muted: #F5F0E9;
  --muted-foreground: #6B6B6B;
  --radius: 0.625rem;
}

/* Poker Card Dimensions: 63.5mm x 88.9mm */
.card-container {
  width: 63.5mm;
  height: 88.9mm;
  border-radius: 3mm;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--card);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Print Overrides */
@media print {
  @page { margin: 0; }
  body { background: white; }
  .no-print { display: none; }
}
```

### 5.2 Card Template (Jinja2 Macro)
This macro reproduces the exact design of the React component. Save as `app/templates/card_macro.html`.

```html
{% macro render_card(game) %}
<div class="card-container font-sans text-[#3A3A3A]">
    <!-- Top Half: Image -->
    <div class="h-[55%] w-full relative bg-[#F5F0E9] overflow-hidden">
        {% if game.image %}
            <img src="{{ game.image }}" alt="{{ game.name }}" class="w-full h-full object-cover">
        {% else %}
            <div class="w-full h-full flex items-center justify-center text-gray-500 text-xs">No Image</div>
        {% endif %}

        <!-- Gradient Overlay -->
        <div class="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-black/80 to-transparent"></div>

        <!-- Title & Year -->
        <div class="absolute bottom-2 left-3 right-3 text-white">
            <h2 class="font-bold text-lg leading-tight line-clamp-2 drop-shadow-md">{{ game.name }}</h2>
            {% if game.yearpublished %}
                <p class="text-xs opacity-90 font-medium drop-shadow-sm">{{ game.yearpublished }}</p>
            {% endif %}
        </div>
    </div>

    <!-- Stats Bar -->
    <div class="h-[12%] bg-[#8367C7] text-white flex items-center justify-between px-4 text-xs font-bold shadow-sm z-10">
        <!-- Players -->
        <div class="flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-80"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            <span>
                {% if game.minplayers == game.maxplayers %}
                    {{ game.minplayers }}
                {% else %}
                    {{ game.minplayers }}-{{ game.maxplayers }}
                {% endif %}
            </span>
        </div>
        <!-- Time -->
        <div class="flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-80"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span>{{ game.playingtime }}m</span>
        </div>
        <!-- Weight -->
        <div class="flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-80"><path d="m6.5 6.5 11 11"/><path d="m21 21-1-1"/><path d="m3 3 1 1"/><path d="m18 22 4-4"/><path d="m2 6 4-4"/><path d="m3 10 7-7"/><path d="m14 21 7-7"/></svg>
            <span>{{ "%.1f"|format(game.averageweight|default(0)) }}</span>
        </div>
    </div>

    <!-- Bottom Half: Description -->
    <div class="flex-1 p-3 flex flex-col gap-2 bg-[#F5F0E9]">
        <p class="text-[10px] leading-snug line-clamp-6 flex-1 opacity-90 text-justify">
            {{ game.description | default("No description available.") }}
        </p>
        
        <!-- Credits -->
        <div class="mt-auto pt-2 border-t border-black/10 flex flex-col gap-0.5 text-[9px] opacity-70">
            {% if game.designers %}
            <div class="flex gap-1 truncate">
                <span class="font-bold">Design:</span>
                <span class="truncate">{{ game.designers|join(", ") }}</span>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endmacro %}
```

## 6. PDF Generation

We use **Playwright** to render the HTML to PDF.

**`app/services/pdf.py`**:
```python
from playwright.sync_api import sync_playwright

def generate_pdf(html_content):
    """
    Renders HTML content to a PDF using a headless browser.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Set content
        page.set_content(html_content)
        
        # Wait for images to load
        page.wait_for_load_state("networkidle")
        
        # Generate PDF (A4 size)
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
        )
        browser.close()
        return pdf_bytes
```

## 7. Authentication Setup

**`app/auth.py`**:
```python
from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def setup_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'openid email profile'},
    )
```

## 8. Putting It Together (Routes)

**`app/routes/main.py`**:
```python
from flask import Blueprint, render_template, request
from app.services.bgg import fetch_collection, fetch_things, scrape_description

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/collection', methods=['POST'])
def collection():
    username = request.form.get('username')
    # 1. Fetch Collection
    data = fetch_collection(username)
    if not data or 'item' not in data['items']:
        return "No games found", 404
        
    # 2. Extract IDs (limit to 10 for demo)
    games = data['items']['item'][:10] 
    ids = [g['@objectid'] for g in games]
    
    # 3. Fetch Details
    details = fetch_things(ids)
    
    # 4. Process for Template
    processed_games = []
    for item in details['items']['item']:
        # Helper to safely get value from XML dict
        def get_val(obj, key, default=None):
            return obj.get(key, {}).get('@value', default)
            
        game = {
            'name': item['name'][0]['@value'] if isinstance(item['name'], list) else item['name']['@value'],
            'image': item.get('image'),
            'yearpublished': get_val(item, 'yearpublished'),
            'minplayers': get_val(item, 'minplayers'),
            'maxplayers': get_val(item, 'maxplayers'),
            'playingtime': get_val(item, 'playingtime'),
            'averageweight': item.get('statistics', {}).get('ratings', {}).get('averageweight', {}).get('@value'),
            'description': scrape_description(item['@id']) # Scrape description
        }
        processed_games.append(game)
        
    return render_template('collection.html', games=processed_games)
```
