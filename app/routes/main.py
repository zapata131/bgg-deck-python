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

@main_bp.route('/collection', methods=['GET', 'POST'])
def collection():
    if request.method == 'POST':
        username = request.form.get('username')
    else:
        username = request.args.get('username')

    if not username:
        return redirect(url_for('main.index'))

    # 1. Fetch Collection
    data = fetch_collection(username)
    
    if data and data.get('status') == 202:
        return render_template('processing.html', username=username)

    if not data or 'items' not in data or 'item' not in data['items']:
        flash(f"No games found for user '{username}' or user does not exist.", "error")
        return redirect(url_for('main.index'))
        
    # 2. Extract IDs
    items = data['items']['item']
    if isinstance(items, dict):
        items = [items]
        
    # Pagination Logic
    page = request.args.get('page', 1, type=int)
    per_page = 24 # 4x6 grid
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    
    current_items = items[start:end]
    ids = [g['@objectid'] for g in current_items]
    
    # 3. Fetch Details
    details = fetch_things(ids)
    
    # 4. Process for Template
    processed_games = []
    if details and 'items' in details and 'item' in details['items']:
        from app.services.bgg import process_games_data
        processed_games = process_games_data(details['items']['item'])
        
    return render_template('collection.html', 
                           games=processed_games, 
                           username=username,
                           page=page,
                           total_pages=total_pages,
                           total_items=total_items)

@main_bp.route('/pdf', methods=['POST'])
@main_bp.route('/pdf', methods=['POST'])
def download_pdf():
    username = request.form.get('username')
    selected_ids_str = request.form.get('selected_ids')
    download_all = request.form.get('download_all') == 'true'
    
    if not username:
        return "Username required", 400
        
    ids = []
    if not download_all and selected_ids_str:
        import json
        try:
            ids = json.loads(selected_ids_str)
        except:
            pass
            
    if download_all or not ids:
        # Fetch full collection if download_all is requested or as fallback
        data = fetch_collection(username)
        if not data or 'items' not in data or 'item' not in data['items']:
            return "No games found", 404
        items = data['items']['item']
        if isinstance(items, dict):
            items = [items]
            
        # If specific IDs were requested (and valid), use them. 
        # Otherwise (download_all or fallback), use all IDs.
        if not ids: 
             ids = [g['@objectid'] for g in items]

    # Fetch details for selected IDs
    details = fetch_things(ids)
    
    processed_games = []
    if details and 'items' in details and 'item' in details['items']:
        from app.services.bgg import process_games_data
        processed_games = process_games_data(details['items']['item'])

    # Render template to string
    import os
    from flask import current_app
    
    css_path = os.path.join(current_app.root_path, 'static', 'style.css')
    with open(css_path, 'r') as f:
        css_content = f.read()
        
    # Pass dummy pagination values as they are not needed for PDF (and hidden via CSS)
    html_content = render_template('collection.html', 
                                   games=processed_games, 
                                   username=username, 
                                   inline_css=css_content,
                                   page=1,
                                   total_pages=1,
                                   total_items=len(processed_games))
    
    from app.services.pdf import generate_pdf
    from flask import make_response
    
    pdf_bytes = generate_pdf(html_content)
    
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=bgg_deck_{username}.pdf'
    
    return response
