from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List
import json


app = FastAPI()

#Basemodel for /post_student_detail API:

class Student(BaseModel):
    student_id:str
    student_name:str
    parent_name:str
    subjects_listed:List[str]
    date_of_birth:str
    




# Function to Create connection with my Database.
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


#Calling function to actually create the DB connection.
try:
    db_connection = get_db_connection()
except Exception as e:
    print(e)
    raise SystemExit("Database connection initialization failed.")



'''API to get details of all the students present inside the database:
Simple read operation from the database.'''
@app.get("/get_students_detail")
async def get_students():
    try:
        with db_connection.cursor() as cur:
            # Execute the query
            cur.execute("SELECT * FROM students")
            students = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            result = [dict(zip(column_names, row)) for row in students]

        return {"students": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    

'''API To Upload Single data of the Students'''
@app.post("/post_student_detail")
async def post_student(student_data:Student):
    try:
        print("!!!!!!!!")
        subjects_listed=json.dumps(student_data.subjects_listed)
        print("sibject_listed:",subjects_listed)
        query=f"INSERT INTO public.students (student_id,student_name,parent_name,subjects_listed,date_of_birth) VALUES('{student_data.student_id}','{student_data.student_name}','{student_data.parent_name}','{subjects_listed}','{student_data.date_of_birth}')"
        print("Query:",query)

        with db_connection.cursor() as cur:
            # Execute the query
            cur.execute(query)
            db_connection.commit()   #We have to commit these changes for making these transaction.
            print("Query Executed")          

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
'''API To Update Student details by student_id'''



@app.put("/update_student_detail")
async def update_student(student_data:Student):
    try:
        print("!!!!!!!!")
        subjects_listed=json.dumps(student_data.subjects_listed)
        print("sibject_listed:",subjects_listed)
        #query=f"INSERT INTO public.students (student_id,student_name,parent_name,subjects_listed,date_of_birth) VALUES('{student_data.student_id}','{student_data.student_name}','{student_data.parent_name}','{subjects_listed}','{student_data.date_of_birth}')"
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

        print("Query:",query)

        with db_connection.cursor() as cur:
            # Execute the query
            cur.execute(query)
            db_connection.commit()   #We have to commit these changes for making these transaction.
            print("Query Executed")          

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    

'''Get Student detail using Subject'''


@app.get("/update_student_detail_by_subject")
async def update_student_detail_by_subject(subject:str):
    try:
        #query=f"INSERT INTO public.students (student_id,student_name,parent_name,subjects_listed,date_of_birth) VALUES('{student_data.student_id}','{student_data.student_name}','{student_data.parent_name}','{subjects_listed}','{student_data.date_of_birth}')"
        query = f"""
    SELECT student_id, student_name
FROM students s 
WHERE subjects_listed::jsonb @> '["{subject}"]'::jsonb;
"""

        print("Query:",query)

        with db_connection.cursor() as cur:
            # Execute the query
            cur.execute(query)
            print("Query Executed")
            students = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            result = [dict(zip(column_names, row)) for row in students]

        return {"students": result}          

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    

'''Get Student detail using Student_id using indexing'''
@app.get("/update_student_detail_by_name_using_indexing")
async def update_student_detail_by_name_using_indexing(subject:str):
    try:
        #query=f"INSERT INTO public.students (student_id,student_name,parent_name,subjects_listed,date_of_birth) VALUES('{student_data.student_id}','{student_data.student_name}','{student_data.parent_name}','{subjects_listed}','{student_data.date_of_birth}')"
        query = f"""
    SELECT *
FROM students s 
WHERE student_name='{subject}';
"""

        print("Query:",query)

        with db_connection.cursor() as cur:
            # Execute the query
            cur.execute(query)
            print("Query Executed")
            students = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            result = [dict(zip(column_names, row)) for row in students]

        return {"students": result}          

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")




