from flask import Flask, request, jsonify, send_from_directory
import threading
import time

import json
import os

app = Flask(__name__, static_folder='debug_frontend')

DATA_FILE = 'map_data.json'

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
    data = request.json
    # Merge map data
    if 'map' in data:
        world_state['map'].update(data['map'])
        world_state['changed'] = True
        world_state['version'] += 1
        save_data() # Auto-save
    if 'players' in data:
        world_state['players'] = data['players']
        # save_data() # Optional for players
    return jsonify({"status": "ok"})

@app.route('/v1/mc/map')
def get_map():
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
