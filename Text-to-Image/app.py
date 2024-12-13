import base64
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Function to fetch base64 image from the external API
def fetch_base64_image(prompt):
    try:
        api_url = "https://restapi-238600609590.us-central1.run.app/"
        payload = {"prompt": prompt}
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            api_response = response.json()
            base64_string = api_response.get("image_base64")
            
            if not base64_string:
                print("Error: No image data in response.")
                return None
            return base64_string
        else:
            print(f"Error: Unable to fetch API response. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt', '')
    base64_string = fetch_base64_image(prompt)
    
    if base64_string:
        return jsonify({"image_base64": base64_string})
    else:
        return jsonify({"error": "Failed to generate image"}), 500

if __name__ == "__main__":
    app.run(debug=True)
