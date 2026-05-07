# -*- coding: utf-8 -*-
# ==================================================
# ==================== META DATA ===================
# ==================================================
__author__ = "Daxeel Soni"
__url__ = "https://daxeel.github.io"
__email__ = "daxeelsoni44@gmail.com"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daxeel Soni"

# ==================================================
# ================= IMPORT MODULES =================
# ==================================================
from flask import Flask, render_template, request
import json

# Init flask app
app = Flask(__name__)


def normalize_block_payload(payload):
    """
        Return a parsed JSON payload when possible, otherwise keep the original value.
    """
    try:
        string_types = (basestring,)
    except NameError:
        string_types = (str,)

    if isinstance(payload, string_types):
        try:
            return json.loads(payload)
        except (TypeError, ValueError):
            return payload

    return payload


def get_field_value(obj, field):
    """Return nested field value from dict using dot notation, or None."""
    if not isinstance(obj, dict):
        return None
    parts = field.split('.') if field else []
    cur = obj
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def payload_matches(payload, field, value):
    """Return True if payload contains value in given field (case-insensitive, substring)."""
    if payload is None:
        return False
    # support searching in list of dicts
    if isinstance(payload, list):
        for item in payload:
            v = get_field_value(item, field)
            if v is not None and value.lower() in str(v).lower():
                return True
        return False

    if isinstance(payload, dict):
        v = get_field_value(payload, field)
        return v is not None and value.lower() in str(v).lower()

    return False


@app.route('/')
def index():
    return render_template('guide.html')

@app.route('/allblocks')
def mined_blocks():
    """
        Endpoint to list all mined blocks.
    """
    f = open("chain.txt", "r")
    data = json.loads(f.read())
    f.close()

    field = request.args.get('field', '').strip()
    value = request.args.get('value', '').strip()

    search_active = False
    if field and value:
        search_active = True
        filtered = []
        for block in data:
            payload = normalize_block_payload(block.get('data'))
            if payload_matches(payload, field, value):
                filtered.append(block)
        data = filtered

    return render_template('blocks.html', data=data, search_active=search_active, search_field=field, search_value=value)

@app.route('/block/<hash>')
def block(hash):
    """
        Endpoint which shows all the data for given block hash.
    """
    f = open("chain.txt", "r")
    data = json.loads(f.read())
    f.close()
    for eachBlock in data:
        if eachBlock['hash'] == hash:
            payload = normalize_block_payload(eachBlock.get('data'))
            payload_is_mapping = isinstance(payload, dict)
            payload_is_json = payload_is_mapping or isinstance(payload, list)
            payload_pretty = json.dumps(payload, indent=4, sort_keys=True) if payload_is_json else payload
            return render_template('blockdata.html', data=eachBlock, payload=payload, payload_is_mapping=payload_is_mapping, payload_pretty=payload_pretty)

# Run flask app
if __name__ == '__main__':
    app.run(debug=True)
