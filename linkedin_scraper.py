import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import datetime
from markdownify import markdownify as md
import csv
import time
import random

def createSession(): # to create a session to handle the requests
    headers = { # headers to be sent with the request
            "authority": "www.linkedin.com", 
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
    session: requests.Session = requests.Session() # create a session object
    session.headers.update(headers) # update the headers of the session object
    retry = Retry( # to retry the request if it fails
        total = 3,
        status=3,
        status_forcelist= [429, 500, 502, 503, 504],
        backoff_factor=3
    )

    adapter = HTTPAdapter(max_retries=retry) # create an adapter object to handle the retries
    session.mount('https://', adapter=adapter) # mount the adapter to the session object
    return session # return the session object

def scrapeLinkedin(search_term, search_location, noOfjobswanted): # function to scrape linkedin for jobs
    start = 0 # to keep track of the number of jobs scraped
    job_list = [] # list to store the jobs scraped
    unique_jobs = set() # set to store unique jobs
    baseUrl = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?' # base url to scrape linkedin
    session = createSession() # create a session object
    while len(job_list) < noOfjobswanted-1: # loop to scrape the number of jobs wanted
        param = { # parameters to be sent with the request
            'keywords': {search_term},
            'location': {search_location},
            'start': {start}
        }
        session.cookies.clear() # clear the cookies
        response = session.get(baseUrl, params=param, timeout=5) # send a get request to the url with the parameters
        if response.status_code != 200: # check if the response is successful
            print('response status code: ', response.status_code, response.reason) # print the status code and reason
            raise Exception(jobResponse.status_code, jobResponse.reason, 'Failed to get the response') # raise an exception
        soup = BeautifulSoup(response.text, 'html.parser') # parse the response text
        jobs = soup.find_all('div', class_='base-card') # find all the jobs
        for job in jobs: # loop through the jobs
            eachjob = [] # list to store the details of each job
            jobPosition = job.find('span', class_='sr-only').get_text(strip=True) if job.find('span', class_='sr-only') else 'NIL' # get the job position if it exists else set it to NIL
            jobUrl = job.find("a", class_="base-card__full-link")['href'].split('?')[0] if job.find("a", class_="base-card__full-link")['href'].split('?')[0] else 'NIL' # get the job url if it exists else set it to NIL
            jobId = jobUrl.split('-')[-1] if jobUrl.split('-')[-1] else 'NIL' # get the job id if it exists else set it to NIL
            company = job.find('a', class_='hidden-nested-link') if job.find('a', class_='hidden-nested-link') else 'NIl' # get the company details if it exists else set it to NIL
            companyUrl = company['href'].split('?')[0] if company['href'].split('?')[0] else 'NIL' # get the company url if it exists else set it to NIL
            companyName = company.get_text(strip=True) if company.get_text(strip=True) else 'NIL' # get the company name if it exists else set it to NIL
            joblocation = job.find('span', class_='job-search-card__location').get_text(strip=True) if job.find('span', class_='job-search-card__location').get_text(strip=True) else 'NIL' # get the job location if it exists else set it to NIL
            jobPostDate = job.find('time',class_='job-search-card__listdate')['datetime'] if job.find('time',class_='job-search-card__listdate')['datetime'] else 'NIL' # get the job post date if it exists else set it to NIL
            # jobPostDate = datetime.strptime(jobDatetime, "%Y-%m-%d") # convert the job post date to datetime object
            session.cookies.clear() # clear the cookies
            time.sleep(random.uniform(3, 6))
            jobResponse = session.get(jobUrl, timeout=5) # send a get request to the job url
            if jobResponse.status_code != 200: # check if the response is successful
                print('jobResponse status code: ', jobResponse.status_code, jobResponse.reason) # print the status code and reason
                raise Exception(jobResponse.status_code, jobResponse.reason, 'Failed to get the job response') # raise an exception
            jobSoup = BeautifulSoup(jobResponse.text, 'html.parser') # parse the response text
            jobDesctag = jobSoup.find('div', class_='show-more-less-html__markup') if jobSoup.find('div', class_='show-more-less-html__markup') else 'NIL' # get the job description tag if it exists else set it to NIL
            for attr in list(jobDesctag.attrs): # loop through the attributes of the tag
                del jobDesctag[attr] # delete the attributes
            jobDeschtml = jobDesctag.prettify(formatter='html') if jobDesctag else 'NIL' # get the job description html if it exists else set it to NIL
            jobDescMD = md(jobDeschtml) if jobDeschtml else 'NIL' # convert the job description html to markdown if it exists else set it to NIL
            jobDesc = jobDescMD.strip() # strip the job description
            if jobId in unique_jobs: # check if the job id is in the unique jobs set
                continue # continue to the next job
            unique_jobs.add(jobId) # add the job id to the unique jobs set
            
            eachjob.append(jobId) # append the job id to the list
            eachjob.append(jobPosition) # append the job position to the list
            eachjob.append(companyName) # append the company name to the list
            eachjob.append(joblocation) # append the job location to the list
            eachjob.append(jobDesc) # append the job description to the list
            eachjob.append(jobPostDate) # append the job post date to the list
            eachjob.append(jobUrl) # append the job url to the list
            eachjob.append(companyUrl) # append the company url to the list
            job_list.append(eachjob) # append the job to the job list
        if job_list == []: # check if the job list is empty
            print('No jobs found with the given parameters') # print that no jobs were found
            break # break the loop
        if len(job_list) < noOfjobswanted-1: # check if the number of jobs scraped is less than the number of jobs wanted
            time.sleep(random.uniform(4, 10)) # sleep for a random time between 4 and 10 seconds to avoid getting blocked (float)
            start += len(job_list) # increment the start by the number of jobs scraped
    return job_list[:noOfjobswanted] # return the job list with the number of jobs wanted
    
def save_to_csv(jobList): # function to save the job list to a csv file
    with open('linkedinjobs.csv', 'w', newline='', encoding='utf-8', errors='replace') as f: # open a csv file to write the job list 
        writer = csv.writer(f, delimiter=',') # create a csv writer object
        writer.writerow(['ID', 'Title','Company name', 'Location', 'Job Description', 'Job post date', 'Job URL', 'Company URL']) # write the header row
        writer.writerows(jobList) # write the job list to the csv file

if __name__ == '__main__': # main function
    while True: # loop to get the search term, location and number of jobs wanted
        search_term = input("Enter a job to search for: ") # get the search term
        if not search_term.isalpha(): # check if the search term is alphabetic
            if search_term == '': # check if the search term is empty
                search_term = '' # set the search term to '' if it is empty
                print('Will just find any jobs that show up in linkedin website first') # print that any jobs will be found
            else: # if the search term is not empty
                continue # continue to the next iteration
        search_location = input('Enter a coutntry: ') # get the search location
        if not search_location.isalpha(): # check if the search location is alphabetic
            if search_location == '': # check if the search location is empty
                search_location = 'singapore' # set the search location to singapore if it is empty
            else: # if the search location is not empty
                continue # continue to the next iteration
        noOfjobswanted = input('Enter the number of jobs to scrape: ') # get the number of jobs wanted
        if noOfjobswanted == '': # check if the number of jobs wanted is empty
            noOfjobswanted = 25 # set the number of jobs wanted to 25 if it is empty
        try: # try to convert the number of jobs wanted to an integer
            noOfjobswanted = int(noOfjobswanted) # convert the number of jobs wanted to an integer
            break # break the loop
        except ValueError: # handle the value error
            print("Enter a valid integer") # print that a valid integer should be entered
    
    scrapedJobs = scrapeLinkedin(search_term, search_location, noOfjobswanted) # scrape linkedin for jobs
    try: # try to save the job list to a csv file
        if len(scrapedJobs) == 0: # check if the job list is empty
            print("No jobs found with the parameters") # print that no jobs were found
        save_to_csv(scrapedJobs) # save the job list to a csv file
        print(f'Results saved to linkedinjobs.csv with {len(scrapedJobs)} jobs scraped from linkedin') # print that the results were saved to a csv file
    except: # handle the exception
        print("Failed to write to csv") # print that writing to csv failed