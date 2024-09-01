import pandas as pd

def fetch_data_from_excel(file_path: str, required_sheets: list = None) -> dict:
    """
    Reads data from an Excel file and returns a dictionary of DataFrames.

    Parameters:
    - file_path (str): Path to the Excel file.
    - required_sheets (list of str, optional): List of sheet names to fetch. Defaults to None (fetches all sheets).

    Returns:
    - dict: Dictionary where each key is a sheet name and the value is a corresponding DataFrame.
    """
    try:
        # Load the Excel file
        excel_data = pd.ExcelFile(file_path)
        
        # Determine which sheets to fetch
        if required_sheets:
            sheets_to_fetch = [sheet for sheet in required_sheets if sheet in excel_data.sheet_names]
        else:
            sheets_to_fetch = excel_data.sheet_names  # Fetch all sheets if none specified

        # Read the data from each sheet and store in a dictionary
        data = {sheet: excel_data.parse(sheet) for sheet in sheets_to_fetch}

        return data

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return {}
