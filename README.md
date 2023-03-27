# Gmail Email Subject Monitor

This Python script monitors your Gmail inbox for specific emails based on their subject content. It checks for new emails every 60 seconds and writes the results to a json file.

## Prerequisites

- Python 3.6 or higher
- A Google account with Gmail access

## Dependencies

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Setup
1. Go to the Google Developer Console.
2. Create a new project or select an existing one.
3. Click on "Enable APIs and Services" and enable the Gmail API.
4. Go to "Credentials" and create an OAuth 2.0 Client ID.
5. Download the JSON file for the created Client ID and save it as credentials.json in the same directory as the script.
6. Save a .env file and populate it with SUBJECT_TO_SEARCH and POLLING_INTERVAL

## Usage
After setting up your virtual environment, run the script in your terminal:

```bash
python main.py
```
The script will open a browser window for authorization. Allow access to your Gmail account, and the script will start monitoring your inbox for new emails with subjects starting with your SUBJECT_TO_SEARCH variable.
