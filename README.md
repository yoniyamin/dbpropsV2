Replicate Internal Parameters List Web Application
Overview
The Replicate Internal Parameters List web application allows users to browse, search, and comment on internal parameters for databases such as Oracle, Snowflake, and others. The app displays parameters categorized by Source, Target, Other, and Unparsed parameters, and includes functionality for expanding/collapsing parameter details, searching, and adding comments in COMMENT_MODE.

Key Features:
Browse by Database: Select different databases and view their associated parameters.
Search Functionality: Easily search for parameters by name or UI name, with highlighted results shown at the top.
Expandable/Collapsible Sections: View more details of each parameter using the expand button.
Comments: Add multiple comments to parameters when COMMENT_MODE is enabled.
Google and Qlik Community Search: Quick access to search for parameters on Google or Qlik Community with a single click.
Go to Top Button: Smoothly scroll back to the top when navigating long parameter lists.

├── app.py                  # The main Flask application
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── styles.css          # CSS styles for the application
│   ├── icons8-google-48.png # Google search icon
│   └── qlik.48.png          # Qlik Community search icon
└── README.md               # This file

Setup and Installation
Prerequisites
Python 3.x installed on your system
pip (Python package installer)
Dependencies
The required packages can be installed using the requirements.txt (if available), or install them manually

Open in Browser: Once the Flask app is running, open your browser and navigate to:
http://127.0.0.1:5000/
