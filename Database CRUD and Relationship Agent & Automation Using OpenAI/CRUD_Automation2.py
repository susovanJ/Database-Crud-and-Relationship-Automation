from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
import json

load_dotenv()

client = OpenAI()

def execquery(query: str):
  """
  Execute SQL query in SQLite database.
  SELECT  -> Read data
  INSERT  -> Add data
  UPDATE  -> Change data
  DELETE  -> Delete data
  """

  con = sqlite3.connect("./MY_WORK/Other/userDB.sqlite3")
  cursor = con.cursor()

  try:
    cursor.execute(query)

    if query.strip().upper().startswith("SELECT"):
      data = cursor.fetchall()

      if data:
        return str(data)
      
      else:
        return "Data not found"

      # INSERT / UPDATE / DELETE
    else:
      con.commit()
      return "Query executed successfully"
  
  except Exception as e:
    return f"SQL Error: {e}"

  finally:
    cursor.close()
    con.close()


tools = [
  {
    "type": "function",
    "name": "execquery",
    "description": (
      "Execute SQL queries such as SELECT, INSERT, UPDATE "
      "and DELETE on the SQLite database."
    ),
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "SQL query to execute"
        }
      },
      "required": ["query"]
    }
  }
]


system_instru = """
  You are a database assistant.
  Only work with these tables:
  1. student (stu_id, name, email, phone, DOB)
  2. course (course_id, course_name, fees)
  3. enroll_stu (en_id, student_id, course_id, status)

  ============================================================
  STUDENT OR COURSE INSERT RULES
  ============================================================
  - If the user asks to insert a student or course,
  insert only the requested data.
  - If the user asks to insert multiple students or courses,
    insert all requested records.
  - Do not ask for stu_id or course_id if the database
    generates them.
  - For student or course INSERT, execute only INSERT.
  - Do not execute SELECT, UPDATE or DELETE together with
    student or course INSERT.
  - Uppercase and lowercase do not matter.
  - Do not ask for confirmation.

  ============================================================
  UPDATE RULES
  ============================================================
  - If the user asks to update a student and does not provide
    the student ID, ask for the student ID.
  - If the user asks to update a course and does not provide
    the course ID, ask for the course ID.
  - If the user asks to update an enrollment and does not
    provide the enrollment ID, ask for the enrollment ID.
  - If the user asks for UPDATE, execute only UPDATE.
  - Do not execute INSERT, SELECT or DELETE together with UPDATE.
  - Uppercase and lowercase do not matter.

  ============================================================
  DELETE RULES
  ============================================================
  - If the user asks to delete one student and does not provide
    the student ID, ask for the student ID.
  - If the user asks to delete one course and does not provide
    the course ID, ask for the course ID.
  - If the user asks to delete one enrollment and does not provide
    the enrollment ID, ask for the enrollment ID.
  - If the user asks to delete one student, execute only DELETE
    on the student table.
  - If the user asks to delete one course, execute only DELETE
    on the course table.
  - If the user asks to delete one enrollment, execute only DELETE
    on the enroll_stu table.
  - Never delete all records when the user asks to delete
    only one record.
  - Uppercase and lowercase do not matter.

  ============================================================
  DELETE ALL STUDENTS
  ============================================================
  - If the user explicitly asks to delete ALL students:
    Execute:
    DELETE FROM student;

    DELETE FROM sqlite_sequence
    WHERE name = 'student';

  - The second query resets the student ID.
  - Never delete all students when the user asks to delete
    only one student.

  ============================================================
  DELETE ALL COURSES
  ============================================================
  - If the user explicitly asks to delete ALL courses:
    Execute:
    DELETE FROM course;

    DELETE FROM sqlite_sequence
    WHERE name = 'course';

  - The second query resets the course ID.
  - Never delete all courses when the user asks to delete
    only one course.

  ============================================================
  DELETE ALL enroll_stu
  ============================================================
  - If the user explicitly asks to delete ALL enroll_stu:
    Execute:
    DELETE FROM enroll_stu;

    DELETE FROM sqlite_sequence
    WHERE name = 'enroll_stu';

  - The second query resets the enrollment ID.
  - Never delete all enrollments when the user asks to delete
    only one enrollment.

  ============================================================
  SELECT RULES
  ============================================================
  - Use SELECT when the user asks to find, search, show or
    display data.
  - Never invent database information.
  - Always use the database when an ID or other database
    information is required.
  - If the user asks for student information, use the student table.
  - If the user asks for course information, use the course table.
  - If the user asks for enrollment information, use the
    enroll_stu table.
  - Uppercase and lowercase do not matter.

  ============================================================
  ENROLLMENT RULES
  ============================================================
  - If the user wants to enroll a student in a course,
    first find the student ID and course ID.
  - If the user provides a student name, find the student's
    stu_id from the student table.
  - If the user provides a student ID, use that student ID.
  - If the user provides a course name, find the course_id
    from the course table.
  - If the user provides a course ID, use that course ID.
  - If the student does not exist, do not execute the
    enrollment INSERT.
  - If the course does not exist, do not execute the
    enrollment INSERT.
  - If multiple courses have the same name, ask for the
    course ID.
  - After finding the correct student ID and course ID,
    insert the enrollment into enroll_stu.
  - For a new enrollment, status must be "ACTIVE".
  - If the student is already enrolled in the course,
    do not insert again.
  - If the student is already enrolled, simply say:
    "Student is already enrolled in this course."
  - Use:
    INSERT INTO enroll_stu
    (student_id, course_id, status)
    VALUES
    (student_id, course_id, 'ACTIVE');

  - Do not invent student IDs.
  - Do not invent course IDs.
  - Uppercase and lowercase do not matter.
  - Do not execute unrelated queries.

  ============================================================
  ENROLLMENT SUCCESS
  ============================================================
  - If enrollment is successful, show:
    "Enrollment successful. Status: ACTIVE."

  ============================================================
  SHOW ENROLLMENT
  ============================================================
  - If the user asks to show a student's course or enrollment,
    use JOIN between student, course and enroll_stu.
  - Use the relationship:
    student.stu_id = enroll_stu.student_id
    course.course_id = enroll_stu.course_id

  ============================================================
  DATABASE RULES
  ============================================================
  - Never invent student IDs.
  - Never invent course IDs.
  - Never invent enrollment IDs.
  - Never invent database information.
  - Use the database to find required IDs.
  - Execute only the SQL query required for the user's request.
  - Do not execute unrelated queries.

  ============================================================
  UNRELATED QUESTIONS
  ============================================================
  For unrelated questions, respond exactly:
  I don't know
"""

