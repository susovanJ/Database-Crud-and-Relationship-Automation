# AI Database Assistant with OpenAI Function Calling

An AI-powered database assistant that allows users to interact with a SQLite database using natural language.

The assistant understands requests such as:

* Add students or courses
* Update student, course, or enrollment records
* Delete individual records
* Delete all records when explicitly requested
* Search and display database information
* Enroll students into courses
* Check a student's enrolled courses

The project uses the OpenAI Responses API with function calling to convert natural-language requests into SQL queries and execute those queries against a SQLite database.

## Features

### Student Management

The assistant can:

* Insert one or multiple students
* Search for students
* Update a student when the student ID is provided
* Delete a specific student
* Delete all students when explicitly requested
* Automatically use database-generated student IDs

### Course Management

The assistant supports:

* Adding courses
* Searching for courses
* Updating courses
* Deleting individual courses
* Deleting all courses when explicitly requested

### Enrollment Management

Students can be enrolled in courses using either names or IDs.

For example:

```text
YOU: Enroll Rahul in Python
```

The assistant will:

1. Find Rahul's `stu_id`
2. Find the Python course's `course_id`
3. Check whether Rahul is already enrolled
4. Insert the enrollment if necessary
5. Set the enrollment status to `ACTIVE`

A successful enrollment returns:

```text
Enrollment successful. Status: ACTIVE.
```

The assistant also prevents duplicate enrollments.

## Database Structure

The project works with three tables.

### `student`

```text
stu_id
name
email
phone
DOB
```

### `course`

```text
course_id
course_name
fees
```

### `enroll_stu`

```text
en_id
student_id
course_id
status
```

The relationships are:

```text
student.stu_id
       ↓
enroll_stu.student_id

course.course_id
       ↓
enroll_stu.course_id
```

## How It Works

The application follows this workflow:

```text
User
  ↓
Natural-language request
  ↓
OpenAI Responses API
  ↓
AI determines required SQL operation
  ↓
Function call: execquery()
  ↓
SQLite database
  ↓
Database result
  ↓
OpenAI
  ↓
Final response
```

The database result is returned to the model through a `function_call_output`, allowing the model to generate the final response using the actual database result.

## SQL Rules

The assistant follows explicit database rules.

For example:

* It must not invent student IDs.
* It must not invent course IDs.
* It must not invent enrollment IDs.
* It must query the database when an ID is required.
* Student INSERT requests only perform the requested INSERT.
* Course INSERT requests only perform the requested INSERT.
* UPDATE requests only perform UPDATE.
* Individual DELETE requests never delete all records.
* Enrollment is not created if the student does not exist.
* Enrollment is not created if the course does not exist.
* Duplicate enrollments are not created.
* Unrelated questions return:

```text
I don't know
```

## Technologies Used

* Python
* OpenAI API
* OpenAI Responses API
* Function Calling
* SQLite
* `python-dotenv`
* JSON

## Project Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

### 2. Install dependencies

```bash
pip install openai python-dotenv
```

### 3. Configure the OpenAI API key

Create a `.env` file in the project directory:

```env
OPENAI_API_KEY=your_api_key_here
```

Do not commit the `.env` file to GitHub.

Add the following to `.gitignore`:

```text
.env
```

### 4. Configure the database path

The application uses a SQLite database file.

Set the database path in the Python code according to the location of your database:

```python
DATABASE_PATH = "path/to/your/database.sqlite3"
```

For example:

```python
con = sqlite3.connect(DATABASE_PATH)
```

This allows each user to provide their own local database path instead of depending on a specific computer or folder structure.

### 5. Prepare the database

The SQLite database should contain these tables:

```text
student
course
enroll_stu
```

### 6. Run the application

```bash
python main.py
```

Then interact with the assistant:

```text
YOU: Show all students
```

## Example Interaction

```text
YOU: Add a course named Python with fees 5000

SQL: INSERT INTO course (course_name, fees)
     VALUES ('Python', 5000)

DATABASE: Query executed successfully

AGENT: Course added successfully.
```

Enrollment example:

```text
YOU: Enroll Rahul in Python

SQL: SELECT stu_id FROM student WHERE name = 'Rahul';

DATABASE: [(1,)]

SQL: SELECT course_id FROM course WHERE course_name = 'Python';

DATABASE: [(2,)]

SQL: INSERT INTO enroll_stu
     (student_id, course_id, status)
     VALUES (1, 2, 'ACTIVE');

DATABASE: Query executed successfully

AGENT: Enrollment successful. Status: ACTIVE.
```

## Architecture

The AI does not directly access the SQLite database.

Instead, the model has access to a controlled Python function:

```python
execquery(query)
```

The architecture is:

```text
AI
 ↓
Function Calling
 ↓
Python
 ↓
SQLite
 ↓
Database Result
 ↓
AI
 ↓
User
```

## Project Goal

The goal of this project is to demonstrate how an AI agent can interact with a real SQLite database using natural-language instructions and OpenAI function calling while following explicit database business rules.

This project combines:

**LLM + Function Calling + Python + SQL + SQLite**
