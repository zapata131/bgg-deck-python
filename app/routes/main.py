from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.services.bgg import fetch_collection, fetch_things, scrape_description
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/collection', methods=['POST'])
def collection():
    username = request.form.get('username')
    # 1. Fetch Collection
    data = fetch_collection(username)
    
    if data and data.get('status') == 202:
        flash("BGG is processing the collection. Please try again in a few seconds.", "info")
        return redirect(url_for('main.index'))

    if not data or 'items' not in data or 'item' not in data['items']:
        return "No games found or user does not exist", 404
        
    # 2. Extract IDs (limit to 50)
    # Handle case where 'item' is a single dict or list
    items = data['items']['item']
    if isinstance(items, dict):
        items = [items]
        
    games = items[:50] 
    ids = [g['@objectid'] for g in games]
    
    # 3. Fetch Details
    details = fetch_things(ids)
    
    # 4. Process for Template
    processed_games = []
    if details and 'item' in details['items']:
        from app.services.bgg import process_games_data
        processed_games = process_games_data(details['items']['item'])
        
    return render_template('collection.html', games=processed_games, username=username)

@main_bp.route('/pdf', methods=['POST'])
def download_pdf():
    # Re-use collection logic or accept data. For simplicity, we'll re-fetch or expect IDs.
    # But re-fetching is safer for now to ensure data consistency.
    # Ideally, we should refactor the fetching logic into a reusable function.
    
    username = request.form.get('username')
    if not username:
        return "Username required", 400
        
    # Reuse the logic (copy-paste for now, refactor later if needed)
    data = fetch_collection(username)
    if not data or 'items' not in data or 'item' not in data['items']:
        return "No games found", 404
        
    items = data['items']['item']
    if isinstance(items, dict):
        items = [items]
    
    games = items[:50]
    ids = [g['@objectid'] for g in games]
    details = fetch_things(ids)
    
    processed_games = []
    if details and 'item' in details['items']:
        from app.services.bgg import process_games_data
        processed_games = process_games_data(details['items']['item'])

    # Render template to string
    # We need to inline CSS for Playwright to see it easily without a running server context
    import os
    from flask import current_app
    
    css_path = os.path.join(current_app.root_path, 'static', 'style.css')
    with open(css_path, 'r') as f:
        css_content = f.read()
        
    html_content = render_template('collection.html', games=processed_games, username=username, inline_css=css_content)
    
    from app.services.pdf import generate_pdf
    from flask import make_response
    
    pdf_bytes = generate_pdf(html_content)
    
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=bgg_deck_{username}.pdf'
    
    return response