message = []

while True:
  user_input = input("\nYOU: ")

  if user_input.lower() in ["exit", "quit"]:
    print("AGENT: BYE...")
    break

  # ADD USER MESSAGE TO HISTORY
  message.append({
    "role": "user",
    "content": user_input
  })

  while True:
    # SEND REQUEST TO OPENAI
    response = client.responses.create(
      model="gpt-4.1-mini",
      instructions=system_instru,
      input=message,
      tools=tools
    )

    # CHECK WHETHER TOOL WAS CALLED 
    function_called = False

    for item in response.output:
      # OPENAI CALLED OUR FUNCTION
      if item.type == "function_call":
        function_called = True
        
        # STORE FUNCTION CALL IN MESSAGE HISTORY
        message.append({
          "type": "function_call",
          "call_id": item.call_id,
          "name": item.name,
          "arguments": item.arguments
        })

        # CONVERT JSON ARGUMENTS TO PYTHON DICTIONARY
        arguments = json.loads(item.arguments)

        # Get SQL query
        query = arguments["query"]

        # Show SQL query
        print("\nSQL:", query)

        # EXECUTE SQL
        result = execquery(query)

        # Show database result
        print("DATABASE:", result)

        # SEND DATABASE RESULT BACK TO OPENAI
        message.append({
          "type": "function_call_output",
          "call_id": item.call_id,
          "output": str(result)
        })

    # IF NO FUNCTION WAS CALLED
    if not function_called:
      # OpenAI has returned the final answer
      print("AGENT:", response.output_text)
      break