from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from data_fetcher import fetch_data_from_excel
from data_validator import validate_data
from document_generator import generate_invoice, generate_report
from email_sender import send_invoices_to_clients, send_reports_to_managers


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    data = request.get_json()
    file_path = data.get('filePath')

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 400

    try:
        df = pd.read_excel(file_path, sheet_name=0)  # Read the first sheet
        head_data = {
            "columns": df.columns.tolist(),
            "rows": df.head().values.tolist()  # Convert the head of the DataFrame to a list of lists
        }
        return jsonify({"head": head_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-invoices', methods=['POST'])
def generate_invoices():
    try:
        # Assume settings file contains necessary paths
        settings = request.get_json()
        
        # Check if filePath is in settings
        if 'filePath' not in settings or not settings['filePath']:
            return jsonify({"error": "File path is missing"}), 400

        # Check if the file exists
        if not os.path.exists(settings['filePath']):
            return jsonify({"error": "Excel file not found"}), 400

        # Fetch and validate data
        data = fetch_data_from_excel(settings['filePath'])
        if not data:
            return jsonify({"error": "Failed to fetch data from Excel"}), 500

        validation_results = validate_data(data)

        # Generate invoices
        client_invoice_map = generate_invoice(validation_results)
        if client_invoice_map:
            return jsonify({"status": "success", "message": "Invoices generated successfully."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to generate invoices."}), 400
    except Exception as e:
        print("Error generating invoices:", str(e))  # Debug line
        return jsonify({"error": str(e)}), 500

@app.route('/generate-reports', methods=['POST'])
def generate_reports():
    try:
        settings = request.get_json()
        data = fetch_data_from_excel(settings['filePath'])
        validation_results = validate_data(data)
        
        generate_report(validation_results)
        return jsonify({"status": "success", "message": "Reports generated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send-invoices', methods=['POST'])
def send_invoices():
    try:
        # Load settings from the request body
        settings = request.get_json()

        # Ensure required settings are present
        if not settings:
            return jsonify({"error": "No settings provided"}), 400

        # Define the paths based on settings
        invoices_folder = settings['invoicesFolder']
        invoice_paths = find_all_invoices(invoices_folder)

        # Check if invoice paths exist
        if not invoice_paths:
            return jsonify({"error": "No invoice files found in the invoices folder"}), 400

        # Create a mapping of client emails to their respective invoice paths
        client_invoice_map = create_client_invoice_map(invoice_paths)

        # Email server configuration
        smtp_server = settings.get('emailServer')
        port = 587  # Common SMTP port
        sender_email = settings.get('emailUser')
        sender_password = settings.get('emailPassword')

        # Validate required email settings
        if not smtp_server or not sender_email or not sender_password:
            return jsonify({"error": "Missing email configuration settings."}), 400

        # Send invoices to clients
        send_invoices_to_clients(
            client_invoice_map=client_invoice_map,
            smtp_server=smtp_server,
            port=port,
            sender_email=sender_email,
            sender_password=sender_password
        )

        return jsonify({"status": "success", "message": "Invoices sent successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_client_invoice_map(invoice_paths):
    """
    Create a mapping of client emails to their respective invoice paths.

    Parameters:
    - invoice_paths (list): List of paths to invoice files.

    Returns:
    - dict: A dictionary mapping client emails to their respective invoice paths.
    """
    client_invoice_map = {}
    for path in invoice_paths:
        # Assuming the client email or ID is part of the filename, you can adjust this as needed
        client_name = os.path.basename(path).split('_')[1]  # Adjust splitting logic as necessary
        client_email = f"{client_name.lower()}@example.com"  # Replace this with actual logic to map client names to emails
        client_invoice_map[client_email] = path
    return client_invoice_map

def find_all_invoices(invoices_folder):
    """
    Find all invoice files in the specified folder.

    Parameters:
    - invoices_folder (str): The path to the invoices folder.

    Returns:
    - list: A list of paths to all invoice files.
    """
    try:
        invoices = [os.path.join(invoices_folder, f) for f in os.listdir(invoices_folder) if f.endswith('.pdf')]
        return invoices
    except Exception as e:
        print(f"Error finding invoices: {e}")
        return []


@app.route('/send-report', methods=['POST'])
def send_report():
    try:
        # Load settings from the request body
        settings = request.get_json()

        # Ensure required settings are present
        if not settings:
            return jsonify({"error": "No settings provided"}), 400

        # Retrieve manager emails and validate
        manager_emails = settings.get('managerEmails', [])
        if not manager_emails:
            return jsonify({"error": "No manager emails provided in settings"}), 400

        # Define the paths based on settings
        reports_folder = settings['reportsFolder']
        report_path = find_latest_report(reports_folder)

        # Check if report path exists
        if not report_path or not os.path.exists(report_path):
            return jsonify({"error": f"Report file not found at {report_path}"}), 400

        # Email server configuration
        smtp_server = settings.get('emailServer')
        port = 587  # Common SMTP port
        sender_email = settings.get('emailUser')
        sender_password = settings.get('emailPassword')

        # Validate required email settings
        if not smtp_server or not sender_email or not sender_password:
            return jsonify({"error": "Missing email configuration settings."}), 400

        # Send report to managers
        send_reports_to_managers(
            manager_emails=manager_emails,
            report_path=report_path,
            smtp_server=smtp_server,
            port=port,
            sender_email=sender_email,
            sender_password=sender_password,
            invoice_paths=[]  # No additional invoices to attach for report sending
        )

        return jsonify({"status": "success", "message": "Report sent to managers successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def find_latest_report(reports_folder):
    """
    Find the latest report in the specified folder based on file modification time.

    Parameters:
    - reports_folder (str): The path to the reports folder.

    Returns:
    - str: The path to the latest report file.
    """
    try:
        reports = [os.path.join(reports_folder, f) for f in os.listdir(reports_folder) if f.endswith('.pdf')]
        if not reports:
            return None
        latest_report = max(reports, key=os.path.getmtime)
        return latest_report
    except Exception as e:
        print(f"Error finding latest report: {e}")
        return None

if __name__ == '__main__':
    app.run(port=5000)  # Run Flask server on port 5000
