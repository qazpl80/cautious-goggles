import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import datetime
from markdownify import markdownify as md
import csv
import time
import random

def createSession():
    headers = {
            "authority": "www.linkedin.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
    session: requests.Session = requests.Session()
    session.headers.update(headers)
    retry = Retry(
        total = 3,
        status=3,
        status_forcelist= [429, 500, 502, 503, 504],
        backoff_factor=3
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter=adapter)
    return session

def scrapeLinkedin(search_term, search_location, noOfjobswanted):
    start = 0
    job_list = []
    unique_jobs = set()
    baseUrl = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?'
    session = createSession()
    while len(job_list) < noOfjobswanted-1:
        param = {
            'keywords': {search_term},
            'location': {search_location},
            'start': {start}
        }
        session.cookies.clear()
        response = session.get(baseUrl, params=param, timeout=5)
        if response.status_code != 200:
            print('response status code: ', response.status_code, response.reason)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('div', class_='base-card')
        for job in jobs:
            eachjob = []
            jobPosition = job.find('span', class_='sr-only').get_text(strip=True) if job.find('span', class_='sr-only') else 'NIL'
            jobUrl = job.find("a", class_="base-card__full-link")['href'].split('?')[0] if job.find("a", class_="base-card__full-link")['href'].split('?')[0] else 'NIL'
            jobId = jobUrl.split('-')[-1] if jobUrl.split('-')[-1] else 'NIL'
            company = job.find('a', class_='hidden-nested-link') if job.find('a', class_='hidden-nested-link') else 'NIl'
            companyUrl = company['href'].split('?')[0] if company['href'].split('?')[0] else 'NIL'
            companyName = company.get_text(strip=True) if company.get_text(strip=True) else 'NIL'
            joblocation = job.find('span', class_='job-search-card__location').get_text(strip=True) if job.find('span', class_='job-search-card__location').get_text(strip=True) else 'NIL'
            jobPostDate = job.find('time',class_='job-search-card__listdate')['datetime'] if job.find('time',class_='job-search-card__listdate')['datetime'] else 'NIL'
            # jobPostDate = datetime.strptime(jobDatetime, "%Y-%m-%d")
            jobResponse = session.get(jobUrl, timeout=5)
            if jobResponse.status_code != 200:
                print('jobResponse status code: ', jobResponse.status_code, jobResponse.reason)
            jobSoup = BeautifulSoup(jobResponse.text, 'html.parser')
            jobDesctag = jobSoup.find('div', class_='show-more-less-html__markup') if jobSoup.find('div', class_='show-more-less-html__markup') else 'NIL'
            for attr in list(jobDesctag.attrs):
                del jobDesctag[attr]
            jobDeschtml = jobDesctag.prettify(formatter='html')
            jobDescMD = md(jobDeschtml)
            jobDesc = jobDescMD.strip()
            if jobId in unique_jobs:
                continue
            unique_jobs.add(jobId)
            
            eachjob.append(jobId)
            eachjob.append(jobPosition)
            eachjob.append(companyName)
            eachjob.append(joblocation)
            eachjob.append(jobDesc)
            eachjob.append(jobPostDate)
            eachjob.append(jobUrl)
            eachjob.append(companyUrl)
            job_list.append(eachjob)
        if job_list == []:
            print('No jobs found with the given parameters')
            break
        if len(job_list) < noOfjobswanted-1:
            time.sleep(random.uniform(4, 10))
            start += len(job_list)
    return job_list[:noOfjobswanted]
    
def save_to_csv(jobList):
    with open('linkedinjobs.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['ID', 'Title','Company name', 'Location', 'Job Description', 'Job post date', 'Job URL', 'Company URL'])
        writer.writerows(jobList)

if __name__ == '__main__':
    while True:
        search_term = input("Enter a job to search for: ")
        if not search_term.isalpha():
            if search_term == '':
                search_term = ''
                print('Will just find any jobs that show up in linkedin website first')
            else:
                continue
        search_location = input('Enter a coutntry: ')
        if not search_location.isalpha():
            if search_location == '':
                search_location = 'singapore'
            else:
                continue
        noOfjobswanted = input('Enter the number of jobs to scrape: ')
        if noOfjobswanted == '':
            noOfjobswanted = 25
        try:
            noOfjobswanted = int(noOfjobswanted)
            break
        except ValueError:
            print("Enter a valid integer")
    
    scrapedJobs = scrapeLinkedin(search_term, search_location, noOfjobswanted)
    try:
        if len(scrapedJobs) == 0:
            print("No jobs found with the parameters")
        save_to_csv(scrapedJobs)
        print(f'Results saved to linkedinjobs.csv with {len(scrapedJobs)} jobs scraped from linkedin')
    except:
        print("Failed to write to csv")