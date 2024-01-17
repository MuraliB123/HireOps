from flask import Flask, json, render_template, request, session
from flask import jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL, create_engine
from sqlalchemy import text as sql_text
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
app = Flask(__name__, static_folder='static')
app.secret_key = 'mykey'
engine = create_engine('mysql+pymysql://root:new_password@localhost/HIREOPS',execution_options={"isolation_level": "AUTOCOMMIT"})
Session = sessionmaker(bind=engine)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:new_password@localhost/HIREOPS'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
from models import Employees,db,skills,EmployeeDetails,Task
db.init_app(app)

def fetch_employee_details(employee_ids):
    employee_details = EmployeeDetails.query.filter(EmployeeDetails.EMPLOYEE_ID.in_(employee_ids)).all()
    return employee_details

@app.route('/')
def  index():
    return render_template('hiring_input.html')

@app.template_filter('custom_title')
def custom_title(value):
    return ', '.join(word.strip().capitalize() for word in value.split(','))

@app.route('/profile/<int:employee_id>')
def profile(employee_id):
    employee_details = EmployeeDetails.query.filter_by(EMPLOYEE_ID=employee_id).first() 
    Skills = skills.query.filter_by(employee_id=employee_id).first()
    tasks = Task.query.filter_by(EMPLOYEE_ID=employee_id).all()
    return render_template('profile.html', employee_details=employee_details, skills=Skills,tasks=tasks)
  
   
@app.route('/fryde', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        project_name = request.form.get('projectName')
        project_id = request.form.get('projectID')
        requirements = request.form.get('requirements')
        query = "SELECT * FROM skills"
        df = pd.read_sql_query(con=engine.connect(),sql=sql_text(query))
        df['SKILLS'] = df['SKILLS'].apply(lambda x: ' '.join(str(x).split(',')))
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['SKILLS'])
        input_vector = tfidf_vectorizer.transform([requirements])
        cosine_similarities = linear_kernel(input_vector, tfidf_matrix).flatten()
        similar_employees = [(df['employee_id'][i], similarity) for i, similarity in enumerate(cosine_similarities) if similarity > 0.35]
        similar_employees = sorted(similar_employees, key=lambda x: x[1], reverse=True)
     
        similar_employee_ids = [emp_id for emp_id, _ in similar_employees]
        similar_employee_details = fetch_employee_details(similar_employee_ids)
        return render_template("score.html", similar_employee_details=similar_employee_details)
    else:
        return render_template("index.html")

@app.route('/json', methods=['GET', 'POST'])
def file_json():
    if request.method == 'POST':       
        uploaded_file = request.files['jsonFile']
        if uploaded_file and uploaded_file.filename.endswith('.json'):
            json_data = uploaded_file.read()
            data = json.loads(json_data)
            requirements = data.get('requirements', [])
            query = "SELECT * FROM skills"
            df = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
            df['SKILLS'] = df['SKILLS'].apply(lambda x: ' '.join(map(str, x)) if isinstance(x, list) else str(x))
            tfidf_vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf_vectorizer.fit_transform(df['SKILLS'])
            input_vector = tfidf_vectorizer.transform([' '.join(requirements)])
            cosine_similarities = linear_kernel(input_vector, tfidf_matrix).flatten()
            similar_employees = [(df['employee_id'][i], similarity) for i, similarity in enumerate(cosine_similarities) if similarity > 0.35]
            similar_employees = sorted(similar_employees, key=lambda x: x[1], reverse=True)
            similar_employee_ids = [emp_id for emp_id, _ in similar_employees]
            similar_employee_details = fetch_employee_details(similar_employee_ids)
        return render_template("score.html", similar_employee_details=similar_employee_details)
    else:
        return render_template("index.html")



if __name__ == '__main__':
    app.run(debug=True)