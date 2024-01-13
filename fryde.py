import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel



df = pd.read_csv("/home/murali/Documents/HireOps/skills.csv")


df['SKILLS'] = df['SKILLS'].apply(lambda x: ' '.join(str(x).split(',')))

tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['SKILLS'])

def get_recommendations(required_skills, tfidf_matrix=tfidf_matrix, df=df):
    # Convert required skills into a string
    input_skills = ' '.join(required_skills)

    # Transform input skills using the same TF-IDF vectorizer
    input_vector = tfidf_vectorizer.transform([input_skills])

    # Compute the cosine similarity between input skills and employees' skills
    cosine_similarities = linear_kernel(input_vector, tfidf_matrix).flatten()

    # Sort employees by similarity
    similar_employees = sorted(list(enumerate(cosine_similarities)), key=lambda x: x[1], reverse=True)

    # Print recommended employees
    print("Recommended Employees:")
    for employee_id, similarity in similar_employees:
        print(f"Employee {employee_id + 1} (Similarity: {similarity:.2f})")

# Example: Get recommendations for required skills
required_skills_to_recommend = ["MONGODB","DATABASE MANAGEMENT","DOCKER","KUBERNETES","AWS"]
get_recommendations(required_skills_to_recommend)
