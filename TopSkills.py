import pandas as pd 
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from Cleandata import clean_job_descriptions

# Download NLTK resources
nltk.download('punkt')  # Download tokenizer
nltk.download('stopwords')  # Download stopwords
nltk.download('wordnet')  # Download wordnet for lemmatization

# Initialize lemmatizer and stopwords
lemmatizer = nltk.WordNetLemmatizer()  # Initialize lemmatizer
stop_words = set(nltk.corpus.stopwords.words('english'))  # Set of English stopwords

# Define a list of general skills
GENERAL_SKILLS = {
    'communication', 'teamwork', 'problem solving', 'leadership', 'time management',
    'adaptability', 'creativity', 'work ethic', 'interpersonal skills', 'critical thinking',
    'organization', 'attention to detail', 'customer service', 'project management',
    'negotiation', 'conflict resolution', 'decision making', 'multitasking', 'presentation skills',
    'analytical skills'
}

# Define a list of IT and infocomm skills
ICT_SKILLS = {
    'python', 'java', 'c#', 'javascript', 'html', 'css', 'sql', 'linux', 'devops',
    'machine learning', 'data analysis', 'cloud computing', 'react', 'angular',
    'typescript', 'git', 'docker', 'kubernetes', 'agile', 'scrum', 'database',
    'networking', 'cybersecurity', 'artificial intelligence', 'web development',
    'mobile development', 'api', 'software development', 'big data', 'data science',
    'information technology', 'it support', 'system administration', 'telecommunications',
    'information systems', 'it project management'
}

# Define a list of business skills
BUSINESS_SKILLS = {
    'business analysis', 'financial analysis', 'marketing', 'sales', 'strategic planning',
    'business development', 'accounting', 'budgeting', 'forecasting', 'risk management',
    'supply chain management', 'operations management', 'human resources', 'customer relationship management'
}

# Define a list of design skills
DESIGN_SKILLS = {
    'graphic design', 'ui design', 'ux design', 'web design', 'adobe photoshop', 'illustrator',
    'indesign', 'sketch', 'figma', 'prototyping', 'wireframing', 'visual design', 'branding'
}

# Define a list of engineering skills
ENGINEERING_SKILLS = {
    'mechanical engineering', 'electrical engineering', 'civil engineering', 'chemical engineering',
    'biomedical engineering', 'aerospace engineering', 'structural engineering', 'project management',
    'cad', 'solidworks', 'matlab', 'ansys', 'finite element analysis', 'thermodynamics', 'fluid mechanics'
}

# Define a list of food, chemical, and biology skills
FOOD_CHEM_BIO_SKILLS = {
    'food science', 'nutrition', 'dietitian', 'biochemistry', 'molecular biology', 'genetics',
    'microbiology', 'chemical analysis', 'laboratory techniques', 'quality control', 'food safety',
    'chemical engineering', 'biotechnology', 'pharmaceuticals'
}

# Define a list of health and social sciences skills
HEALTH_SOCIAL_SCIENCES_SKILLS = {
    'nursing', 'public health', 'social work', 'psychology', 'counseling', 'healthcare management',
    'clinical research', 'epidemiology', 'mental health', 'community outreach', 'patient care',
    'health education', 'case management'
}

def extract_top_skills(cleaned_descriptions, top_n=20):
    """Extracts the top N skills mentioned in the job descriptions using TF-IDF."""
    vectorizer = TfidfVectorizer(max_df=0.85, stop_words='english', max_features=1000)  # Initialize TF-IDF Vectorizer
    tfidf_matrix = vectorizer.fit_transform(cleaned_descriptions)  # Fit and transform the cleaned descriptions

    # Sum the TF-IDF score across all job descriptions for each word
    tfidf_scores = tfidf_matrix.sum(axis=0).A1  # Sum TF-IDF scores
    feature_names = vectorizer.get_feature_names_out()  # Get feature names

    # Create a DataFrame of the TF-IDF scores
    tfidf_df = pd.DataFrame({'Skill': feature_names, 'Score': tfidf_scores})  # Create DataFrame

    # Combine all skill sets
    all_skills = ICT_SKILLS.union(GENERAL_SKILLS).union(BUSINESS_SKILLS).union(DESIGN_SKILLS).union(
        ENGINEERING_SKILLS).union(FOOD_CHEM_BIO_SKILLS).union(HEALTH_SOCIAL_SCIENCES_SKILLS)  # Union of all skills
    
    # Filter for relevant skills
    tfidf_df = tfidf_df[tfidf_df['Skill'].isin(all_skills)]  # Filter DataFrame for relevant skills

    # Sort by score and return the top N skills
    top_skills = tfidf_df.sort_values(by='Score', ascending=False).head(top_n)  # Sort and get top N skills

    return top_skills  # Return top skills

if __name__ == "__main__":
    input_file = 'jobs.csv'  # Input CSV file with job descriptions
    output_file = 'cleaned_job_descriptions.csv'  # Output file for cleaned descriptions

    # Clean job descriptions using the function from cleandata.py
    clean_job_descriptions(input_file, output_file)  # Clean job descriptions

    # Load cleaned descriptions from the output file
    cleaned_descriptions_df = pd.read_csv(output_file)  # Read cleaned descriptions
    cleaned_descriptions = cleaned_descriptions_df['Cleaned Requirements'].dropna().tolist()  # Convert to list and drop NaNs
    
    # Extract the top 20 skills mentioned across job descriptions
    top_skills = extract_top_skills(cleaned_descriptions, top_n=20)  # Extract top skills

    # Output the top skills
    print("Top skills employers are looking for:")  # Print header
    print(top_skills)  # Print top skills