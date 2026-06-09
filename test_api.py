import unittest
import os
import datetime
import database
from ml_model import HealthPredictor
from main import validate_input
from fastapi import HTTPException

class TestHealthPredictionApp(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Override database file to a test database
        cls.test_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_patients.db")
        database.DATABASE_FILE = cls.test_db
        # Initialize test database
        database.init_db()
        cls.predictor = HealthPredictor()

    @classmethod
    def tearDownClass(cls):
        # Clean up the test database file
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def setUp(self):
        # Clear patients table before each test
        with database.get_connection() as conn:
            conn.execute("DELETE FROM patients")
            conn.commit()

    # 1. Test ML Health Predictor Logic
    def test_predictor_low_risk(self):
        # Normal levels for a young adult
        prediction = self.predictor.predict(glucose=85.0, haemoglobin=14.0, cholesterol=180.0, dob_str="1995-05-15", gender="Female")
        self.assertEqual(prediction["risk_level"], "Low")
        self.assertIn("Optimal Health Profile", prediction["condition"])
        self.assertTrue(prediction["confidence"] < 50.0)

    def test_predictor_diabetic_risk(self):
        # High glucose levels
        prediction = self.predictor.predict(glucose=150.0, haemoglobin=13.5, cholesterol=180.0, dob_str="1980-01-01", gender="Male")
        self.assertEqual(prediction["risk_level"], "High")
        self.assertIn("Hyperglycemia (Diabetic Risk)", prediction["condition"])

    def test_predictor_anemia_risk(self):
        # Low haemoglobin
        prediction = self.predictor.predict(glucose=90.0, haemoglobin=9.5, cholesterol=185.0, dob_str="1990-08-20", gender="Female")
        self.assertEqual(prediction["risk_level"], "High")
        self.assertIn("Severe Anemia Risk", prediction["condition"])

    def test_predictor_moderate_risk(self):
        # Borderline metrics
        prediction = self.predictor.predict(glucose=105.0, haemoglobin=12.5, cholesterol=210.0, dob_str="1985-04-12", gender="Female")
        self.assertEqual(prediction["risk_level"], "Moderate")

    def test_predictor_gender_thresholds(self):
        # Haemoglobin: Male normal min is 13.8, Female normal min is 12.1.
        # Hb = 13.0 is normal for Female but low for Male.
        pred_female = self.predictor.predict(glucose=90.0, haemoglobin=13.0, cholesterol=180.0, dob_str="1995-05-15", gender="Female")
        self.assertNotIn("Anemia", pred_female["condition"])
        
        pred_male = self.predictor.predict(glucose=90.0, haemoglobin=13.0, cholesterol=180.0, dob_str="1995-05-15", gender="Male")
        self.assertIn("Mild Anemia Risk", pred_male["condition"])

    # 2. Test Input Validation Logic
    def test_validation_valid_input(self):
        # Should complete without throwing exception
        try:
            validate_input("Jane Doe", "1990-01-01", "Female", "jane.doe@example.com", 90.0, 13.5, 180.0)
        except HTTPException:
            self.fail("validate_input raised HTTPException unexpectedly!")

    def test_validation_future_dob(self):
        future_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        with self.assertRaises(HTTPException) as context:
            validate_input("Jane Doe", future_date, "Female", "jane@example.com", 90.0, 13.5, 180.0)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("future", context.exception.detail)

    def test_validation_invalid_email(self):
        with self.assertRaises(HTTPException) as context:
            validate_input("Jane Doe", "1990-01-01", "Female", "jane_at_domain_dot_com", 90.0, 13.5, 180.0)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("valid email", context.exception.detail)

    def test_validation_negative_metrics(self):
        with self.assertRaises(HTTPException) as context:
            validate_input("Jane Doe", "1990-01-01", "Female", "jane@example.com", -10.0, 13.5, 180.0)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("positive numbers", context.exception.detail)

    def test_validation_invalid_gender(self):
        with self.assertRaises(HTTPException) as context:
            validate_input("Jane Doe", "1990-01-01", "Robot", "jane@example.com", 90.0, 13.5, 180.0)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Gender", context.exception.detail)

    # 3. Test SQLite CRUD Operations
    def test_crud_operations(self):
        # CREATE
        p = database.create_patient(
            full_name="Alice Smith",
            dob="1992-06-30",
            gender="Female",
            email="alice@example.com",
            glucose=95.0,
            haemoglobin=12.5,
            cholesterol=190.0,
            remarks="[Low Risk] Normal metrics"
        )
        self.assertIsNotNone(p["id"])
        self.assertEqual(p["full_name"], "Alice Smith")
        self.assertEqual(p["gender"], "Female")

        # READ (All)
        patients = database.get_all_patients()
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0]["email"], "alice@example.com")
        self.assertEqual(patients[0]["gender"], "Female")

        # READ (Single)
        patient_id = p["id"]
        fetched = database.get_patient(patient_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["full_name"], "Alice Smith")
        self.assertEqual(fetched["gender"], "Female")

        # UPDATE
        updated = database.update_patient(
            patient_id=patient_id,
            full_name="Alice Jones",
            dob="1992-06-30",
            gender="Male",
            email="alice@example.com",
            glucose=110.0,
            haemoglobin=12.5,
            cholesterol=190.0,
            remarks="[Moderate Risk] Prediabetic"
        )
        self.assertEqual(updated["full_name"], "Alice Jones")
        self.assertEqual(updated["gender"], "Male")
        self.assertEqual(updated["glucose"], 110.0)

        # DELETE
        deleted = database.delete_patient(patient_id)
        self.assertTrue(deleted)
        self.assertIsNone(database.get_patient(patient_id))

if __name__ == '__main__':
    unittest.main()
