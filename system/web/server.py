from flask import Flask, request, jsonify, send_from_directory
import threading
import time

import json
import os

app = Flask(__name__, static_folder='debug_frontend')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MC_MAX_BODY_BYTES', '262144'))

DATA_FILE = 'map_data.json'
API_TOKEN = os.getenv('MC_API_TOKEN')
MAX_MAP_ENTRIES = int(os.getenv('MC_MAX_MAP_ENTRIES', '50000'))
MAX_PLAYERS = int(os.getenv('MC_MAX_PLAYERS', '200'))

# Load or Init world state
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return { "map": {}, "players": {}, "version": 0, "changed": False }

world_state = load_data()


def is_authorized(req):
    if not API_TOKEN:
        return False
    return req.headers.get('X-API-Token') == API_TOKEN


def reject_unauthorized():
    return jsonify({'error': 'unauthorized'}), 401

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(world_state, f)

@app.route('/')
def index():
    return send_from_directory('debug_frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('debug_frontend', path)

@app.route('/v1/mc/update', methods=['POST'])
def update_map():
    global world_state
    if not is_authorized(request):
        return reject_unauthorized()

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'invalid json body'}), 400

    # Merge map data
    if 'map' in data:
        if not isinstance(data['map'], dict):
            return jsonify({'error': 'map must be an object'}), 400
        if len(data['map']) > MAX_MAP_ENTRIES:
            return jsonify({'error': 'map payload too large'}), 413
        if len(world_state['map']) + len(data['map']) > MAX_MAP_ENTRIES:
            return jsonify({'error': 'map state limit exceeded'}), 413
        world_state['map'].update(data['map'])
        world_state['changed'] = True
        world_state['version'] += 1
        save_data() # Auto-save
    if 'players' in data:
        if not isinstance(data['players'], dict):
            return jsonify({'error': 'players must be an object'}), 400
        if len(data['players']) > MAX_PLAYERS:
            return jsonify({'error': 'players payload too large'}), 413
        world_state['players'] = data['players']
        # save_data() # Optional for players
    return jsonify({"status": "ok"})

@app.route('/v1/mc/map')
def get_map():
    if not is_authorized(request):
        return reject_unauthorized()

    version = request.args.get('since', -1, type=int)
    if version < world_state['version']:
        return jsonify(world_state)
    else:
        return jsonify({"changed": False, "version": world_state['version']})

@app.route('/v1/system/logs')
def get_logs():
    return jsonify({"logs": [], "cursor": 0})

if __name__ == '__main__':
    print("Starting Web Server on 8082...")
    app.run(port=8082)
