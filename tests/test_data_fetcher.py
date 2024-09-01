import unittest
import pandas as pd
from src.data_fetcher import fetch_data_from_excel

class TestDataFetcher(unittest.TestCase):

    def setUp(self):
        # Set up a sample Excel file path for testing
        self.sample_file_path = "data/input/public_works_invoice_data.xlsx"

    def test_fetch_data_from_excel_all_sheets(self):
        """Test fetching all sheets from the Excel file."""
        data = fetch_data_from_excel(self.sample_file_path)
        
        # Check that the output is a dictionary and contains at least one sheet
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)  # Ensure at least one sheet is loaded
        self.assertIn("Clients", data)    # Ensure the "Clients" sheet is loaded

        # Verify that all specified sheets are in the data
        expected_sheets = ["Clients", "Products", "Orders", "Invoices"]
        for sheet in expected_sheets:
            self.assertIn(sheet, data)

    def test_fetch_data_from_excel_specific_sheets(self):
        """Test fetching specific sheets from the Excel file."""
        data = fetch_data_from_excel(self.sample_file_path, ["Clients", "Products"])
        self.assertEqual(len(data), 2)  # Should only fetch the specified sheets
        self.assertIn("Clients", data)
        self.assertIn("Products", data)

    def test_fetch_data_with_invalid_sheet(self):
        """Test handling of invalid sheet name."""
        data = fetch_data_from_excel(self.sample_file_path, ["NonExistentSheet"])
        self.assertEqual(len(data), 0)  # No sheets should be returned

if __name__ == "__main__":
    unittest.main()
