from flask import Flask, flash, render_template, url_for, redirect, request, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func
from sqlalchemy import desc
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tri.db'  # SQLite database for user credentials
app.config['UPLOAD_FOLDER'] = 'static/resumes'  # Folder for uploaded resumes
db = SQLAlchemy(app)
migrate = Migrate(app,db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    contact_no = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(15), nullable=False)
    rskill = db.Column(db.String(100), nullable=False)
    cutoff = db.Column(db.String(200), nullable=False)
    vacancies = db.Column(db.String(200), nullable=False)
    date_of_drive = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    salary_package = db.Column(db.String(20), nullable=False)
    


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    contact_no = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    skill = db.Column(db.String(100), nullable=True)
    student_id = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    year_of_graduation = db.Column(db.String(10), nullable=True)
    cgpa = db.Column(db.String(5), nullable=True)
    sslc = db.Column(db.String(5), nullable=True)
    hsc = db.Column(db.String(5), nullable=True)
    resume_data = db.Column(db.LargeBinary(), nullable=True)
    resume_filename = db.Column(db.String(100), nullable=True)

class ApplyPlacement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(15), nullable=False)
    rskill = db.Column(db.String(100), nullable=False)
    cutoff = db.Column(db.String(200), nullable=False)
    vacancies = db.Column(db.String(200), nullable=False)
    date_of_drive = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    salary_package = db.Column(db.String(20), nullable=False)
    eligibility=db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), nullable=True)  # Nullable string column for status


class UserQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=True)
                  
class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Query the database for the user
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            # Redirect student to student.html upon successful login
            return redirect('/student')
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html', error_message=None)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Retrieve form data
        student_name = request.form['studentName']
        gender = request.form['gender']
        date_of_birth = request.form['dob']
        contact_no = request.form['contactNo']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_message = "Username already exists. Please choose another."
            return render_template('sign_up.html', error_message=error_message)
        else:
            # Create a new user and add it to the database
            new_user = User(username=username, password=password,student_name=student_name)
            db.session.add(new_user)
            db.session.commit()
           
            # Create a new student record and associate it with the user
            new_student = Student(
                student_name=student_name,
                gender=gender,
                date_of_birth=date_of_birth,
                contact_no=contact_no,
                email=email
            )
            db.session.add(new_student)
            db.session.commit()
         

            return redirect('/student-login')
    else:
        return render_template('sign_up.html', error_message=None)



@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        # Retrieve the username from the session
        username = session.get('username')
        if username:
            # Retrieve the existing student record if it exists
            student = Student.query.filter(func.lower(Student.student_name) == func.lower(username)).first()
            if student:
                # Update the existing student record with form data
                student.student_name = request.form['student-name']
                student.gender = request.form['gender']
                student.date_of_birth = request.form['date-of-birth']
                student.contact_no = request.form['contact-no']
                student.email = request.form['email-id']
                student.skill = request.form['skill']
                student.student_id = request.form['student-id']
                student.department = request.form['student-department']
                student.year_of_graduation = request.form['year-graduation']
                student.cgpa = request.form['cgpa']
                student.sslc = request.form['sslc']
                student.hsc = request.form['hsc']
                if 'resume' in request.files:
                    file = request.files['resume']
                    if file.filename != '':
                        # Save the new resume file to static/resumes with a unique name
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        # Update student record with new resume filename and data
                        student.resume_filename = filename
                        with open(file_path, 'rb') as f:
                            student.resume_data = f.read()
                        # Remove the old resume file if it exists
                        if student.resume_filename and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], student.resume_filename)):
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], student.resume_filename))
            else:
                # If the student doesn't exist, create a new student record
                student = Student(
                    student_name=request.form['student-name'],
                    gender=request.form['gender'],
                    date_of_birth=request.form['date-of-birth'],
                    contact_no=request.form['contact-no'],
                    email=request.form['email-id'],
                    skill=request.form['skill'],
                    student_id=request.form['student-id'],
                    department=request.form['student-department'],
                    year_of_graduation=request.form['year-graduation'],
                    cgpa=request.form['cgpa'],
                    sslc=request.form['sslc'],
                    hsc=request.form['hsc'],
                )
                if 'resume' in request.files:
                    file = request.files['resume']
                    if file.filename != '':
                        # Save the new resume file to static/resumes with a unique name
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        # Update student record with new resume filename and data
                        student.resume_filename = filename
                        with open(file_path, 'rb') as f:
                            student.resume_data = f.read()
            db.session.add(student)
            db.session.commit()
            return redirect('/student')
        else:
            # Redirect if user is not logged in
            return redirect('/student-login')
    else:
        # Retrieve the username from the session
        username = session.get('username')
        if username:
            # Query the user first
            user = User.query.filter_by(username=username).first()
            if user:
                # If the user is found, query the student with the same student_name
                student = Student.query.filter(func.lower(Student.student_name) == func.lower(user.student_name)).first()
                if student:
                    return render_template('student.html', username=username, student=student)
                else:
                    # Redirect if no matching student is found
                    return redirect('/student-login')
            else:
                # Redirect if user is not found
                return redirect('/student-login')
        else:
            # Redirect if user is not logged in
            return redirect('/student-login')

        
