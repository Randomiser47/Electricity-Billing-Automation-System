# app.py
from quart import Quart, render_template, request, jsonify, send_file
import os
from scraper import AsyncPITCSession
import hypercorn.asyncio
from hypercorn.config import Config

app = Quart(__name__)
app.secret_key = "final_async_2025"
os.makedirs("bills", exist_ok=True)

active_sessions = {}

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/search', methods=['POST'])
async def search():
    data = await request.get_json()
    no = data.get('contact_no', '').strip()
    if len(no) < 10:
        return jsonify({"error": "Invalid number"}), 400

    session = AsyncPITCSession()
    try:
        await session.start(no)
        sid = str(id(session))
        active_sessions[sid] = session
        return jsonify({"session_id": sid, "accounts": session.accounts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/select_account', methods=['POST'])
async def select():
    data = await request.get_json()
    sid = data.get('session_id')
    val = data.get('account_value')
    session = active_sessions.get(sid)
    if not session:
        return jsonify({"error": "Session expired"}), 400
    try:
        result = await session.select_account(val)
        result["session_id"] = sid

        # Generate graph
        graph_url = generate_billing_graph(result["billing_data"])
        result["billing_graph"] = graph_url

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500@app.route('/generate_bill', methods=['POST'])

async def gen():
    data = await request.get_json()
    sid = data.get('session_id')
    session = active_sessions.pop(sid, None)
    if not session:
        return jsonify({"error": "Session expired"}), 400
    ref_no = data.get('reference_no')
    return jsonify(await session.generate_bill(ref_no))

@app.route('/download/<filename>')
async def download(filename):
    path = os.path.join("bills", filename)
    if os.path.exists(path):
        return await send_file(path, as_attachment=True)
    return "Not found", 404

if __name__ == '__main__':
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    hypercorn.asyncio.serve(app, config)  # FIXED: Use .serve() instead of .run()
