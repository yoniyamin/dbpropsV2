from flask import Flask, render_template, request, redirect, url_for
import xml.etree.ElementTree as ET
import json
import os
import re  # Import re for regular expressions

app = Flask(__name__)

# Flag for comment mode (Set this to True to enable comment mode)
COMMENT_MODE = False

# Path to the file where comments will be stored
COMMENTS_FILE = "comments.json"

# Function to load comments from the JSON file
def load_comments():
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Function to save comments to the JSON file
def save_comments(comments):
    with open(COMMENTS_FILE, 'w') as f:
        json.dump(comments, f, indent=4)

# Function to load and parse the XML file
def load_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

# Function to extract dbid list and metadata from XML, including "syntax" info
def extract_db_metadata(xml_root):
    metadata_list = []
    for dbid in xml_root.findall("dbid"):
        title = dbid.get("title")
        db_type = dbid.get("type")
        syntax = dbid.get("syntax")  # Extract the syntax

        # Append "(target)" to title or type if type contains "target"
        display_name = title if title else db_type
        if "target" in db_type.lower():
            display_name += " (target)"

        # Filter out invalid entries like "enum"
        if display_name.lower() != "enum":
            metadata_list.append({
                "id": dbid.get("id"),
                "title": display_name,
                "syntax": syntax
            })
    return metadata_list

# Function to clean and fix the JSON parameter string
def clean_param_text(param_text):
    param_text = param_text.strip()

    # Remove any trailing commas (handle multiple commas)
    param_text = re.sub(r',+$', '', param_text)

    # Add missing opening curly brace if needed
    if not param_text.startswith('{'):
        param_text = '{' + param_text

    # Remove any trailing comments (//)
    param_text = re.sub(r'//.*$', '', param_text)

    return param_text

# Function to extract parameters for a specific dbid
def extract_parameters(xml_root, selected_dbid):
    dbid_elem = xml_root.find(f"dbid[@id='{selected_dbid}']")
    if dbid_elem is not None:
        source_params = []
        target_params = []
        other_params = []  # Parameters without role
        unparsed_params = []  # Separate list for unparsed parameters
        print(f"Extracting parameters for dbid: {selected_dbid}")  # Debugging

        for param in dbid_elem.findall("parameter"):
            param_text = clean_param_text(param.text)

            try:
                # Attempt to parse the cleaned parameter as JSON
                param_dict = json.loads(param_text)
                print(f"Found parameter: {param_dict}")  # Debugging
                # Split parameters by role: Source, Target, Other, Unparsed
                if param_dict.get("role") == "SOURCE":
                    source_params.append(param_dict)
                elif param_dict.get("role") == "TARGET":
                    target_params.append(param_dict)
                else:
                    other_params.append(param_dict)
            except json.JSONDecodeError as e:
                # Handle unparsed parameter and try to extract the name from 'value' if it exists
                print(f"Error parsing parameter: {param_text}, Error: {e}")
                param_name = param_text.split('"name":')[1].split('"')[1] if '"name":' in param_text else "Unknown Parameter"
                unparsed_params.append({"name": param_name, "value": param_text})

        return source_params, target_params, other_params, unparsed_params
    else:
        print(f"No dbid found for {selected_dbid}")  # Debugging
    return [], [], [], []

# Load the XML file
xml_root = load_xml("dbid_internal.xml")

@app.route('/', methods=['GET', 'POST'])
def index():
    db_metadata = extract_db_metadata(xml_root)
    source_params, target_params, other_params, unparsed_params = [], [], [], []
    selected_dbid = None
    syntax = None
    comments = load_comments()

    if request.method == 'POST':
        selected_dbid = request.form.get('dbid')
        print(f"Selected dbid: {selected_dbid}")  # Debugging
        source_params, target_params, other_params, unparsed_params = extract_parameters(xml_root, selected_dbid)

        # Find the syntax for the selected dbid
        for db in db_metadata:
            if db["id"] == selected_dbid:
                syntax = db["syntax"]
                break

    return render_template('index.html', db_metadata=db_metadata, source_params=source_params,
                           target_params=target_params, other_params=other_params, unparsed_params=unparsed_params,
                           selected_dbid=selected_dbid, syntax=syntax, comments=comments, comment_mode=COMMENT_MODE)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    param_name = request.form.get('param_name')
    comment = request.form.get('comment')
    comments = load_comments()

    # Append the comment to the list of comments for the given parameter name
    if param_name in comments:
        comments[param_name].append(comment)
    else:
        comments[param_name] = [comment]
    save_comments(comments)

    # Redirect back to the home page
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
