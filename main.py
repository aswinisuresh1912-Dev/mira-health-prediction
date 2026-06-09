import datetime
import os
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import database
from ml_model import HealthPredictor

database.init_db()
predictor = HealthPredictor()

app = FastAPI(
    title="MIRA Health Prediction Application",
    description="Backend API for storing patient records and predicting health conditions.",
    version="1.0.0"
)

class PatientCreate(BaseModel):
    full_name: str = Field(..., min_length=1)
    dob: str
    gender: str
    email: str
    glucose: float
    haemoglobin: float
    cholesterol: float

class PatientUpdate(BaseModel):
    full_name: str = Field(..., min_length=1)
    dob: str
    gender: str
    email: str
    glucose: float
    haemoglobin: float
    cholesterol: float

def validate_input(full_name: str, dob: str, gender: str, email: str, glucose: float, haemoglobin: float, cholesterol: float):
    if not full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required.")
        
    if not gender or gender.strip().capitalize() not in ["Male", "Female", "Other"]:
        raise HTTPException(status_code=400, detail="Gender must be Male, Female, or Other.")

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
        
    try:
        dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        if dob_date > datetime.date.today():
            raise HTTPException(status_code=400, detail="Date of birth cannot be in the future.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date of birth must be in YYYY-MM-DD format.")
        
    try:
        g = float(glucose)
        h = float(haemoglobin)
        c = float(cholesterol)
        if g <= 0 or h <= 0 or c <= 0:
            raise HTTPException(status_code=400, detail="Glucose, Haemoglobin, and Cholesterol must be positive numbers.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Blood test metrics must be numeric values.")

@app.get("/api/patients")
def read_patients():
    try:
        return database.get_all_patients()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/patients/{patient_id}")
def read_patient(patient_id: int):
    patient = database.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found.")
    return patient

@app.post("/api/patients", status_code=status.HTTP_201_CREATED)
def create_patient_record(patient: PatientCreate):
    validate_input(
        patient.full_name, 
        patient.dob, 
        patient.gender,
        patient.email, 
        patient.glucose, 
        patient.haemoglobin, 
        patient.cholesterol
    )
    
    prediction = predictor.predict(
        patient.glucose, 
        patient.haemoglobin, 
        patient.cholesterol, 
        patient.dob,
        patient.gender
    )
    remarks = prediction["remarks"]
    
    try:
        created = database.create_patient(
            full_name=patient.full_name,
            dob=patient.dob,
            gender=patient.gender,
            email=patient.email,
            glucose=patient.glucose,
            haemoglobin=patient.haemoglobin,
            cholesterol=patient.cholesterol,
            remarks=remarks
        )
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create record: {str(e)}")

@app.put("/api/patients/{patient_id}")
def update_patient_record(patient_id: int, patient: PatientUpdate):
    validate_input(
        patient.full_name, 
        patient.dob, 
        patient.gender,
        patient.email, 
        patient.glucose, 
        patient.haemoglobin, 
        patient.cholesterol
    )
    
    prediction = predictor.predict(
        patient.glucose, 
        patient.haemoglobin, 
        patient.cholesterol, 
        patient.dob,
        patient.gender
    )
    remarks = prediction["remarks"]
    
    try:
        updated = database.update_patient(
            patient_id=patient_id,
            full_name=patient.full_name,
            dob=patient.dob,
            gender=patient.gender,
            email=patient.email,
            glucose=patient.glucose,
            haemoglobin=patient.haemoglobin,
            cholesterol=patient.cholesterol,
            remarks=remarks
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Patient record not found.")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update record: {str(e)}")

@app.delete("/api/patients/{patient_id}")
def delete_patient_record(patient_id: int):
    deleted = database.delete_patient(patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient record not found.")
    return {"message": f"Patient record {patient_id} successfully deleted."}

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "MIRA Health Prediction Application API Running. Front-end files not found."}
