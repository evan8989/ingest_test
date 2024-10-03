from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Define your required and optional columns
REQUIRED_COLUMNS = ['First Name', 'Last Name', 'Date of Birth']
OPTIONAL_COLUMNS = ['Sex', 'Age', 'Race']

# Define the output folder
OUTPUT_FOLDER = os.path.join(os.getcwd(), "static")

# Create the static folder if it does not exist
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file is uploaded
        if 'file' not in request.files:
            return 'No file uploaded', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400

        # Save the uploaded file to a specific location
        file_name = 'uploaded_file.xlsx'
        file.save(file_name)

        # Read the uploaded Excel file into a DataFrame
        df = pd.read_excel(file_name, engine='openpyxl')

        # Get the column headers from the uploaded file
        columns = df.columns.tolist()

        # Pass the columns to the match_columns template for initial selection
        return render_template('match_columns.html', columns=columns,
                               required_columns=REQUIRED_COLUMNS,
                               optional_columns=OPTIONAL_COLUMNS, file_name=file_name)
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # Retrieve the filename from the form submission
    file_name = request.form['file_name']
    df = pd.read_excel(file_name, engine='openpyxl')

    # Create a new DataFrame with the matched columns
    new_df = pd.DataFrame()

    # Track columns that have already been matched to prevent duplicates
    used_columns = set()

    # Match required columns
    for req_col in REQUIRED_COLUMNS:
        matched_col = request.form.get(f'req_{req_col}')
        if matched_col and matched_col in df.columns and matched_col not in used_columns:
            new_df[req_col] = df[matched_col]
            used_columns.add(matched_col)  # Add to used columns set
        else:
            return f'Missing or duplicate required column mapping: {req_col}', 400

    # Match optional columns if they exist in the uploaded file
    for opt_col in OPTIONAL_COLUMNS:
        matched_col = request.form.get(f'opt_{opt_col}')
        if matched_col and matched_col in df.columns and matched_col not in used_columns:
            new_df[opt_col] = df[matched_col]
            used_columns.add(matched_col)  # Add to used columns set

    # Save to new Excel file in the static folder
    new_file_name = os.path.join(OUTPUT_FOLDER, 'output_fun_data.xlsx')
    new_df.to_excel(new_file_name, index=False)

    # Provide a download link to the processed file
    download_link = f'<a href="/static/output_fun_data.xlsx">Download processed file</a>'
    return f'File processed and saved as <strong>{new_file_name}</strong>. {download_link}'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
