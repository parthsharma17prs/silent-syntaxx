from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test')
def test():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting minimal Flask app on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
