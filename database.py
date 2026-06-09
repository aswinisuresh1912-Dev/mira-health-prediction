import sqlite3
import os
import contextlib

DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patients.db")


@contextlib.contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Sets up the patients table if it doesn't already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                gender TEXT NOT NULL DEFAULT 'Female',
                email TEXT NOT NULL UNIQUE,
                glucose REAL NOT NULL,
                haemoglobin REAL NOT NULL,
                cholesterol REAL NOT NULL,
                remarks TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migration: Check if 'gender' column exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(patients)")
        columns = [row['name'] for row in cursor.fetchall()]
        if columns and "gender" not in columns:
            conn.execute("ALTER TABLE patients ADD COLUMN gender TEXT DEFAULT 'Female'")
            
        conn.commit()


def create_patient(full_name, dob, gender, email, glucose, haemoglobin, cholesterol, remarks):
    """Inserts a new patient and returns the created record."""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO patients (full_name, dob, gender, email, glucose, haemoglobin, cholesterol, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (full_name, dob, gender, email, glucose, haemoglobin, cholesterol, remarks))
            conn.commit()
            return get_patient(cursor.lastrowid)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: patients.email" in str(e):
                raise ValueError(f"A patient with email '{email}' already exists.")
            raise e


def get_all_patients():
    """Returns every patient record, newest first."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_patient(patient_id):
    """Looks up a single patient by their ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_patient(patient_id, full_name, dob, gender, email, glucose, haemoglobin, cholesterol, remarks):
    """Updates a patient's details. Returns the updated record or None if not found."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_id,))
        if not cursor.fetchone():
            return None

        try:
            cursor.execute("""
                UPDATE patients
                SET full_name = ?, dob = ?, gender = ?, email = ?, glucose = ?, haemoglobin = ?, cholesterol = ?, remarks = ?
                WHERE id = ?
            """, (full_name, dob, gender, email, glucose, haemoglobin, cholesterol, remarks, patient_id))
            conn.commit()
            return get_patient(patient_id)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: patients.email" in str(e):
                raise ValueError(f"A patient with email '{email}' already exists.")
            raise e


def delete_patient(patient_id):
    """Removes a patient by ID. Returns True if something was deleted."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        return cursor.rowcount > 0
