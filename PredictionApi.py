from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

total_ribbons = 0
total_arrows = 0
total_stars = 0

prediction_threshold = 0.90

def make_prediction(image_file):
    prediction_key = "27dea928805b4e6baf8b46e2854986b7"
    endpoint = 'https://cvobjectdetector-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/060c28e6-5b5f-41cb-8426-5036e6cfa1b9/detect/iterations/Iteration1/image'
    headers = {
        "Prediction-Key": prediction_key,
        "Content-Type": "application/octet-stream",
    }
    response = requests.post(endpoint, headers=headers, data=image_file.read())

    if response.status_code == 200:
        result = response.json()
        return {
            "Total Ribbons": sum(1 for obj in result.get("predictions", []) if obj["tagName"] == "Ribbon" and obj["probability"] >= prediction_threshold),
            "Total Arrows": sum(1 for obj in result.get("predictions", []) if obj["tagName"] == "Arrow" and obj["probability"] >= prediction_threshold),
            "Total Stars": sum(1 for obj in result.get("predictions", []) if obj["tagName"] == "Star" and obj["probability"] >= prediction_threshold)
        }
    else:
        return {"Error": f"{response.status_code} - {response.text}"}

@app.route('/', methods=['GET', 'POST'])
def detect_objects():
    global total_ribbons, total_arrows, total_stars

    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return jsonify({"Error": "No image file provided"}), 400

            image_file = request.files['image']

            if image_file.filename == '':
                return jsonify({"Error": "No selected file"}), 400

            # Make predictions
            prediction_result = make_prediction(image_file)
            
            # Update global counts
            total_ribbons = prediction_result["Total Ribbons"]
            total_arrows = prediction_result["Total Arrows"]
            total_stars = prediction_result["Total Stars"]

            return jsonify(prediction_result)
        except Exception as e:
            return jsonify({"Error": f"Unexpected error: {str(e)}"}), 500

    elif request.method == 'GET':
        # Display form for uploading images
        return '''
        <!doctype html>
        <title>Upload an image</title>
        <h1>Upload an image</h1>
        <form method=post action="/" enctype=multipart/form-data>
            <input type=file name=image>
            <input type=submit value=Upload>
        </form>
        '''

if __name__ == '__main__':
    app.run(debug=True)






