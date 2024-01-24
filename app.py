from flask import Flask, json, render_template, request, session
from flask import jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL, create_engine
from sqlalchemy import text as sql_text
import pandas as pd
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
app = Flask(__name__, static_folder='static')
CORS(app)
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

@app.route('/forecast',methods=['GET','POST'])
def get_input():
    if request.method == 'POST':
        upload_file = request.files['jsonfile']
        if upload_file and upload_file.filename.endswith('.json'):
            json_data = upload_file.read()
            data = json.loads(json_data)
            data_0 = data.get('EmployeeTurnoverRate')
            data_1 = data.get('EmployeeRetentionRate')
            data_2 = data.get('OrganisationExpansionIndex')
            data_3 = data.get('NumberOfLargeScaleProjects')
            data_4 = data.get('NumberOfMediumAndSmallScaleProjects')
            data_7 = data.get('NIFTYIT')
            data_8 = data.get('GDP')
            data_9 = data.get('GrossProfitMargin')
            data_10 = data.get('WorkingCapital')
            data_11 = data.get('QuickRatio')
            data_12 = data.get('ReturnOnEquity')
            data_to_predict = [[data_0, data_1, data_2, data_3, data_4,data_7, data_8, data_9, data_10, data_11, data_12]]
            dataset = pd.read_csv("/home/murali/Documents/HireOps/forecast_hiring - Sheet1(1).csv")
            Y = dataset['Candidates Hired']
            X = dataset.drop("Candidates Hired",axis=1)
            #Model1
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor()
            model.fit(X,Y)
            predicted_candidates_hired_1 = model.predict(data_to_predict)
            #Model2
            from sklearn.neighbors import KNeighborsRegressor
            knn_model = KNeighborsRegressor(n_neighbors=3)  
            knn_model.fit(X,Y)
            predicted_candidates_hired_2 = knn_model.predict(data_to_predict)
            #time series analysis
            df = pd.DataFrame({'Value':Y})
            df['Value_diff'] = df['Value'].diff()
            df['Value_diff_abs'] = df['Value_diff'].abs()
            df = df.dropna()
            model = ARIMA(Y, order=(1, 0, 0))
            model = model.fit()
            forecast_steps = 4  
            forecast_results = model.get_forecast(steps=forecast_steps)
            forecast_values = forecast_results.predicted_mean
            plt.plot(Y, label='Original Time Series', color='blue')
            plt.plot(range(len(Y), len(Y) + forecast_steps), forecast_values, label='Forecasted Values', color='red')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.title('ARIMA Forecasting')
            plt.legend()
            plt.savefig('static/forecast_plot.png')  
            plt.close()
            return render_template("final_result.html",prediction=(predicted_candidates_hired_1+predicted_candidates_hired_2)/2)


if __name__ == '__main__':
    app.run(host='127.0.0.0', port=5000, debug=True)