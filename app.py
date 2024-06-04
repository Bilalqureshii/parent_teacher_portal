from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import sha256_crypt
import MySQLdb

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Qureshi@123'
app.config['MYSQL_DB'] = 'world'

# Initialize MySQL
mysql = MySQLdb.connect(host=app.config['MYSQL_HOST'],
                        user=app.config['MYSQL_USER'],
                        passwd=app.config['MYSQL_PASSWORD'],
                        db=app.config['MYSQL_DB'])
cursor = mysql.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parent_signup', methods=['GET', 'POST'])
def parent_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # Assuming the password is stored as plain text
        cursor.execute("INSERT INTO parents (email,password) VALUES (%s, %s)", (email,password))
        mysql.commit()
        return redirect(url_for('index'))
    return render_template('parent_signup.html')


@app.route('/teacher_signup', methods=['GET', 'POST'])
def teacher_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # Assuming the password is stored as plain text
        cursor.execute("INSERT INTO teachers (email,password) VALUES (%s,%s)", (email,password))
        mysql.commit()
        return redirect(url_for('index'))
    return render_template('teacher_signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']
        cursor.execute("SELECT * FROM parents WHERE email = %s", [email])
        parent_data = cursor.fetchone()
        if parent_data:
            stored_password = parent_data[2]  # Assuming the password is stored as plain text in the database
            if password_candidate == stored_password:
                session['logged_in'] = True
                session['user_type'] = 'parent'
                session['user_id'] = parent_data[0]
                return redirect(url_for('parent_dashboard'))
            else:
                return "Invalid credentials"
        else:
            cursor.execute("SELECT * FROM teachers WHERE email = %s", [email])
            teacher_data = cursor.fetchone()
            if teacher_data:
                stored_password = teacher_data[2]  # Assuming the password is stored as plain text in the database
                if password_candidate == stored_password:
                    session['logged_in'] = True
                    session['user_type'] = 'teacher'
                    session['user_id'] = teacher_data[0]
                    return redirect(url_for('teacher_dashboard'))
                else:
                    return "Invalid credentials"
            else:
                return "User not found"
    return render_template('signin.html')


@app.route('/parent_dashboard', methods=['GET', 'POST'])
def parent_dashboard():
    if 'logged_in' in session and session['user_type'] == 'parent':
        if request.method == 'POST':
            student_id = request.form['student_id']
            cursor.execute("SELECT * FROM student_progress WHERE student_id = %s", [student_id])
            student_progress = cursor.fetchall()
            return render_template('view_student_progress.html', student_progress=student_progress)
        return render_template('parent_dashboard.html')
    else:
        return redirect(url_for('signin'))

@app.route('/teacher_dashboard', methods=['GET', 'POST'])
def teacher_dashboard():
    if 'logged_in' in session and session['user_type'] == 'teacher':
        if request.method == 'POST':
            student_id = request.form['student_id']
            subject_name = request.form['subject_name']
            student_performance = request.form['student_performance']
            cursor.execute("INSERT INTO student_progress (student_id, subject_name, student_performance) VALUES (%s, %s, %s)", (student_id, subject_name, student_performance))
            mysql.commit()
            return redirect(url_for('teacher_dashboard'))
        return render_template('teacher_dashboard.html')
    else:
        return redirect(url_for('signin'))

@app.route('/view_student_progress', methods=['GET', 'POST'])
def view_student_progress():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        # Fetch student progress data from the database based on the provided student ID
        cursor.execute("SELECT subject_name, student_performance FROM student_progress WHERE student_id = %s", (student_id,))
        student_progress = cursor.fetchall()
        # Pass student progress data to the template
        return render_template('view_student_progress.html', student_progress=student_progress)
    return render_template('view_student_progress.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
