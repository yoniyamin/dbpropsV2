import re
import xml.etree.ElementTree as ET

# First step: Create a flat file with "dbid", "type", "title", and "syntax"
def create_flat_file(content):
    extracted_lines = []
    current_dbid_line = None

    # Iterate through the file line by line
    for line in content.splitlines():
        # Check if the line contains "dbid", "type", "title", or "syntax"
        if '"dbid"' in line or '"type"' in line or '"title"' in line or '"syntax"' in line:
            extracted_lines.append(line)

        # Check if the line contains "level": "INTERNAL"
        elif '"level": "INTERNAL"' in line:
            extracted_lines.append(line)

    return extracted_lines

# Second step: Convert extracted lines into XML format
def convert_to_xml(flat_lines):
    root = ET.Element("dbprops")

    current_dbid_elem = None
    current_metadata = {}

    for line in flat_lines:
        # Check if this is a dbid line
        dbid_match = re.search(r'"dbid":\s*(\d+)', line)
        if dbid_match:
            # If we already have a dbid, add it to the XML structure
            if current_dbid_elem is not None:
                for key, value in current_metadata.items():
                    current_dbid_elem.set(key, value)
                root.append(current_dbid_elem)

            # Create a new dbid element and reset metadata
            current_dbid = dbid_match.group(1)
            current_dbid_elem = ET.Element("dbid", attrib={"id": current_dbid})
            current_metadata = {}

        # Capture type, title, and syntax information
        type_match = re.search(r'"type":\s*"([^"]+)"', line)
        title_match = re.search(r'"title":\s*"([^"]+)"', line)
        syntax_match = re.search(r'"syntax":\s*"([^"]+)"', line)

        if type_match:
            current_metadata["type"] = type_match.group(1)
        if title_match:
            current_metadata["title"] = title_match.group(1)
        if syntax_match:
            current_metadata["syntax"] = syntax_match.group(1)

        # Otherwise, treat this as an item line (assuming it's part of connect_info)
        elif '"level": "INTERNAL"' in line:
            # Add this as a parameter under the current dbid
            if current_dbid_elem is not None:
                param_elem = ET.SubElement(current_dbid_elem, "parameter")
                param_elem.text = line.strip()

    # Add the last dbid element to the XML structure
    if current_dbid_elem is not None:
        for key, value in current_metadata.items():
            current_dbid_elem.set(key, value)
        root.append(current_dbid_elem)

    return root

# Function to save XML tree to a file with XML declaration
def save_xml(root, file_path):
    tree = ET.ElementTree(root)
    with open(file_path, 'wb') as f:
        tree.write(f, xml_declaration=True, encoding='utf-8')

# Read the real content of the input JSON-like file (ar_props.json)
with open('ar_props.json', 'r') as file:
    content = file.read()

# Step 1: Extract flat file lines from real content
flat_file_lines = create_flat_file(content)

# Save the flat file
with open('dbid_internal_flat_file.txt', 'w') as f:
    f.write("\n".join(flat_file_lines))

# Step 2: Convert flat file to XML
xml_root = convert_to_xml(flat_file_lines)

# Save the XML output
xml_file_path = 'dbid_internal.xml'
save_xml(xml_root, xml_file_path)

print(f"Flat file and XML generated successfully: {xml_file_path}")