@app.route('/placement-list')
def placement_list():
    # Retrieve the username from the session
    username = session.get('username')
    if username:
        # Query the placements from the database
        placements = Placement.query.all()
        return render_template('plac_student.html', username=username, placements=placements)
    else:
        return redirect('/student-login')  # Redirect to login if the user is not logged in

@app.route('/applied_placements')
def applied_placements():
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            student_name = user.student_name
            applied_placements = ApplyPlacement.query.filter_by(student_name=student_name).all()
            return render_template('apply_plac.html', username=username, applied_placements=applied_placements)
        else:
            flash("User not found!")
            return redirect('/student-login')
    else:
        flash("Please login first!")
        return redirect('/student-login')



@app.route('/faculty-login', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username and password match predefined credentials
        if username == "admin" and password == "123":
            # Store the logged-in user in session
            session['username'] = username
            return render_template('wel.html', username=username)  # Pass the username to the template
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('admin.html', error_message=error_message)
    else:
        return render_template('admin.html', error_message=None)
    
@app.route('/admin_placements')
def admin_placements():
    username = session.get('username')
    if username:
        if username=='admin':
            applied_placements = ApplyPlacement.query.all()
            return render_template('apply_admin.html', username=username, applied_placements=applied_placements)
        else:
            flash("User not found!")
            return redirect('/faculty-login')
    else:
        flash("Please login first!")
        return redirect('/faculty-login')


@app.route('/welcome')
def welcome():
    return render_template('wel.html')


@app.route('/logout')
def logout():
    # Clear the session data
    session.pop('username', None)
    # Redirect to the index page after logout
    return redirect('/')

@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
    # Retrieve the username from the session
    username = session.get('username')
    if username:
        if request.method == 'POST':
            # Get form data
            company_name = request.form['company-name']
            state = request.form['state']
            city = request.form['city']
            pincode = request.form['pincode']
            district = request.form['district']
            contact_no = request.form['contact-no']
            email = request.form['email-id']
            
            # Create a new company object
            new_company = Company(
                company_name=company_name,
                state=state,
                city=city,
                pincode=pincode,
                district=district,
                contact_no=contact_no,
                email=email
            )
            
            # Add the new company to the database
            db.session.add(new_company)
            db.session.commit()
            
            # Redirect to display_company page
            return redirect('/display_company')
        else:
            return render_template('add_company.html', username=username)
    else:
        return redirect('/faculty-login')  # Redirect to login if the u

@app.route('/add_placement')
def add_placement():
    # Retrieve the username from the session
    username = session.get('username')
    if username:
        return render_template('add_placement.html', username=username)
    else:
        return redirect('/faculty-login')  # Redirect to login if the user is not logged in
    
@app.route('/save_placement', methods=['POST'])
def save_placement():
    print("Form Data:", request.form)
    # Retrieve form data
    company_name = request.form['company-name']
    designation = request.form['designation']
    branch = request.form['branch']
    rskill = request.form['rskill']
    cutoff = request.form['cutoff']
    vacancies = request.form['vacancies']
    # Convert date string to datetime object
    date_of_drive_str = request.form['date-of-drive']
    date_of_drive = datetime.strptime(date_of_drive_str, '%Y-%m-%d').date()
    salary_package = request.form['salary-package']
    
    # Save placement details to the database
    placement = Placement(
        company_name=company_name,
        designation=designation,
        branch=branch,
        rskill=rskill,
        cutoff=cutoff,
        vacancies=vacancies,
        date_of_drive=date_of_drive,  # Provide datetime object
        salary_package=salary_package
    )
    db.session.add(placement)
    db.session.commit()
    
    # Redirect to the display placement page
    return redirect('/display_placement')

@app.route('/company_names')
def get_company_names():
    # Query the database to retrieve company names
    companies = Company.query.with_entities(Company.company_name).all()
    company_names = [company[0] for company in companies]
    return jsonify(company_names)

@app.route('/display_company')
def display_company():
    # Retrieve the username from the session
    username = session.get('username')
    if username:
        # Retrieve company details from the database
        companies = Company.query.all()
        return render_template('display_company.html', username=username, companies=companies)
    else:
        return redirect('/faculty-login')  # Redirect to login if the user is not logged in

@app.route('/student-profile')
def student_profile():
     username = session.get('username')
    # Query student details from the database
     students = Student.query.all()
    # Render the student_profile.html template and pass the student details
     return render_template('student_profile.html', username=username,students=students)


@app.route('/delete_company/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    # Retrieve the username from the session
    username = session.get('username')
    if username:
        # Retrieve company from the database
        company = Company.query.get(company_id)
        if company:
            db.session.delete(company)
            db.session.commit()
    return redirect('/display_company')

@app.route('/delete_placement/<int:placement_id>', methods=['POST'])
def delete_placement(placement_id):
    # Retrieve the username from the session
    username = session.get('username')
    if username:
        # Retrieve placement from the database
        placement = Placement.query.get(placement_id)
        if placement:
            db.session.delete(placement)
            db.session.commit()
    return redirect('/display_placement')


@app.route('/apply_placement/<int:placement_id>', methods=['POST'])
def apply_placement(placement_id):
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            student_name = user.student_name
            placement = Placement.query.get(placement_id)
            student = Student.query.filter_by(student_name=student_name).first()
            if placement:
                # Check if the student has already applied for this placement
                existing_application = ApplyPlacement.query.filter_by(student_name=student_name, company_name=placement.company_name, designation=placement.designation).first()
                if existing_application:
                    flash("You have already applied for this placement.")
                    return redirect('/placement-list')  # Redirect to placement list or wherever appropriate
                else:
                    if float(placement.cutoff) < float(student.cgpa):  # Corrected attribute name from 'students' to 'student'
                        # Create a new applied placement record
                        applied_placement = ApplyPlacement(
                            student_name=student_name,
                            company_name=placement.company_name,
                            designation=placement.designation,
                            branch=placement.branch,
                            rskill=placement.rskill,
                            cutoff=placement.cutoff,
                            vacancies=placement.vacancies,
                            date_of_drive=placement.date_of_drive,
                            salary_package=placement.salary_package,
                            eligibility="Eligible",
                            status="Applied"  # Set the initial status
                        )
                    else:
                        applied_placement = ApplyPlacement(
                            student_name=student_name,
                            company_name=placement.company_name,
                            designation=placement.designation,
                            branch=placement.branch,
                            rskill=placement.rskill,
                            cutoff=placement.cutoff,
                            vacancies=placement.vacancies,
                            date_of_drive=placement.date_of_drive,
                            salary_package=placement.salary_package,
                            eligibility="not eligible",
                            status="Applied"  # Set the initial status
                        )
                    db.session.add(applied_placement)
                    db.session.commit()
                    return redirect('/applied_placements')
            else:
                flash("Placement not found!")
                return redirect('/placement-list')  # Redirect to placement list or wherever appropriate
        else:
            flash("User not found!")
            return redirect('/student-login')
    else:
        flash("Please login first!")
        return redirect('/student-login')


@app.route('/display_placement')
def display_placement():
    # Retrieve the username from the session
    username = session.get('username')
    if username:
         placements = Placement.query.all()
         return render_template('display_placement.html', username=username , placements=placements)
    else:
         return redirect('/faculty-login')  # Redirect to login if the user is not logged in


@app.route('/view-resume/<filename>')
def view_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/notify_company/<int:company_id>', methods=['POST'])
def notify_company(company_id):
    # Retrieve the company from the database
    company = Company.query.get(company_id)
    if company:
        # Save a notification to the database
        notification_message = f"A new company has been added: {company.company_name}"
        notification = Notifications(message=notification_message)
        db.session.add(notification)
        db.session.commit()
        flash("Notification saved successfully!")
    else:
        flash("Company not found!")
    return redirect('/display_company')

@app.route('/notifications')
def notifications():
    username = session.get('username')
    # Retrieve notification messages from the database
    notifications = Notifications.query.all()
    return render_template('admin_notification.html',username=username , notifications=notifications)

@app.route('/stu-notifications')
def stu_notifications():
    username = session.get('username')
    # Retrieve notification messages from the database
    notifications = Notifications.query.all()
    return render_template('stu_notification.html',username=username , notifications=notifications)

@app.route('/update_status/<int:placement_id>', methods=['POST'])
def update_status(placement_id):
    # Retrieve the admin username from the session
    admin_username = session.get('username')
    
    # Check if the admin is logged in and authorized
    if admin_username == 'admin':
        # Retrieve the student name from the request JSON data
        student_name = request.json.get('student_name')
        
        # Retrieve the applied placement from the database based on both placement_id and student_name
        applied_placement = ApplyPlacement.query.filter_by(id=placement_id, student_name=student_name).first()
        
        if applied_placement:
            # Update the status based on the request data
            new_status = request.json.get('status')
            applied_placement.status = new_status
            
            # Commit the changes to the database
            try:
                db.session.commit()
                # Return a JSON response indicating success
                return jsonify({'message': 'Status updated successfully'})
            except Exception as e:
                # Return a JSON response indicating failure
                return jsonify({'error': str(e)}), 500
        else:
            # Return a JSON response indicating failure (placement not found for the student)
            return jsonify({'error': 'Applied placement not found for the current student'}), 404
    else:
        # Return a JSON response indicating failure (admin not logged in or unauthorized)
        return jsonify({'error': 'Unauthorized access'}), 401

@app.route('/statistics')
def statistics():
    username = session.get('username')
    total_companies = Company.query.count()
    total_vacancies = db.session.query(func.sum(Placement.vacancies)).scalar()
    total_students = Student.query.count()
    total_applied_students = ApplyPlacement.query.distinct(ApplyPlacement.student_name).count()
    return render_template('statistics.html', username=username , total_companies=total_companies, total_vacancies=total_vacancies, total_students=total_students, total_applied_students=total_applied_students)


@app.route('/query')
def query():
    username = session.get('username')
    return render_template('submit_query.html',username=username )


@app.route('/submit_query', methods=['POST'])
def submit_query():
    query_text = request.form['query']
    username = session.get('username')  # Assuming you have a way to retrieve the username
    new_query = UserQuery(username=username, text=query_text)
    db.session.add(new_query)
    db.session.commit()
    flash('Query submitted successfully', 'success')
    return redirect('/query')



@app.route('/admin_query')
def admin_query():
    username = session.get('username')
    submitted_queries = UserQuery.query.all()
    return render_template('admin_query.html', username=username ,submitted_queries=submitted_queries)

@app.route('/delete_query/<int:query_id>', methods=['POST'])
def delete_query(query_id):
    query = UserQuery.query.get_or_404(query_id)
    db.session.delete(query)
    db.session.commit()
    return redirect(url_for('admin_query'))

@app.route('/reply_query/<int:query_id>', methods=['POST'])
def reply_query(query_id):
    query = UserQuery.query.get_or_404(query_id)
    if request.method == 'POST':
        reply_text = request.form['reply']
        query.reply = reply_text
        db.session.commit()
        flash('Reply sent successfully', 'success')
    return redirect(url_for('admin_query'))


@app.route('/faq')
def faq():
    username = session.get('username')
    return render_template('faq.html', username=username)



if __name__ == "__main__":      
     app.run(debug=True)