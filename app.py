from flask import Flask, request, render_template, send_file
import pandas as pd
import os

app = Flask(__name__)

# Define region postcode prefixes
region_postcodes = {
    "North East England": ["DH", "DL", "NE", "SR", "TS"],
    "North West England": ["BB", "BL", "CA", "CH", "CW", "FY", "LA", "L", "M", "OL", "PR", "SK", "WA", "WN"],
    "Yorkshire": ["BD", "DN", "HD", "HG", "HU", "HX", "LS", "S", "WF", "YO"],
    "East Midlands": ["DE", "LE", "NG", "NN", "PE"],
    "West Midlands": ["B", "CV", "DY", "HR", "ST", "SY", "TF", "WR", "WS", "WV"],
    "Scotland": ["AB", "DD", "DG", "EH", "FK", "G", "HS", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "TD", "ZE"],
    "Northern Ireland": ["BT"]
}

# Function to check if a postcode belongs to specified regions
def is_in_region(postcode):
    prefix = postcode[:2].upper()  # Get the first two characters
    for prefixes in region_postcodes.values():
        if prefix in prefixes:
            return True
    return False

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSV Filter Portal</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center">CSV Filter Portal</h1>
            <p class="text-center">Upload a CSV file, and the system will filter bookings based on specific UK postal codes.</p>
            <form action="/upload" method="post" enctype="multipart/form-data" class="text-center">
                <div class="mb-3">
                    <input type="file" name="file" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary">Upload and Filter</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        # Process the CSV
        data = pd.read_csv(filepath)
        if 'Postal Code' not in data.columns:
            return "Error: 'Postal Code' column not found in the file."

        # Filter data
        data['Postal Code'] = data['Postal Code'].astype(str)
        filtered_data = data[data['Postal Code'].apply(is_in_region)]

        # Save filtered file
        output_path = os.path.join("uploads", "Filtered_Bookings.csv")
        filtered_data.to_csv(output_path, index=False)

        return send_file(output_path, as_attachment=True)
    else:
        return "Invalid file format. Please upload a CSV file."

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
