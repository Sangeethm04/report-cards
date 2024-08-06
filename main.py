import pdfkit
import pandas as pd
from flask import Flask, render_template
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

@app.route('/generate_pdf')
def generate_pdf(name):
    # Find the student data by name
    student_data = next(item for item in students_data if item['First Name'] == name)

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

# @app.route('/download/<filename>')
# def download_file(filename):
#     return send_from_directory('ReportCards', filename)


def convert_html_to_pdf():
    for name in df["First Name"]:
        with app.test_request_context():
            generate_pdf(name)

if __name__ == '__main__':
    if not os.path.exists('ReportCards'):
        os.makedirs('ReportCards')
    convert_html_to_pdf()
    app.run(debug=True)


# HTML content



if __name__ == '__main__':
    app.run(debug=True, port=5002)
    if not os.path.exists('ReportCards'):
        os.makedirs('ReportCards')
    generate_pdf()