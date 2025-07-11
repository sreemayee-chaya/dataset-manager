from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return 'Flask Backend Running '

@app.route('/upload', methods=['POST'])
def upload():
    try:
        print("=== Upload route hit ===")

        if 'file' not in request.files:
            print(" No file part in request")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        print(f"Received file: {file.filename}")

        if file.filename == '':
            print("Empty filename")
            return jsonify({'error': 'No selected file'}), 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        print(f" Saving file to: {filepath}")

        file.save(filepath)
        print("File saved")

        return jsonify({'message': 'Upload successful'}), 200

    except Exception as e:
        print(" Upload failed:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
