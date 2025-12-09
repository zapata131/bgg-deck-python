import requests
import xmltodict
from bs4 import BeautifulSoup
from functools import lru_cache

import os
from dotenv import load_dotenv

load_dotenv()

BGG_API_BASE = "https://boardgamegeek.com/xmlapi2"
# CRITICAL: BGG blocks requests without a custom User-Agent
HEADERS = {
    "User-Agent": "LaMatatena/1.0 (contact@example.com)",
    "Authorization": f"Bearer {os.environ.get('BGG_API_KEY')}"
}

def fetch_collection(username):
    """Fetches owned games for a user."""
    url = f"{BGG_API_BASE}/collection"
        "username": username,
        "own": 1,
        "stats": 1,
        "excludesubtype": "boardgameexpansion"
    # print(f"DEBUG: Fetching collection for {username} from {url}")
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        # print(f"DEBUG: Response Status: {response.status_code}")
        
        if response.status_code == 202:
            # print("DEBUG: BGG returned 202 Accepted (Processing)")
            return {"status": 202, "message": "Queued. Please try again."}
        
        if response.status_code == 200:
            # force_list ensures 'item' is always a list, even if only 1 game exists
            data = xmltodict.parse(
                response.content, 
                force_list=('item', 'link', 'name', 'poll', 'result')
            )
            return data
        
        # print(f"DEBUG: Error {response.status_code}: {response.text}")
        return None
    except Exception as e:
        print(f"Error fetching collection: {e}")
        return None

def fetch_things(ids):
    """Fetches detailed stats for a list of game IDs."""
    # Chunk IDs into batches of 20 (BGG limit)
    chunk_size = 20
    all_items = []
    
    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i + chunk_size]
        id_str = ",".join(map(str, chunk))
        url = f"{BGG_API_BASE}/thing"
        params = {"id": id_str, "stats": 1}
        
        try:
            response = requests.get(url, params=params, headers=HEADERS)
            if response.status_code == 200:
                data = xmltodict.parse(
                    response.content,
                    force_list=('item', 'link', 'name', 'poll', 'result')
                )
                if data and 'items' in data and 'item' in data['items']:
                    items = data['items']['item']
                    if isinstance(items, dict):
                        items = [items]
                    all_items.extend(items)
            else:
                print(f"DEBUG: fetch_things chunk failed with status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error fetching chunk: {e}")
            
    if all_items:
        return {'items': {'item': all_items}}
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

import concurrent.futures
import json
from app import db
from app.models import Game

def process_games_data(items):
    """
    Processes a list of BGG game items (from fetch_things) into a list of game dictionaries.
    Checks DB for existing games, fetches missing descriptions in parallel, and saves new games.
    """
    if not items:
        return []

    if isinstance(items, dict):
        items = [items]

    # 1. Identify IDs
    # items contains the raw XML data from BGG
    item_map = {item['@id']: item for item in items}
    all_ids = list(item_map.keys())
    
    # 2. Check DB for existing games
    existing_games_db = Game.query.filter(Game.bgg_id.in_(all_ids)).all()
    existing_ids = {str(g.bgg_id) for g in existing_games_db}
    
    # 3. Filter for missing games
    missing_ids = [gid for gid in all_ids if gid not in existing_ids]
    missing_items = [item_map[gid] for gid in missing_ids]
    
    processed_games = []
    
    # Convert DB models to dicts
    for g in existing_games_db:
        processed_games.append({
            'id': str(g.bgg_id),
            'name': g.name,
            'image': g.image,
            'thumbnail': g.thumbnail,
            'description': g.description,
            'yearpublished': g.year_published,
            'minplayers': g.min_players,
            'maxplayers': g.max_players,
            'playingtime': g.playing_time,
            'averageweight': str(g.average_weight) if g.average_weight else None,
            'designers': json.loads(g.designers) if g.designers else [],
            'artists': json.loads(g.artists) if g.artists else []
        })

    if not missing_items:
        return processed_games

    # 4. Process missing games
    # Helper to safely get value from XML dict
    def get_val(obj, key, default=None):
        return obj.get(key, {}).get('@value', default)

    # Pre-process basic data
    temp_games = []
    for item in missing_items:
        game = {
            'id': item['@id'],
            'name': item['name'][0]['@value'] if isinstance(item['name'], list) else item['name']['@value'],
            'image': item.get('image'),
            'thumbnail': item.get('thumbnail'),
            'yearpublished': get_val(item, 'yearpublished'),
            'minplayers': get_val(item, 'minplayers'),
            'maxplayers': get_val(item, 'maxplayers'),
            'playingtime': get_val(item, 'playingtime'),
            'averageweight': item.get('statistics', {}).get('ratings', {}).get('averageweight', {}).get('@value'),
            'designers': [],
            'artists': []
        }
        
        # Extract designers and artists
        links = item.get('link', [])
        if isinstance(links, dict):
            links = [links]
        for link in links:
            if link.get('@type') == 'boardgamedesigner':
                game['designers'].append(link.get('@value'))
            elif link.get('@type') == 'boardgameartist':
                game['artists'].append(link.get('@value'))
        
        temp_games.append(game)

    # Fetch descriptions in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Create a map of future -> game
        future_to_game = {executor.submit(scrape_description, game['id']): game for game in temp_games}
        
        for future in concurrent.futures.as_completed(future_to_game):
            game = future_to_game[future]
            try:
                game['description'] = future.result()
            except Exception as exc:
                print(f"Description fetch generated an exception for {game['name']}: {exc}")
                game['description'] = None
            
            # Save to DB
            try:
                new_game = Game(
                    bgg_id=int(game['id']),
                    name=game['name'],
                    image=game['image'],
                    thumbnail=game['thumbnail'],
                    description=game['description'],
                    year_published=game['yearpublished'],
                    min_players=game['minplayers'],
                    max_players=game['maxplayers'],
                    playing_time=game['playingtime'],
                    average_weight=float(game['averageweight']) if game['averageweight'] else 0.0,
                    designers=json.dumps(game['designers']),
                    artists=json.dumps(game['artists'])
                )
                db.session.add(new_game)
                processed_games.append(game)
            except Exception as e:
                print(f"Error saving game {game['name']} to DB: {e}")

    # Commit all new games
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error committing games to DB: {e}")
    
    return processed_games
