from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==========================================
# Developer Info
# ==========================================
DEVELOPER = "Abhay Singh"

# ==========================================
# Access Token
# ==========================================
ACCESS_TOKEN = "eyJraWQiOiJ5eE1hUkU1V0tnMmRZUm1GQUFyZE5CVDNRNzBGaHZVRXI0ZTJiU1hhY2xnPSIsImFsZyI6IlJTMjU2In0"

# ==========================================
# Headers
# ==========================================
DEFAULT_HEADERS = {
    "authorization": f"Bearer {ACCESS_TOKEN}",
    "content-type": "application/json",
    "x-device-source": "ANDROID_WEB",
    "device-id": "94398dffe0c4ccdb01c283cabe28a253",
    "source-type": "MERCHANT_DASHBOARD",
    "origin": "https://merchant.cashfree.com",
    "referer": "https://merchant.cashfree.com/onboarding?formType=NEW",
    "user-agent": "Mozilla/5.0",
    "accept": "*/*"
}

# ==========================================
# Validate PAN
# ==========================================
def validate_pan_format(pan_number):

    if not pan_number:
        return False, "PAN number required"

    pan_number = pan_number.upper().strip()

    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'

    if re.match(pattern, pan_number):
        return True, pan_number

    return False, "Invalid PAN format"

# ==========================================
# Verify PAN
# ==========================================
def verify_pan_with_cashfree(pan_number):

    url = "https://merchant.cashfree.com/ob/auto-verify/pan"

    payload = {
        "panNumber": pan_number,
        "storageKey": "companyPan",
        "panType": "companyPan",
        "processPAN": False,
        "sourceType": "Android"
    }

    try:

        response = requests.post(
            url,
            headers=DEFAULT_HEADERS,
            json=payload,
            timeout=30
        )

        try:
            data = response.json()
        except:
            data = response.text

        return {
            "success": True,
            "status_code": response.status_code,
            "data": data
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }

# ==========================================
# Home Route
# ==========================================
@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "developer": DEVELOPER,
        "message": "PAN Verification API Running",
        "time": datetime.now().isoformat(),
        "routes": {
            "GET /search-pan?pan=ABCDE1234F": "Browser Search",
            "POST /verify-pan": "POST API",
            "GET /health": "Health Check"
        }
    })

# ==========================================
# Browser Search Route
# ==========================================
@app.route("/search-pan", methods=["GET"])
def search_pan():

    try:

        pan_number = request.args.get("pan")

        if not pan_number:
            return jsonify({
                "success": False,
                "message": "PAN number required"
            }), 400

        is_valid, result = validate_pan_format(pan_number)

        if not is_valid:
            return jsonify({
                "success": False,
                "message": result
            }), 400

        api_result = verify_pan_with_cashfree(result)

        return jsonify({
            "success": True,
            "developer": DEVELOPER,
            "pan_number": result,
            "result": api_result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# ==========================================
# POST Verify Route
# ==========================================
@app.route("/verify-pan", methods=["POST"])
def verify_pan():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "JSON body required"
            }), 400

        pan_number = (
            data.get("pan_number")
            or data.get("pan")
            or data.get("PAN")
        )

        if not pan_number:
            return jsonify({
                "success": False,
                "message": "PAN number required"
            }), 400

        is_valid, result = validate_pan_format(pan_number)

        if not is_valid:
            return jsonify({
                "success": False,
                "message": result
            }), 400

        api_result = verify_pan_with_cashfree(result)

        return jsonify({
            "success": True,
            "developer": DEVELOPER,
            "pan_number": result,
            "result": api_result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# ==========================================
# Health Route
# ==========================================
@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "status": "running",
        "developer": DEVELOPER
    })

# ==========================================
# Run App
# ==========================================
if __name__ == "__main__":

    print("=" * 60)
    print(" PAN Verification API ")
    print("=" * 60)
    print(" Developer : Abhay Singh ")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )

# ==========================================
# Vercel Export
# ==========================================
app = app
