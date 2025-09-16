from flask import Flask, request, jsonify
import ollama

app = Flask(__name__)
model_name = "codegemma"

ollama.pull(model_name)
VALID_TOKEN = "@#$#234RAIN##SHINE$$INTHE$$CLUB"

def validate_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        return False,jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ")[1]

    if token != VALID_TOKEN:
        return False,jsonify({"error": "Invalid token"}), 403

    return True,None, None

@app.route('/generate', methods=['POST'])
def generate_text():
    is_valid, error_response, status = validate_token()

    if not is_valid:
        return error_response,status
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    return jsonify({'text': response['message']['content']})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5000)