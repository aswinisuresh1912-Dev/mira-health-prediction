import database
from ml_model import HealthPredictor

database.init_db()
predictor = HealthPredictor()

# clear old data so emails don't conflict
with database.get_connection() as conn:
    conn.execute("DELETE FROM patients")
    conn.commit()

# a good spread of patients covering low, moderate, and high risk profiles
sample_patients = [
    {
        "full_name": "Eleanor Vance",
        "dob": "1994-08-12",
        "gender": "Female",
        "email": "eleanor.vance@hospital.org",
        "glucose": 88.5,
        "haemoglobin": 13.9,
        "cholesterol": 178.0
    },
    {
        "full_name": "Marcus Chen",
        "dob": "1982-11-04",
        "gender": "Male",
        "email": "m.chen@medcenter.com",
        "glucose": 162.0,
        "haemoglobin": 14.1,
        "cholesterol": 195.0
    },
    {
        "full_name": "Sarah Jenkins",
        "dob": "1975-03-22",
        "gender": "Female",
        "email": "s.jenkins@clinic.net",
        "glucose": 92.0,
        "haemoglobin": 9.2,
        "cholesterol": 210.0
    },
    {
        "full_name": "David Miller",
        "dob": "1968-07-15",
        "gender": "Male",
        "email": "d.miller@healthcare.io",
        "glucose": 112.0,
        "haemoglobin": 13.2,
        "cholesterol": 224.0
    },
    {
        "full_name": "Amina Al-Mansoor",
        "dob": "1989-05-30",
        "gender": "Female",
        "email": "amina.m@regional-med.org",
        "glucose": 145.0,
        "haemoglobin": 10.5,
        "cholesterol": 268.0
    },
    {
        "full_name": "Raj Patel",
        "dob": "1991-12-18",
        "gender": "Male",
        "email": "raj.patel@vitahealth.com",
        "glucose": 78.0,
        "haemoglobin": 15.2,
        "cholesterol": 165.0
    },
    {
        "full_name": "Olivia Thompson",
        "dob": "2000-04-09",
        "gender": "Female",
        "email": "olivia.t@wellcare.org",
        "glucose": 105.0,
        "haemoglobin": 12.8,
        "cholesterol": 201.0
    },
    {
        "full_name": "James O'Brien",
        "dob": "1972-09-27",
        "gender": "Male",
        "email": "j.obrien@medlink.net",
        "glucose": 198.0,
        "haemoglobin": 11.4,
        "cholesterol": 252.0
    },
]

print("Seeding database with sample patients...")

for p in sample_patients:
    pred = predictor.predict(p["glucose"], p["haemoglobin"], p["cholesterol"], p["dob"], p["gender"])

    database.create_patient(
        full_name=p["full_name"],
        dob=p["dob"],
        gender=p["gender"],
        email=p["email"],
        glucose=p["glucose"],
        haemoglobin=p["haemoglobin"],
        cholesterol=p["cholesterol"],
        remarks=pred["remarks"]
    )
    print(f"  Added: {p['full_name']} ({p['gender']}) -> {pred['risk_level']} risk")

print(f"\nDone! {len(sample_patients)} patients seeded into the database.")
