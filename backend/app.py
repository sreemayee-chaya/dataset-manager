from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import traceback

app = Flask(__name__)
CORS(app)

# Setup upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return 'Flask Backend Running'

@app.route('/call', methods=['GET'])
def get_call():
    print("Call success")
    return jsonify({'message': 'Call received successfully'}), 200

@app.route('/upload', methods=['POST'])
def upload():
    print("=== Upload route hit ===")
    try:
        # Check if 'file' is present
        if 'file' not in request.files:
            print("No file part in request")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        print(f"Received file: {file.filename}")

        # Check file size (limit: 100MB)
        MAX_FILE_SIZE_MB = 100
        file.seek(0, os.SEEK_END)
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)  # Reset pointer to beginning for saving

        if size_mb > MAX_FILE_SIZE_MB:
            print(f"File too large: {size_mb:.2f}MB")
            return jsonify({'error': f'File exceeds max size of {MAX_FILE_SIZE_MB}MB'}), 400

        
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.zip']
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            print(" Unsupported file type:", file_ext)
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        if file.filename == '':
            print("Empty filename")
            return jsonify({'error': 'No selected file'}), 400
        


        # Save the uploaded file
        project_name = request.form.get('name') or 'default'
        # Find the next version number
        project_base_folder = os.path.join(UPLOAD_FOLDER, project_name)
        os.makedirs(project_base_folder, exist_ok=True)

        # Detect existing versions (v1, v2...)
        existing_versions = [d for d in os.listdir(project_base_folder) if d.startswith('v') and os.path.isdir(os.path.join(project_base_folder, d))]
        version_numbers = [int(v[1:]) for v in existing_versions if v[1:].isdigit()]
        next_version = max(version_numbers + [0]) + 1
        version_folder_name = f"v{next_version}"

        # Check for duplicate file in all previous versions
        duplicate_found = False
        for existing_version in existing_versions:
            version_path = os.path.join(project_base_folder, existing_version)
            if os.path.exists(os.path.join(version_path, file.filename)):
                duplicate_found = True
                print(f"Duplicate file '{file.filename}' already exists in version '{existing_version}'")
                break
            if duplicate_found:
                return jsonify({'error': f'A file named "{file.filename}" already exists in a previous version of this project.'}), 409

        # Create versioned folder
        project_folder = os.path.join(project_base_folder, version_folder_name)
        os.makedirs(project_folder, exist_ok=True)


        filepath = os.path.join(project_folder, file.filename)
        print(f"Saving file to: {filepath}")
        file.save(filepath)
        print("File saved successfully")
        
        # Extracting ZIP file
        if file.filename.lower().endswith('.zip'):
            import zipfile
            extract_folder = os.path.splitext(filepath)[0]  # Remove .zip
            os.makedirs(extract_folder, exist_ok=True)
            try:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(extract_folder)
                print(f" ZIP extracted to: {extract_folder}")
            except zipfile.BadZipFile:
                print(" Invalid ZIP file")
                return jsonify({'error': 'Uploaded file is not a valid ZIP archive'}), 400

        # Read metadata from form fields
        metadata = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'source': request.form.get('source'),
            'date': request.form.get('date'),
            'status': request.form.get('status'),
            'filename': file.filename
        }
        print("Received metadata:", metadata)

        # Save metadata as JSON next to file
        meta_path = os.path.splitext(filepath)[0] + '_meta.json'
        with open(meta_path, 'w') as meta_file:
            json.dump(metadata, meta_file, indent=4)

        print(f"Metadata saved to: {meta_path}")
        return jsonify({'message': 'File and metadata uploaded successfully'}), 200

    except Exception as e:
        print(" Upload failed:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

#  NEW: Route to list all uploaded datasets
@app.route('/datasets', methods=['GET'])
def list_datasets():
    datasets = []

    try:
        # Loop through each folder in 'uploads/'
        for folder_name in os.listdir(UPLOAD_FOLDER):
            project_path = os.path.join(UPLOAD_FOLDER, folder_name)
            if os.path.isdir(project_path):
                # Look into each version folder
                for version in os.listdir(project_path):
                    version_path = os.path.join(project_path, version)
                    if os.path.isdir(version_path):
                        for file in os.listdir(version_path):
                            if file.endswith('_meta.json'):
                                meta_path = os.path.join(version_path, file)
                                with open(meta_path, 'r') as f:
                                    metadata = json.load(f)
                                    metadata['project'] = folder_name
                                    metadata['version'] = version
                                    datasets.append(metadata)
        return jsonify(datasets), 200

    except Exception as e:
        print("Error while listing datasets:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

