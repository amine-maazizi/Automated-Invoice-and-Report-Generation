import os
import pdfkit
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Get the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Set up paths
template_path = os.path.join(root_dir, 'templates')  # Path to templates
output_invoices_path = os.path.join(root_dir, 'data', 'output', 'invoices')  # Path to invoices output
output_reports_path = os.path.join(root_dir, 'data', 'output', 'reports')  # Path to reports output

# Ensure output directories exist
os.makedirs(output_invoices_path, exist_ok=True)
os.makedirs(output_reports_path, exist_ok=True)

# Configure Jinja2 environment
env = Environment(loader=FileSystemLoader(template_path))

def load_template(template_name):
    """
    Load the specified HTML template using Jinja2.

    Parameters:
    - template_name (str): Name of the HTML template file.

    Returns:
    - Template: Jinja2 template object.
    """
    try:
        return env.get_template(template_name)
    except TemplateNotFound:
        print(f"Error: Template '{template_name}' not found in path '{template_path}'.")
        raise

def render_html(template, context):
    """
    Render HTML content from a Jinja2 template and a context dictionary.

    Parameters:
    - template (Template): Jinja2 template object.
    - context (dict): Dictionary containing data to populate the template.

    Returns:
    - str: Rendered HTML content as a string.
    """
    try:
        return template.render(context)
    except Exception as e:
        print(f"Error rendering HTML: {e}")
        raise

def html_to_pdf(html_content, output_path):
    """
    Convert rendered HTML content to a PDF file.

    Parameters:
    - html_content (str): HTML content to convert to PDF.
    - output_path (str): Path where the PDF file should be saved.
    """
    try:
        # Use additional options to handle local file access and enable debugging
        options = {
            'enable-local-file-access': '',  # Allow access to local files
            'quiet': '',  # Suppress messages, but keep error messages visible
        }
        # Convert HTML to PDF using pdfkit with specific options
        pdfkit.from_string(html_content, output_path, options=options)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise

def generate_invoice(data):
    """
    Generate an invoice PDF from the validated data.

    Parameters:
    - data (dict): Validated data from the Excel sheets.

    Returns:
    - dict: A dictionary mapping client emails to their respective invoice file paths.
    """
    try:
        # Load the invoice template
        template = load_template('invoice_template.html')
    except Exception as e:
        print(f"Error loading template: {e}")
        return None

    # Access the clean DataFrames for "Orders" and "Clients"
    orders_df = data["Orders"]["clean_data"]
    clients_df = data["Clients"]["clean_data"]
    products_df = data["Products"]["clean_data"]
    
    # Check if any required data is missing
    if orders_df is None or clients_df is None:
        print("No valid orders or clients data to generate invoices.")
        return None

    # Initialize the dictionary to map client emails to their invoices
    client_invoice_map = {}

    # Loop through each order to generate an invoice
    for index, row in orders_df.iterrows():
        try:
            # Lookup client details using the "Client ID"
            client_details = clients_df[clients_df["Client ID"] == row["Client ID"]].iloc[0]
            
            # Create context for rendering
            context = {
                "invoice_id": row["Order ID"],
                "invoice_date": row["Order Date"],
                "due_date": row["Delivery Date"],
                "client_name": client_details["Client Name"],
                "contact_person": client_details["Contact Person"],
                "client_email": client_details["Email"],
                "client_address": client_details["Address"],
                "order_items": [],  # To be filled dynamically
                "total_amount_due": row["Total Amount ($)"]
            }

            # Extract order details dynamically
            order_items = []
            for product_id in row["Product ID"].split(','):  # Assuming multiple products are separated by commas
                product = products_df[products_df["Product ID"] == product_id.strip()].iloc[0]
                order_items.append({
                    "product_name": product["Product Name"],
                    "unit_price": product["Unit Price ($)"],
                    "quantity": row["Quantity"],  # Adjust as necessary
                    "total_price": row["Quantity"] * product["Unit Price ($)"]
                })

            context["order_items"] = order_items

            # Define a safe and unique filename for the invoice
            client_name_safe = client_details["Client Name"].replace(" ", "_").replace(",", "")  # Replace spaces and commas with underscores
            output_path = os.path.join(output_invoices_path, f"invoice_{client_name_safe}_{row['Order ID']}.pdf")
            
            # Render the HTML content
            html_content = render_html(template, context)

            # Convert to PDF and save
            html_to_pdf(html_content, output_path)

            # Store the client email and corresponding invoice path
            client_invoice_map[client_details["Email"]] = output_path

        except Exception as e:
            print(f"Error generating invoice for order {row['Order ID']}: {e}")

    return client_invoice_map  # Ensure the map is returned

def generate_report(data):
    """
    Generate a report PDF from the validated data.

    Parameters:
    - data (dict): Validated data from the Excel sheets.
    """
    try:
        # Load the report template
        template = load_template('report_template.html')
    except Exception as e:
        print(f"Error loading report template: {e}")
        return

    # Access the clean DataFrames for Orders and Invoices
    orders_df = data["Orders"]["clean_data"]
    invoices_df = data["Invoices"]["clean_data"]
    clients_df = data["Clients"]["clean_data"]
    
    if orders_df is None or invoices_df is None or clients_df is None:
        print("No valid data to generate the report.")
        return

    # Calculate Total Sales and Outstanding Invoices
    total_sales = orders_df["Total Amount ($)"].sum()
    outstanding_invoices = invoices_df[invoices_df["Paid Status"] == "Unpaid"]["Amount Due ($)"].sum()

    # Calculate Total Purchases by Clients
    client_purchases = orders_df.groupby("Client ID")["Total Amount ($)"].sum().reset_index()
    client_purchases = client_purchases.merge(clients_df, on="Client ID", how="left")

    # Identify Top Clients
    top_clients = client_purchases.nlargest(5, "Total Amount ($)").to_dict(orient='records')  # Top 5 clients by purchase

    # Prepare Detailed Orders Report with Client Names
    detailed_orders = orders_df.merge(clients_df, on="Client ID", how="left")
    detailed_orders = detailed_orders[["Client Name", "Order ID", "Order Date", "Total Amount ($)", "Status"]]
    detailed_orders = detailed_orders.rename(columns={
        "Client Name": "client_name",
        "Order ID": "order_id",
        "Order Date": "order_date",
        "Total Amount ($)": "amount",
        "Status": "status"
    })
    orders_list = detailed_orders.to_dict(orient='records')

    # Prepare context for the report
    context = {
        "report_period": "August 2024",  # Example: hardcoded or dynamically calculated
        "total_sales": total_sales,
        "outstanding_invoices": outstanding_invoices,
        "top_clients": [{"name": client["Client Name"], "total_purchase": client["Total Amount ($)"]} for client in top_clients],
        "orders": orders_list  # Use the detailed orders with client names
    }

    try:
        # Render the HTML content
        html_content = render_html(template, context)
        
        # Define output path
        output_path = os.path.join(output_reports_path, "report_August_2024.pdf")

        # Convert to PDF and save
        html_to_pdf(html_content, output_path)
    except Exception as e:
        print(f"Error generating report: {e}")
