import pandas as pd
from langdetect import detect
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    """Cleans the text by removing non-alphabetic characters, stop words, and applying lemmatization."""
    # Remove non-alphabetic characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenize the text
    words = nltk.word_tokenize(text)
    
    # Remove stop words and lemmatize
    cleaned_words = [lemmatizer.lemmatize(word.lower()) for word in words if word.lower() not in stop_words]
    
    return ' '.join(cleaned_words)

def is_english(text):
    """Detects if the text is in English."""
    try:
        return detect(text) == 'en'
    except:
        return False

def extract_requirements(text):
    """Extracts qualifications/requirements from job descriptions."""
    # This is a placeholder; you may want to implement a more sophisticated method.
    requirements_section = re.search(r'(Qualifications|Requirements|Skills|Desired Skills).*?(?=Responsibilities|$)', text, re.IGNORECASE)
    return requirements_section.group(0) if requirements_section else ''

def clean_job_descriptions(input_file, output_file):
    # Read the csv file with specified encoding
    df = pd.read_csv(input_file, encoding='latin1')  # You can change 'latin1' to 'iso-8859-1' or 'cp1252' if needed

    # Assuming the job descriptions are in a column named 'Job Description'
    cleaned_data = []
    
    for index, row in df.iterrows():
        jd = row['Job Description']
        
        # Check if JD is in English
        if is_english(jd):
            # Extract the requirements
            requirements = extract_requirements(jd)
            cleaned_requirements = clean_text(requirements)
            cleaned_data.append({'Cleaned Requirements': cleaned_requirements})

    # Convert cleaned data to a DataFrame and save to CSV
    cleaned_df = pd.DataFrame(cleaned_data)
    cleaned_df.to_csv(output_file, index=False)

# Example usage
if __name__ == "__main__":
    input_file = 'jobs.csv'  # Input CSV file with job descriptions
    output_file = 'cleaned_job_descriptions.csv'  # Output CSV file
    clean_job_descriptions(input_file, output_file)