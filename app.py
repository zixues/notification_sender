import csv
import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from twilio.rest import Client
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

@app.route('/send-notifications', methods=['POST'])
def send_messages():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    results = []

    try:
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                content_vars = {str(i+1): value for i, value in enumerate(row.values())}
                print("sending to:", row.get('name', 'Unknown'), "| Content Vars:", content_vars)

                message = client.messages.create(
                    from_='whatsapp:+14155238886',
                    content_sid='HXd3fa494fbc6d86a3adf105dcec12ea3e',  
                    content_variables=json.dumps(content_vars),
                    to='whatsapp:+919380651814'  
                )

                results.append({
                    "name": row.get('name', 'Unknown'),
                    "message_sid": message.sid
                })

        return jsonify({"status": "success", "message": results}), 200
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
