import pandas as pd 
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer

def load_skills(filepath):
    """Load list of skills"""
    try:
        with open(filepath, 'r') as f:
            skills_data = json.load(f)
        return {skill for skill_set in skills_data.values() for skill in skill_set}
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return set()
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {filepath}")
        return set()

def extract_top_skills(cleaned_descriptions, all_skills, top_n):
    """Extracts the top N skills mentioned in the job descriptions using TF-IDF."""
    vectorizer = TfidfVectorizer(max_df=0.85, stop_words='english', max_features=1000)  # Initialize TF-IDF Vectorizer
    tfidf_matrix = vectorizer.fit_transform(cleaned_descriptions)  # Fit and transform the cleaned descriptions

    # Sum the TF-IDF score across all job descriptions for each word
    tfidf_scores = tfidf_matrix.sum(axis=0).A1
    feature_names = vectorizer.get_feature_names_out()

    # Create a DataFrame of the TF-IDF scores
    tfidf_df = pd.DataFrame({'Skill': feature_names, 'Score': tfidf_scores})
    
    # Filter for relevant skills
    tfidf_df = tfidf_df[tfidf_df['Skill'].isin(all_skills)]

    # Sort by score and return the top N skills
    top_skills = tfidf_df.sort_values(by='Score', ascending=False).head(top_n)
    return top_skills 

def plot_top_skills(top_skills):
    """Generate a bar graph for the top skills using Seaborn."""
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_skills, x='Score', y='Skill', palette='viridis')
    
    plt.xlabel('TF-IDF Score')
    plt.ylabel('Skills')
    plt.title('Top Skills Employers are Looking For')
    plt.xticks(rotation=45)
    plt.tight_layout()  # Adjust layout to make room for labels
    plt.show()  # Show the plot

def run_extraction(input_file, skills_file, top_n):
    """Runs extraction process"""
    # Load cleaned descriptions
    cleaned_descriptions_df = pd.read_csv(input_file)
    cleaned_descriptions = cleaned_descriptions_df['Cleaned Data'].dropna().tolist()
    
    # Load skills
    all_skills = load_skills(skills_file)

    # Extract and output top skills
    if cleaned_descriptions and all_skills:
        top_skills = extract_top_skills(cleaned_descriptions, all_skills, top_n)
        print("Top skills employers are looking for:")
        print(top_skills)

        # Plot the top skills
        plot_top_skills(top_skills)
        
    else:
        print("No valid cleaned descriptions or skills found.")

if __name__ == "__main__":
    input_file = 'cleaned_job_descriptions.csv'  # Input CSV file with cleaned job descriptions
    skills_file = 'skills.json' #Input JSON file for skill sets
    top_n = 20  # Number of top skills to extract

    run_extraction(input_file, skills_file, top_n)