from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import date

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="attendance_system"
)

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def login():
    return render_template("login.html")


# ---------------- LOGIN CHECK ----------------
@app.route('/login', methods=['POST'])
def check_login():

    email = request.form['email']
    password = request.form['password']

    cursor = db.cursor()

    query = "SELECT * FROM teachers WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))

    result = cursor.fetchone()

    if result:
        return redirect("/dashboard")
    else:
        return "Invalid Login"


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


# ---------------- LOAD STUDENTS ----------------
@app.route('/attendance', methods=['POST'])
def attendance():

    class_name = request.form['class']
    year = request.form['year']
    division = request.form['division']

    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM students WHERE class=%s AND year=%s AND division=%s"
    cursor.execute(query, (class_name, year, division))

    students = cursor.fetchall()

    return render_template("attendance.html", students=students)


# ---------------- SAVE ATTENDANCE ----------------
@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():

    cursor = db.cursor()

    for student_id in request.form:

        status = request.form[student_id]

        query = "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)"
        cursor.execute(query, (student_id, date.today(), status))

    db.commit()

    return render_template("success.html")


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin')
def admin():

    cursor = db.cursor(dictionary=True)

    today = date.today()

    # total students
    cursor.execute("SELECT COUNT(*) as total FROM students")
    total = cursor.fetchone()['total']

    # today's absent students list
    query = """
    SELECT students.name
    FROM attendance
    JOIN students ON students.id = attendance.student_id
    WHERE attendance.status='Absent' AND attendance.date=%s
    """

    cursor.execute(query, (today,))
    absent_students = cursor.fetchall()

    return render_template("admin.html", total=total, absent_students=absent_students)


# ---------------- ATTENDANCE REPORT ----------------
@app.route('/report')
def report():

    cursor = db.cursor(dictionary=True)

    query = """
    SELECT students.name,
           SUM(attendance.status='Present') AS present_days,
           COUNT(attendance.id) AS total_days
    FROM attendance
    JOIN students ON students.id = attendance.student_id
    GROUP BY student_id
    """

    cursor.execute(query)

    data = cursor.fetchall()

    for row in data:
        if row['total_days'] > 0:
            row['percentage'] = round((row['present_days'] / row['total_days']) * 100, 2)
        else:
            row['percentage'] = 0

    return render_template("report.html", data=data)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)