import base64
from google.cloud import aiplatform
from flask import jsonify
import functions_framework

# Constants
PROJECT_ID = "assignment-2-443109"
REGION = "us-central1"
ENDPOINT_ID = "8171369207003348992"

@functions_framework.http
def create(request):
    """HTTP Cloud Function for Stable Diffusion text-to-image generation with CORS support."""
    
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key',
            'Access-Control-Max-Age': '3600',
        }
        return '', 204, headers

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key',
    }

    try:
        # Parse the request JSON
        request_json = request.get_json(silent=True)
        if not request_json:
            return jsonify({"error": "Invalid request: No JSON body found"}), 400, headers

        # Extract parameters
        prompt = request_json.get("prompt")
        if not prompt:
            return jsonify({"error": "Missing required parameter: prompt"}), 400, headers

        num_inference_steps = request_json.get("num_inference_steps", 4)
        width = request_json.get("width", 512)
        height = request_json.get("height", 512)

        # Initialize the AI Platform endpoint
        aiplatform.init(project=PROJECT_ID, location=REGION)
        endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)

        # Send the prediction request
        instances = [{"text": prompt}]
        parameters = {
            "height": height,
            "width": width,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": 7.5
        }
        response = endpoint.predict(instances=instances, parameters=parameters, use_raw_predict=True)

        if not response or not response.predictions:
            return jsonify({"error": "Model did not return predictions"}), 500, headers

        # Decode the base64-encoded image
        generated_image_base64 = response.predictions[0]["output"]

        # Return the base64-encoded image with CORS headers
        return jsonify({"image_base64": generated_image_base64, "prompt": prompt}), 200, headers

    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500, headers