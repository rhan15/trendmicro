from flask import jsonify

def create_success_response(
    data=None, message="", status=200, statusMsg="success"
):
    response = {
        "status": statusMsg,
        "data": data,
        "message": message,
        "respond_code": status
    }
    return response

def create_error_response(message="", error_message="", status=400, data=""):
    response = {"status": "failed", "message": message, "error_message": error_message, "data": data, "respond_code": status}
    return jsonify(response)