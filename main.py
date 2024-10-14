import shutil
import pdfkit
import pandas as pd
from flask import Flask, abort, redirect, render_template, request, send_from_directory, url_for, flash, after_this_request
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_mail import Mail, Message
from sqlalchemy import text
import os
from datetime import datetime



from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy #Access sql through python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import LoginForm, RegisterForm




app = Flask(__name__)
#os.environ.get('FLASK_KEY')
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C06K56b"
ckeditor = CKEditor(app)
Bootstrap(app)

file_path = 'Mid-Data.csv'
df = pd.read_csv(file_path)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('mail_account')
app.config['MAIL_PASSWORD'] = os.environ.get('mail_pass')
app.config['MAIL_DEFAULT_SENDER'] = 'schery004@gmail.com'

mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

with app.app_context():
    db.create_all()

# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = db.session.execute(text("Select email from users"))

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        result = db.session.execute(text("select email from users"))
        for email in result:
            print(email)
            
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash("Incorrect Password, please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Convert DataFrame rows to dictionaries for easier access
students_data = df.to_dict(orient='records')
now = datetime.now()
formatted_date = now.strftime("%m-%d-%y")

login_manager.login_view = 'login'

@app.route('/')
@login_required
def home():
    return render_template("index.html")

def convert_html_to_pdf():
    for name in df["First Name"]:
        with app.test_request_context():
            generate_pdf(name)

@app.route('/generate_pdf/<name>')
def generate_pdf(name):
    # Find the student data by namet
    try:
        student_data = next(item for item in students_data if item['First Name'] == name)
    except StopIteration:
        abort(404, description="Student not found")



    # Extract relevant data from the student_data
    data = {
        "name": f"{student_data['First Name']} {student_data['Last Name']}",
        "mid_term_exam": student_data['Mid-Term Exam'],
        # "exam_final": student_data['Final Exam'],
        # "exam_total": student_data['Exam Total'],
        "behavior_mid": student_data['Behavior Mid'],
        # "behavior_final": student_data['Behavior Final'],
        # "behavior_total": student_data['Behavior Total'],
        "quiz_mid": student_data['Quiz Mid'],
        # "quiz_final": student_data['Quiz Final'],
        # "quiz_total": student_data['Quiz Total'],
        "homework_mid": student_data['Homework Mid'],
        # "homework_final": student_data['Homework Final'],
        # "homework_total": student_data['Homework Total'],
        "diary_mid": student_data['Diary Mid'],
        # "diary_final": student_data['Diary Final'],
        # "diary_total": student_data['Diary Total'],
        "final_grade": student_data['Final Grade'],
        "teacher_comments": student_data['Teacher Comments'],
        "teacher1_name": student_data['Teacher1Name'],
        "teacher2_name": student_data['Teacher2Name'],
        "grade":student_data["Grade"],
        "date": formatted_date,
        "email": student_data["Parent Email"]
    }

    # PDF path to save
    pdf_path = f'ReportCards/{name} Report Card.pdf'
    try:
        rendered = render_template("midCard.html", data=data)
        pdfkit.from_string(rendered, pdf_path)
        print(f"PDF generated and saved at {pdf_path}")

        # Send an email if there's a parent email
        emails = data['email']
        parent_email = [email.strip() for email in emails.split(",")]
        if parent_email:
            send_email(parent_email, pdf_path, data)
            print(f"Email sent to {parent_email}")

    except Exception as e:
        print(f"PDF generation failed: {e}")

def send_email(to, pdf_path, data):
    subject = f"CCD Report Card for {data['name']}"
    body = f"Dear Parent,\n\nPlease find attached the report card for your child, {data['name']}.\n\nBest regards,\nFaith Formation Team\nSt. Thomas Syro Malabar Forane Catholic Church"
    msg = Message(
    subject=subject,
    recipients=to,
    body=body
    )
    with app.open_resource(pdf_path) as card:
        msg.attach(f"{data['name']} Report Card.pdf", "application/pdf", card.read())
    mail.send(msg)


@app.route("/upload", methods=["POST"])
def upload():
    global file_path,df, students_data
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == '':
        return redirect(request.url)
    if file:
        file.save(f"Uploads/{file.filename}")   
        file_path = f"Uploads/{file.filename}"
        df = pd.read_csv(file_path)
        students_data = df.to_dict(orient='records')  # Update the global students_data
    convert_html_to_pdf()
    return redirect(url_for('home'))
        
@app.route('/download')
def download_file():
    if not os.path.exists("ReportCards"):
            abort(404, description="Directory not found")

        # Compress the directory into a ZIP file
    shutil.make_archive('reportcards', 'zip', "ReportCards")
        
        # Serve the ZIP file
    response =  send_from_directory(os.getcwd(), 'reportcards.zip', as_attachment=True)

    @after_this_request
    def remove_report_cards(response):
        global file_path
        for filename in os.listdir("ReportCards"):
            file_paths = os.path.join("ReportCards", filename)
            try:
                if os.path.isfile(file_paths) and filename != "Thanks.txt":
                    os.remove(file_paths)  # Remove the file
            except Exception as e:
                print(f'Failed to delete {file_paths}. Reason: {e}')
        if os.path.isfile(file_path):
            os.remove(file_path)
        return response
        

    return response


@app.route('/downloadex')
def download_example():
    if not os.path.exists("Example"):
            abort(404, description="Directory not found")

        # Compress the directory into a ZIP file
    shutil.make_archive('example', 'zip', "Example")
        
        # Serve the ZIP file
    return send_from_directory(os.getcwd(), 'example.zip', as_attachment=True)




@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=False)