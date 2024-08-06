import shutil
import pdfkit
import pandas as pd
from flask import Flask, abort, redirect, render_template, request, send_from_directory, url_for
import os
from datetime import datetime

app = Flask(__name__)

file_path = 'Report Card - Sheet1.csv'
df = pd.read_csv(file_path)

# Convert DataFrame rows to dictionaries for easier access
students_data = df.to_dict(orient='records')
now = datetime.now()
formatted_date = now.strftime("%m-%d-%y")

@app.route('/')
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
        "exam_final": student_data['Final Exam'],
        "exam_total": student_data['Exam Total'],
        "behavior_mid": student_data['Behavior Mid'],
        "behavior_final": student_data['Behavior Final'],
        "behavior_total": student_data['Behavior Total'],
        "quiz_mid": student_data['Quiz Mid'],
        "quiz_final": student_data['Quiz Final'],
        "quiz_total": student_data['Quiz Total'],
        "homework_mid": student_data['Homework Mid'],
        "homework_final": student_data['Homework Final'],
        "homework_total": student_data['Homework Total'],
        "diary_mid": student_data['Diary Mid'],
        "diary_final": student_data['Diary Final'],
        "diary_total": student_data['Diary Total'],
        "final_grade": student_data['Final Grade'],
        "teacher_comments": student_data['Teacher Comments'],
        "teacher1_name": "sangeeth",
        "teacher2_name": "menachery",
        "date": formatted_date
    }

    # PDF path to save
    pdf_path = f'ReportCards/{name} Report Card.pdf'
    try:
        rendered = render_template("card.html", data=data)
        pdfkit.from_string(rendered, pdf_path)
        print(f"PDF generated and saved at {pdf_path}")
    except Exception as e:
        print(f"PDF generation failed: {e}")

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
    return send_from_directory(os.getcwd(), 'reportcards.zip', as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True)