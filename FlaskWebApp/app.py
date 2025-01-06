from flask import Flask, request, render_template, send_from_directory, url_for
import requests
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Azure Form Recognizer Configuration
AZURE_ENDPOINT = "<your-endpoint>"
AZURE_API_KEY = "<your-api-key>"
MODEL_ID = "<your-model-id>"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # Save the file temporarily
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        
        # Generate a URL for the uploaded file
        file_url = url_for('uploaded_file', filename=file.filename)
        
        # Send the file to Azure Form Recognizer
        with open(file_path, "rb") as f:
            headers = {
                "Ocp-Apim-Subscription-Key": AZURE_API_KEY,
                "Content-Type": "application/pdf"
            }
            response = requests.post(
                f"{AZURE_ENDPOINT}/formrecognizer/documentModels/{MODEL_ID}:analyze",
                headers=headers,
                data=f
            )

        # Check response
        if response.status_code == 200:
            result = response.json()
            return render_template('result.html', result=result, file_url=file_url)
        else:
            return f"Error: {response.status_code} - {response.text}", 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == '__main__':
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)
