import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def load_manager_emails(file_path: str) -> list:
    """
    Load manager emails from a text file.

    Parameters:
    - file_path (str): Path to the text file containing manager emails.

    Returns:
    - list: A list of manager email addresses.
    """
    try:
        with open(file_path, 'r') as f:
            manager_emails = [line.strip() for line in f if line.strip()]
        return manager_emails
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []

def send_email(smtp_server, port, sender_email, sender_password, recipient_email, subject, body, attachments=None):
    """
    Send an email with optional attachments.

    Parameters:
    - smtp_server (str): The SMTP server address.
    - port (int): Port number for the SMTP server.
    - sender_email (str): The sender's email address.
    - sender_password (str): The sender's email password.
    - recipient_email (str): The recipient's email address.
    - subject (str): The email subject.
    - body (str): The email body.
    - attachments (list, optional): List of file paths to attach to the email.
    """
    try:
        # Set up the email content
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Attach files
        if attachments:
            for file_path in attachments:
                with open(file_path, "rb") as attachment_file:
                    part = MIMEApplication(attachment_file.read(), Name=file_path)
                    part['Content-Disposition'] = f'attachment; filename="{file_path.split("/")[-1]}"'
                    msg.attach(part)

        # Set up the SMTP server and send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Email sent to {recipient_email}")

    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")

def send_invoices_to_clients(client_invoice_map, smtp_server, port, sender_email, sender_password):
    """
    Send invoices to clients using the client-email to invoice mapping.

    Parameters:
    - client_invoice_map (dict): A dictionary mapping client emails to their respective invoice file paths.
    - smtp_server (str): The SMTP server address.
    - port (int): Port number for the SMTP server.
    - sender_email (str): The sender's email address.
    - sender_password (str): The sender's email password.
    """
    for client_email, invoice_path in client_invoice_map.items():
        subject = "Your Invoice from [Your Company]"
        body = "Dear client,\n\nPlease find your invoice attached.\n\nBest regards,\n[Your Company]"

        send_email(smtp_server, port, sender_email, sender_password, client_email, subject, body, [invoice_path])

def send_reports_to_managers(manager_emails, report_path, smtp_server, port, sender_email, sender_password, invoice_paths):
    """
    Send reports and invoices to managers.

    Parameters:
    - manager_emails (list): List of manager email addresses.
    - report_path (str): Path to the consolidated report file.
    - smtp_server (str): The SMTP server address.
    - port (int): Port number for the SMTP server.
    - sender_email (str): The sender's email address.
    - sender_password (str): The sender's email password.
    - invoice_paths (list): List of all invoice file paths.
    """
    for manager_email in manager_emails:
        subject = "Monthly Reports and Invoices from [Your Company]"
        body = "Dear Manager,\n\nPlease find the consolidated report and all invoices attached.\n\nBest regards,\n[Your Company]"
        attachments = [report_path] + invoice_paths

        send_email(smtp_server, port, sender_email, sender_password, manager_email, subject, body, attachments)
