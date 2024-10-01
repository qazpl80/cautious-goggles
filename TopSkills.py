import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from Cleandata import clean_job_descriptions # Importing the cleaning function

# Define a list of IT skills
IT_SKILLS = {
    'python', 'java', 'c#', 'javascript', 'html', 'css', 'sql', 'linux', 'devops',
    'machine learning', 'data analysis', 'cloud computing', 'react', 'angular',
    'typescript', 'git', 'docker', 'kubernetes', 'agile', 'scrum', 'database',
    'networking', 'cybersecurity', 'artificial intelligence', 'web development',
    'mobile development', 'api', 'software development', 'big data', 'data science'
}

def extract_top_skills(cleaned_descriptions, top_n=20):
    """Extracts the top N IT skills mentioned in the job descriptions using TF-IDF."""
    vectorizer = TfidfVectorizer(max_df=0.85, stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(cleaned_descriptions)

    # Sum the TF-IDF score across all job descriptions for each word
    tfidf_scores = tfidf_matrix.sum(axis=0).A1
    feature_names = vectorizer.get_feature_names_out()

    # Create a DataFrame of the TF-IDF scores
    tfidf_df = pd.DataFrame({'Skill': feature_names, 'Score': tfidf_scores})

    # Filter for IT skills only
    tfidf_df = tfidf_df[tfidf_df['Skill'].isin(IT_SKILLS)]

    # Sort by score and return the top N skills
    top_skills = tfidf_df.sort_values(by='Score', ascending=False).head(top_n)

    return top_skills

if __name__ == "__main__":
    input_file = 'jobs.csv'  # Input CSV file with job descriptions
    output_file = 'cleaned_job_descriptions.csv'  # Output file for cleaned descriptions

    # Clean job descriptions using the function from cleandata.py
    clean_job_descriptions(input_file, output_file)

    # Load cleaned descriptions from the output file
    cleaned_descriptions_df = pd.read_csv(output_file)
    cleaned_descriptions = cleaned_descriptions_df['Cleaned Requirements'].dropna().tolist()  # Adjust based on your cleaned output structure
    
    # Extract the top 20 IT skills mentioned across job descriptions
    top_skills = extract_top_skills(cleaned_descriptions, top_n=20)

    # Output the top skills
    print("Top IT skills employers are looking for:")
    print(top_skills)