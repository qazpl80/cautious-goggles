import spacy
import pandas as pd
import re
from langdetect import detect
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from keybert import KeyBERT
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')
kw_model = KeyBERT()

# Initialize NLTK components
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

requirement_keywords = [
    "responsible for", "experience in", "competency", "skills", "ability to", 
    "required", "must have", "proficiency", "knowledge of", "familiarity with",
    "oversee", "manage", "supervise", "source", "identify", "mentor", "agile", "description",
    "expertise in", "develop", "implement", "coordinate", "collaborate"
]

# Clean text for further processing
def clean_text(text):
    # Retain colons, dashes, commas, and other relevant punctuation marks
    # Remove only unwanted characters like non-alphanumeric characters except for :, -, and ,
    text = re.sub(r'[^a-zA-Z0-9\s,:-]', '', text)
    
    # Tokenize the text
    words = nltk.word_tokenize(text)
    
    # Remove stop words and apply lemmatization
    cleaned_words = [lemmatizer.lemmatize(word.lower()) for word in words if word.lower() not in stop_words]
    
    return ' '.join(cleaned_words)

def preprocess_text(text):
    # Remove unwanted symbols like *, -, and •
    text = re.sub(r'[\*\-•]', '', text)  # Remove *, -, and • symbols
    
    # Remove escape sequences and normalize spaces
    text = re.sub(r'\\[tn]', ' ', text)  # Remove escape characters like \n and \t
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    
    return text

def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False
    
def keyword_based_extraction(sentences):
    # Find sentences that contain requirement-related keywords
    extracted_requirements = []
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in requirement_keywords):
            extracted_requirements.append(sentence.strip())
    
    return ' '.join(extracted_requirements) if extracted_requirements else ''

def extract_requirements(text):
    # Preprocess the text to remove unwanted symbols
    text = preprocess_text(text)
    
    # Match structured sections like "Your background", "What you will do", etc.
    pattern = re.compile(r'(\b[A-Za-z\s&]+)\s*:\s*(.+?)(?=\b[A-Za-z\s&]+(?:\s*:\s*)|$)', re.DOTALL)
    matches = pattern.findall(text)

    # Join all matches related to "requirements" sections
    extracted_requirements = []
    for heading, content in matches:
        # Add logic to filter relevant sections based on the heading or content
        if any(keyword.lower() in heading.lower() for keyword in ["Qualifications", "Skills", "Responsibilities", "Network Design", "Troubleshooting", "Experience", "Education", "Requirements", "Job Description", "Installation and Configuration", "Security Implementation", "Upgrades", "Documentation", "Performance Optimization", "Vendor Management", "Compliance & Standards","Your background", "What you will do"]):
            extracted_requirements.append(f'{heading.strip()}: {content.strip()}')
    
    # Bullet point detection for non-labeled qualifications or skills
    #bullet_point_pattern = re.compile(r'^\s*[\*\-]\s*(.+)', re.MULTILINE)
    #bullet_points = bullet_point_pattern.findall(text)
    
    #if bullet_points:
    #    extracted_requirements.append("Bullet Points: " + " | ".join(bullet_points))

    # If regex extraction fails or doesn't capture everything, fall back to keyword-based extraction
    if not extracted_requirements:
        # Tokenize the text into sentences and apply keyword-based extraction
        sentences = nltk.sent_tokenize(text)
        extracted_keywords = keyword_based_extraction(sentences)
        
        if extracted_keywords:
            extracted_requirements.append(extracted_keywords)

    return ' '.join(extracted_requirements) if extracted_requirements else 'No extracted requirements'

# Extract keywords using KeyBERT
def extract_keywords(text):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', nr_candidates=50, top_n=5)
    return ', '.join([kw[0] for kw in keywords])

# Perform NER using spaCy (MIGHT NEED TO REMOVE THIS)
def extract_ner(text):
    doc = nlp(text)
    skills = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'GPE', 'DATE', 'SKILL']]
    return ', '.join(skills) if skills else 'No skills found'

# Perform topic modeling using LDA
def topic_modeling(texts):
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    dtm = vectorizer.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=5, random_state=42)
    lda.fit(dtm)
    
    topics = []
    for index, topic in enumerate(lda.components_):
        top_words = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-5:]]
        topics.append(', '.join(top_words))
    return topics

# Main function to clean and extract information from job descriptions
def clean_job_descriptions(input_file, output_file):
    df = pd.read_csv(input_file, encoding='latin1', index_col=False)
    cleaned_data = []
    all_texts = []
    
    for index, row in df.iterrows():
        jd = row['Job Description']
        
        if is_english(jd):
            # Extract the requirements section
            requirements = extract_requirements(jd)
            if requirements:
                cleaned_requirements = clean_text(requirements)
                
                # Store cleaned text for LDA analysis later
                all_texts.append(cleaned_requirements)
                
                # Extract skills using KeyBERT, NER, and LDA
                keywords = extract_keywords(cleaned_requirements)
                ner_skills = extract_ner(cleaned_requirements)
                
                cleaned_data.append({
                    'Cleaned Data': cleaned_requirements,
                    'Keywords (KeyBERT)': keywords,
                    'NER Skills (spaCy)': ner_skills
                })
            else:
                cleaned_data.append({'Cleaned Data': 'No extracted requirements', 'Keywords (KeyBERT)': '', 'NER Skills (spaCy)': ''})
        else:
            cleaned_data.append({'Cleaned Data': 'Non-English data', 'Keywords (KeyBERT)': '', 'NER Skills (spaCy)': ''})
    
    # Perform LDA topic modeling after processing all job descriptions
    lda_topics = topic_modeling(all_texts)
    
    # Add LDA topics to the cleaned data
    for i, topic in enumerate(lda_topics):
        cleaned_data[i]['LDA Topics'] = topic
    
    # Save the results to CSV
    cleaned_df = pd.DataFrame(cleaned_data)
    cleaned_df.to_csv(output_file, index=False)

# Example usage
if __name__ == "__main__":
    input_file = 'jobs.csv'
    output_file = 'cleaned_job_descriptions.csv'
    clean_job_descriptions(input_file, output_file)