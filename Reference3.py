import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer
import nltk

# Ensure NLTK data is downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Configuration
linkedin_email = 'your-email@example.com'
linkedin_password = 'your-password'
search_terms = ['Information Security', 'AAI', 'Supply Chain']
search_url_template = 'https://www.linkedin.com/jobs/search/?keywords={search_term}'
output_file_raw = 'job_descriptions_raw.xlsx'
output_file_cleaned = 'job_descriptions_cleaned.xlsx'

# Dummy login function (LinkedIn login via automated scripts is typically against their terms of service)
def linkedin_login(email, password):
    # Normally, you would use a login API or other method here
    pass

def scrape_job_descriptions(search_terms):
    job_data = []
    for term in search_terms:
        search_url = search_url_template.format(search_term=term.replace(' ', '%20'))
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(search_url, headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        job_listings = soup.find_all('div', class_='job-card-container')
        
        for job in job_listings:
            try:
                title = job.find('h3', class_='job-card-list__title').get_text(strip=True)
                company = job.find('a', class_='job-card-container__company-name').get_text(strip=True)
                location = job.find('span', class_='job-card-container__metadata-item').get_text(strip=True)
                description_url = job.find('a', class_='job-card-list__title')['href']
                
                # Extract job description
                response = requests.get(description_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                description = soup.find('div', class_='jobs-description__container').get_text(strip=True)
                
                # Determine position level (This is a placeholder, actual extraction may vary)
                position_level = 'Not Specified'  # Placeholder
                
                job_data.append({
                    'Title': title,
                    'Company': company,
                    'Location': location,
                    'Description URL': description_url,
                    'Description': description,
                    'Position Level': position_level
                })
            except Exception as e:
                print(f'Error: {e}')
    
    df = pd.DataFrame(job_data)
    df.to_excel(output_file_raw, index=False)

def clean_data(input_file, output_file):
    df = pd.read_excel(input_file)
    
    # Remove non-English descriptions
    df = df[df['Description'].apply(lambda x: all(ord(c) < 128 for c in x))]
    
    # Extract relevant sections (Placeholder logic, actual extraction will need better parsing)
    def extract_requirements(description):
        # Simplified example, improve extraction based on format
        match = re.search(r'(Qualifications|Requirements|Skills).*?:\s*(.*?)(?=\n\n|\Z)', description, re.DOTALL)
        return match.group(2).strip() if match else ''
    
    df['Requirements'] = df['Description'].apply(extract_requirements)
    
    # Data Cleaning
    stop_words = set(stopwords.words('english'))
    
    def preprocess_text(text):
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
        return ' '.join(tokens)
    
    df['Cleaned Requirements'] = df['Requirements'].apply(preprocess_text)
    
    df.to_excel(output_file, index=False)

def generate_skills(input_file):
    df = pd.read_excel(input_file)
    text = ' '.join(df['Cleaned Requirements'].dropna())
    
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform([text])
    freq_dist = FreqDist(vectorizer.get_feature_names_out(), X.sum(axis=0).tolist())
    
    skills = pd.DataFrame(freq_dist.items(), columns=['Skill', 'Frequency'])
    skills = skills.sort_values(by='Frequency', ascending=False)
    
    skills.to_excel('skills_summary.xlsx', index=False)

try:
    linkedin_login(linkedin_email, linkedin_password)
    scrape_job_descriptions(search_terms)
    clean_data(output_file_raw, output_file_cleaned)
    generate_skills(output_file_cleaned)
except Exception as e:
    print(f'An error occurred: {e}')
