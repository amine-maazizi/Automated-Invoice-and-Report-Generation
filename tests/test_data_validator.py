import unittest
import pandas as pd
from src.data_validator import (
    check_required_fields,
    validate_email_format,
    validate_numeric_fields,
    validate_date_fields,
    check_missing_values,
    validate_data
)

class TestDataValidator(unittest.TestCase):

    def setUp(self):
        # Sample DataFrames for testing
        self.clients_df = pd.DataFrame({
            "Client ID": [101, 102],
            "Client Name": ["XYZ Construction Co", "ABC Builders"],
            "Contact Person": ["John Doe", "Jane Smith"],
            "Email": ["john@xyzcon.com", "invalid-email"],
            "Address": ["1234 Elm St", "5678 Oak Ave"]
        })

        self.products_df = pd.DataFrame({
            "Product ID": ["P001", "P002"],
            "Product Name": ["Asphalt", "Concrete"],
            "Unit Price ($)": [100, "invalid"],
            "Stock Quantity": [500, 300],
            "Description": ["Asphalt for paving", "Concrete for construction"]
        })

    def test_check_required_fields(self):
        """Test for missing required fields."""
        required_fields = ["Client ID", "Client Name", "Email"]
        errors = check_required_fields(self.clients_df, required_fields)
        self.assertEqual(len(errors), 0)  # No missing fields

    def test_validate_email_format(self):
        """Test email format validation."""
        warnings = validate_email_format(self.clients_df)
        self.assertIn("Invalid email formats found.", warnings)

    def test_validate_numeric_fields(self):
        """Test numeric field validation."""
        errors = validate_numeric_fields(self.products_df, "Unit Price ($)")
        self.assertIn("Unit Price ($) should be numeric.", errors)

    def test_validate_date_fields(self):
        """Test date field validation."""
        df = pd.DataFrame({"Order Date": ["2024-08-01", "invalid-date"]})
        errors = validate_date_fields(df, ["Order Date"])
        self.assertIn("Invalid date format in Order Date.", errors)

    def test_check_missing_values(self):
        """Test checking for missing values."""
        df_with_missing = pd.DataFrame({"Client Name": ["XYZ", None]})
        warnings = check_missing_values(df_with_missing, ["Client Name"])
        self.assertIn("Missing values found in Client Name.", warnings)

if __name__ == "__main__":
    unittest.main()
