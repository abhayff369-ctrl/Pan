from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==========================================
# Developer
# ==========================================
DEVELOPER = "Abhay Singh"

# ==========================================
# Access Token
# ==========================================
ACCESS_TOKEN = "eyJraWQiOiJ5eE1hUkU1V0tnMmRZUm1GQUFyZE5CVDNRNzBGaHZVRXI0ZTJiU1hhY2xnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyNGU4NzJhYi1lNGFkLTRkNDYtYTNiOC1hMDA4YzdhYzgxNTgiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGgtMS5hbWF6b25hd3MuY29tXC9hcC1zb3V0aC0xX3pRWVJuTEhrciIsImNsaWVudF9pZCI6IjRrY28zMWE3YWRhNWRhMTdrZmpidDdqNGg0Iiwib3JpZ2luX2p0aSI6IjcyYzk5YzVkLWQzMDMtNDViMi1iZWYxLTFhMDA1MzU5NDY5OCIsImV2ZW50X2lkIjoiNjUxODQzNjktZGY0Yy00M2E5LTk3NmItM2VkZjcxNWE1MWE3IiwidG9rZW5fdXNlIjoiYWNjZXNzIiwic2NvcGUiOiJhd3MuY29nbml0by5zaWduaW4udXNlci5hZG1pbiIsImF1dGhfdGltZSI6MTc3OTg5MjIzNSwiZXhwIjoxNzc5ODk5NDM1LCJpYXQiOjE3Nzk4OTIyMzUsImp0aSI6IjJlYzc4ZGFiLTRkYzYtNDE5Yi04ZDAwLTkyYmQ1YjM5ODAwNyIsInVzZXJuYW1lIjoibWVyY2hhbnRfb3duZXI6MTI3MTg0MiJ9.EZcu_KrKSetSCgyB4M5DLN0rB662POQGEyh6JAipIBudWTcKsQ3AcG8G2K8i9zUPqfkqMSsEoyIAkNUAnWVBZSpU6yBxwho01nYuaR8XCdg5UZqaVDvIp18rLZxe7bdGpe_Sg9DKcRnd0gQAVJlsyXo_9-FV2rXRegc0-bljapbjWPojqVhE6LNicQEw77DemumxYIZ1hBdcAyjcEgKKxe2IwOjaAm-B1evSUTzWppJDaH4xpx8HuvkICXLt6BFaO2GMre53_OTDn0UMF8EPYLZBS7X4CMIPfKyksv7tlasFpBl-5PnyddKIb0ymKOsqLbTn0QDmYX4AK4iAYcttjg"

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
# PAN Validation
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
            "status_code": response.status_code,
            "response": data
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }

# ==========================================
# Home
# ==========================================
@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "developer": DEVELOPER,
        "message": "PAN Verification API Running",
        "time": datetime.now().isoformat(),
        "endpoints": {
            "POST /verify-pan": {
                "body": {
                    "pan_number": "ABCDE1234F"
                }
            }
        }
    })

# ==========================================
# Verify PAN API
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
# Health
# ==========================================
@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "status": "running",
        "developer": DEVELOPER
    })

# ==========================================
# Vercel
# ==========================================
app = app
