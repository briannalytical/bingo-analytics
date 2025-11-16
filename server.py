from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)


# initialize db
def init_db():
    conn = sqlite3.connect('bingo_analytics.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS card_appearances
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  card_id TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS card_selections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  card_id TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()


init_db()


@app.route('/api/appearance', methods=['POST'])
def log_appearance():
    data = request.json
    card_ids = data.get('cardIds', [])

    conn = sqlite3.connect('bingo_analytics.db')
    c = conn.cursor()

    for card_id in card_ids:
        c.execute('INSERT INTO card_appearances (card_id) VALUES (?)', (card_id,))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/selection', methods=['POST'])
def log_selection():
    data = request.json
    card_id = data.get('cardId')

    conn = sqlite3.connect('bingo_analytics.db')
    c = conn.cursor()
    c.execute('INSERT INTO card_selections (card_id) VALUES (?)', (card_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect('bingo_analytics.db')
    c = conn.cursor()

    # get appearance counts
    c.execute('''SELECT card_id, COUNT(*) as count 
                 FROM card_appearances 
                 GROUP BY card_id''')
    appearances = {row[0]: row[1] for row in c.fetchall()}

    # get selected counts
    c.execute('''SELECT card_id, COUNT(*) as count 
                 FROM card_selections 
                 GROUP BY card_id''')
    selections = {row[0]: row[1] for row in c.fetchall()}

    conn.close()

    # calculate stats/analytics
    stats = []
    for card_id in appearances:
        app_count = appearances.get(card_id, 0)
        sel_count = selections.get(card_id, 0)
        stats.append({
            'cardId': card_id,
            'appearances': app_count,
            'selections': sel_count,
            'clickThroughRate': sel_count / app_count if app_count > 0 else 0
        })

    return jsonify(stats)


if __name__ == '__main__':
    app.run(port=3000, debug=True)