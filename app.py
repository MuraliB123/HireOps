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
from models import Employees,db,skills
db.init_app(app)


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

        
        return render_template("module1.html", similar_employees=similar_employees)
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
            return render_template("module1.html", similar_employees=similar_employees)
    else:
        return render_template("index.html")



if __name__ == '__main__':
    app.run(debug=True)