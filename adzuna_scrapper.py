import requests
from bs4 import BeautifulSoup
import csv

# Prompt the user for the job position and location
job_position = input("Enter the job position to search for (e.g., Software Engineer): ")
location = input("Enter the location to search for (e.g., Singapore): ")

# Construct the search URL dynamically based on user input
url = f'https://www.adzuna.sg/search?q={job_position.replace(" ", "%20")}&w={location.replace(" ", "%20")}'

# Send a GET request to the URL
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
except requests.exceptions.RequestException as e:
    print(f"Failed to retrieve the page: {e}")
    exit()

# Check if the request was successful
if response.status_code == 200:
    print("Successfully retrieved the webpage.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
    exit()

# Create a BeautifulSoup object
soup = BeautifulSoup(response.content, 'html.parser')

# Find all job listings (adjust class based on actual HTML structure)
job_listings = soup.find_all('div', class_='a')  # Adjust this class name based on Adzuna's HTML structure

# Debugging: Check if any job listings were found
if not job_listings:
    print("No job listings found. Please check the HTML structure or class names.")
    exit()
else:
    print(f"Found {len(job_listings)} job listings.")

# Initialize a list to store job data
jobs = []

# Extract data from each job listing
for job in job_listings:
    title_element = job.find('h2').find('a')  # Find the job title link
    company_element = job.find('div', class_='ui-company')  # Find the company name
    description_element = job.find('span', class_='max-snippet-height md:overflow-hidden')  # Find the job description

    link = title_element['href'] if title_element else "N/A"  # Get the job URL
    title = title_element.get_text(strip=True) if title_element else "N/A"
    company = company_element.get_text(strip=True) if company_element else "N/A"
    description = description_element.get_text(strip=True) if description_element else "N/A"

    # Append the job details to the jobs list
    jobs.append({
        'title': title,
        'company': company,
        'link': link,
        'description': description
    })

# Write the extracted job data to a CSV file
csv_filename = 'job_listings.csv'

with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(['Position/Title', 'Company Name', 'Job Description', 'Link to Job'])

    # Write the job data
    for job in jobs:
        writer.writerow([job['title'], job['company'], job['description'], job['link']])

print(f"Job data written to {csv_filename}.")
