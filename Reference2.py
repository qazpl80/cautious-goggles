import pandas as pd
import re
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer
import nltk

# Ensure NLTK data is downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Configuration
webdriver_path = 'path/to/chromedriver'
linkedin_email = 'your-email@example.com'
linkedin_password = 'your-password'
search_terms = ['Information Security', 'AAI', 'Supply Chain']
search_url_template = 'https://www.linkedin.com/jobs/search/?keywords={search_term}'
output_file_raw = 'job_descriptions_raw.xlsx'
output_file_cleaned = 'job_descriptions_cleaned.xlsx'

# Setup Selenium
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

service = Service(webdriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

def linkedin_login(email, password):
    driver.get('https://www.linkedin.com/login')
    email_field = driver.find_element(By.ID, 'username')
    password_field = driver.find_element(By.ID, 'password')
    email_field.send_keys(email)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'global-nav')))

def scrape_job_descriptions(search_terms):
    job_data = []
    for term in search_terms:
        search_url = search_url_template.format(search_term=term.replace(' ', '%20'))
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'job-card-container')))
        job_listings = driver.find_elements(By.CLASS_NAME, 'job-card-container')
        
        for job in job_listings:
            try:
                title = job.find_element(By.CLASS_NAME, 'job-card-list__title').text
                company = job.find_element(By.CLASS_NAME, 'job-card-container__company-name').text
                location = job.find_element(By.CLASS_NAME, 'job-card-container__metadata-item').text
                description_url = job.find_element(By.CLASS_NAME, 'job-card-list__title').find_element(By.XPATH, '..').get_attribute('href')
                
                # Extract job description
                driver.get(description_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'jobs-description__container')))
                description = driver.find_element(By.CLASS_NAME, 'jobs-description__container').text
                
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
finally:
    driver.quit()
