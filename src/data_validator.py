import pandas as pd

def check_required_fields(df: pd.DataFrame, required_fields: list) -> list:
    """
    Check for missing required fields in the DataFrame.

    Parameters:
    - df (pd.DataFrame): DataFrame to validate.
    - required_fields (list): List of required fields for the DataFrame.

    Returns:
    - list: List of error messages for missing fields.
    """
    errors = []
    missing_fields = [field for field in required_fields if field not in df.columns]
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")
    return errors

def validate_email_format(df: pd.DataFrame) -> list:
    """
    Validate the format of email addresses in the DataFrame.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the email column.

    Returns:
    - list: List of warning messages for invalid email formats.
    """
    warnings = []
    if "Email" in df.columns:
        invalid_emails = df[~df["Email"].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)]
        if not invalid_emails.empty:
            warnings.append("Invalid email formats found.")
    return warnings

def validate_numeric_fields(df: pd.DataFrame, field: str) -> list:
    """
    Validate that a specified field in the DataFrame is numeric.

    Parameters:
    - df (pd.DataFrame): DataFrame to validate.
    - field (str): Field name to check for numeric data.

    Returns:
    - list: List of error messages for non-numeric fields.
    """
    errors = []
    if field in df.columns and not pd.api.types.is_numeric_dtype(df[field]):
        errors.append(f"{field} should be numeric.")
    return errors

def validate_date_fields(df: pd.DataFrame, fields: list) -> list:
    """
    Validate that specified fields in the DataFrame are in the correct date format.

    Parameters:
    - df (pd.DataFrame): DataFrame to validate.
    - fields (list): List of field names to check for date data.

    Returns:
    - list: List of error messages for invalid date formats.
    """
    errors = []
    for field in fields:
        if field in df.columns:
            df[field] = pd.to_datetime(df[field], errors='coerce')
            if df[field].isnull().any():
                errors.append(f"Invalid date format in {field}.")
    return errors

def check_missing_values(df: pd.DataFrame, required_fields: list) -> list:
    """
    Check for missing values in required fields of the DataFrame.

    Parameters:
    - df (pd.DataFrame): DataFrame to validate.
    - required_fields (list): List of required fields to check for missing values.

    Returns:
    - list: List of warning messages for missing values.
    """
    warnings = []
    for field in required_fields:
        if field in df.columns and df[field].isnull().any():
            warnings.append(f"Missing values found in {field}.")
    return warnings

def validate_data(data: dict) -> dict:
    """
    Validates the data extracted from Excel sheets to ensure it is clean and ready for processing.

    Parameters:
    - data (dict): Dictionary where each key is a sheet name, and the value is a DataFrame containing the data from that sheet.

    Returns:
    - dict: Dictionary containing validation results for each sheet (errors, warnings, and clean data).
    """
    validation_results = {}

    # Define required fields for each sheet
    required_fields = {
        "Clients": ["Client ID", "Client Name", "Contact Person", "Email", "Address"],
        "Products": ["Product ID", "Product Name", "Unit Price ($)", "Stock Quantity", "Description"],
        "Orders": ["Order ID", "Client ID", "Order Date", "Product ID", "Quantity", "Total Amount ($)", "Delivery Date", "Status"],
        "Invoices": ["Invoice ID", "Order ID", "Invoice Date", "Due Date", "Amount Due ($)", "Paid Status"]
    }

    # Loop through each sheet and validate data
    for sheet_name, df in data.items():
        errors = []
        warnings = []

        # Perform various validations
        errors.extend(check_required_fields(df, required_fields.get(sheet_name, [])))

        if sheet_name == "Clients":
            warnings.extend(validate_email_format(df))

        if sheet_name == "Products":
            errors.extend(validate_numeric_fields(df, "Unit Price ($)"))

        if sheet_name == "Orders":
            errors.extend(validate_date_fields(df, ["Order Date"]))

        if sheet_name == "Invoices":
            errors.extend(validate_date_fields(df, ["Invoice Date", "Due Date"]))

        warnings.extend(check_missing_values(df, required_fields.get(sheet_name, [])))

        # Save validation results for the sheet
        validation_results[sheet_name] = {
            "errors": errors,
            "warnings": warnings,
            "clean_data": df if not errors else None  # Return clean data only if no critical errors
        }

    return validation_results
