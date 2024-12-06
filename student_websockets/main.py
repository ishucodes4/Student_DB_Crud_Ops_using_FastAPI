from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import psycopg2
from typing import List
import json

app = FastAPI()

# BaseModel for /post_student_detail API
class Student(BaseModel):
    student_id: str
    student_name: str
    parent_name: str
    subjects_listed: List[str]
    date_of_birth: str


# WebSocket active connections
active_connections = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def notify_clients(message: str):
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Error sending message to a WebSocket client: {e}")


# Function to create a connection with the database
def get_db_connection():
    try:
        return psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="goluishan",
            host="localhost",
            port="1234",
        )
    except Exception as e:
        raise Exception(f"Could not connect to the database: {e}")


# Initialize the database connection
try:
    db_connection = get_db_connection()
except Exception as e:
    print(e)
    raise SystemExit("Database connection initialization failed.")


# API to get details of all the students
@app.get("/get_students_detail")
async def get_students():
    try:
        with db_connection.cursor() as cur:
            cur.execute("SELECT * FROM students")
            students = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            result = [dict(zip(column_names, row)) for row in students]

        # Notify WebSocket clients
        await notify_clients("All student details fetched.")
        return {"students": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# API to upload single data of a student
@app.post("/post_student_detail")
async def post_student(student_data: Student):
    try:
        subjects_listed = json.dumps(student_data.subjects_listed)
        query = f"""
        INSERT INTO public.students 
        (student_id, student_name, parent_name, subjects_listed, date_of_birth) 
        VALUES ('{student_data.student_id}', '{student_data.student_name}', '{student_data.parent_name}', '{subjects_listed}', '{student_data.date_of_birth}')
        """
        with db_connection.cursor() as cur:
            cur.execute(query)
            db_connection.commit()

        # Notify WebSocket clients
        await notify_clients(f"New student added: {student_data.student_name}")
        return {"message": "Student added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# API to update student details
@app.put("/update_student_detail")
async def update_student(student_data: Student):
    try:
        subjects_listed = json.dumps(student_data.subjects_listed)
        query = f"""
        UPDATE public.students 
        SET 
            student_name = '{student_data.student_name}', 
            parent_name = '{student_data.parent_name}', 
            subjects_listed = '{subjects_listed}', 
            date_of_birth = '{student_data.date_of_birth}' 
        WHERE 
            student_id = '{student_data.student_id}';
        """
        with db_connection.cursor() as cur:
            cur.execute(query)
            db_connection.commit()

        # Notify WebSocket clients
        await notify_clients(f"Student details updated for: {student_data.student_name}")
        return {"message": "Student details updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# API to get student details by subject
@app.get("/get_students_by_subject")
async def get_students_by_subject(subject: str):
    try:
        query = f"""
        SELECT student_id, student_name
        FROM students
        WHERE subjects_listed::jsonb @> '["{subject}"]'::jsonb;
        """
        with db_connection.cursor() as cur:
            cur.execute(query)
            students = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            result = [dict(zip(column_names, row)) for row in students]

        # Notify WebSocket clients
        await notify_clients(f"Fetched students who study {subject}.")
        return {"students": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# API to get student details by name using indexing
@app.get("/get_student_by_name")
async def get_student_by_name(name: str):
    try:
        query = f"""
        SELECT *
        FROM students
        WHERE student_name = '{name}';
        """
        with db_connection.cursor() as cur:
            cur.execute(query)
            students = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            result = [dict(zip(column_names, row)) for row in students]

        # Notify WebSocket clients
        await notify_clients(f"Fetched student details for: {name}.")
        return {"students": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
