# MIRA — Medical Intelligence Robotic Automation

MIRA is a lightweight full-stack dashboard I built to manage basic patient records and run simple clinical risk scoring on blood markers in real time. 

The main goal was to create a clean, single-page dashboard where a user can perform full CRUD operations on patient records, while a custom backend math engine dynamically evaluates risk boundaries on the fly.

## What it Does
* **Complete CRUD Registry:** You can register new patients, pull up the whole registry table, edit specific clinical values, or delete old rows.
* **Continuous Risk Calculation:** Instead of using basic if/else limits, the app measures how far metrics move away from healthy clinical bounds.
* **Sigmoid Probability Mapping:** It runs the total variance through a standard logistic sigmoid function to generate a 0–100% confidence score for the clinical notes.
* **Dynamic Dark-Theme Front-end:** Built as an interactive single-page app (SPA) using vanilla JavaScript Fetch utilities to swap data with the API smoothly without annoying page reloads.

## The Tech Stack
* **Backend Framework:** FastAPI (Python)
* **Database:** SQLite3 (Native driver with custom context isolation)
* **Frontend:** Clean HTML5, Custom CSS, Vanilla JavaScript (ES6), FontAwesome
* **Testing:** Python `unittest` suite

## File Structure & Organization
* `main.py` — Sets up the FastAPI engine, request schemas, and core endpoint controllers.
* `database.py` — Handles connection pools using context managers to prevent SQLite file locks.
* `ml_model.py` — Houses the threshold metrics, age calculations, and the sigmoid scoring formula.
* `seed.py` — A quick utility script to populate the database with diverse mock profiles for testing.
* `test_api.py` — Unit testing pipeline that safely targets an isolated, short-lived memory database.
* `/static` — Holds all front-end assets (`index.html`, `style.css`, and `app.js`).

## Running the App on Your Machine

1. Make sure you have your dependencies installed:
   pip install fastapi uvicorn
2. Run the seeding script to spin up the schema and insert mock data:
   python seed.py
3. Fire up the local Uvicorn development server:
   uvicorn main:app --reload
4. Open your browser and navigate to:
   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
---


