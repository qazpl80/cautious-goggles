from enum import Enum
from pydantic import BaseModel
import requests
import csv
from requests.adapters import HTTPAdapter, Retry
from markdownify import markdownify
import datetime


class RequestSession(requests.Session): # Request session class to create an object of session

    def __init__(self): # Constructor to initialize the session
        requests.Session.__init__(self) # Inheriting the properties of the parent class
        
    def request(self, method, url, **kwargs): # Method to make a request to the server
        return requests.Session.request(self, method, url, **kwargs) # Making a request to the server


def create_session() -> requests.Session: # Function to create a session object
    session = RequestSession() # Creating a session object
    return session # Returning the session object


class Site(Enum): # Enum class to define the sites
    LINKEDIN = "linkedin" # LinkedIn site
    INDEED = "indeed" # Indeed site
    GLASSDOOR = "glassdoor" # Glassdoor site
    TIMESJOBS = "timesjobs" # TimesJobs site
    
class UserInput(BaseModel): # Base model class to define the user input
    scrapSites: list[Site] # List of sites to scrape
    position: str = "cyber security" # Position to search
    location: str | None = None # Location to search
    country: str = "singapore" # Country to search
    noOfJobs: int = 20 # Number of jobs to scrape

class indeedScraper():  # Indeed scraper class to scrape the jobs from Indeed site
    def __init__(self, proxiesList :list[str] | str | None = None): # Constructor to initialize the class
        self.session = create_session() # Creating a session object
        self.site = Site.INDEED # Setting the site to Indeed
        self.scrapeInput = None # Initializing the scrape input
        self.header = None # Initializing the header
        self.uniqueJobs = set() # Initializing the unique jobs
        self.apiUrl = "https://apis.indeed.com/graphql"   # API URL
        self.siteUrl = "https://sg.indeed.com" # Site URL
        
        retries = Retry( # Retry object to retry the request
            total=3, # Total number of retries
            backoff_factor=1, # Backoff factor
            status_forcelist=[500,502,503,504] # Status force list
        )
        adapter = HTTPAdapter(max_retries=retries) # Adapter object to retry the request
        self.session.mount("http://", adapter) # Mounting the adapter to the session (http)
        self.session.mount("https://", adapter) # Mounting the adapter to the session (https)
        
    def scrape(self, scrapeInput: UserInput): # Method to scrape the jobs
        self.scrapeInput = scrapeInput # Setting the scrape input
        self.header = { # Header to make the request
        "Host": "apis.indeed.com", 
        "content-type": "application/json", 
        "indeed-api-key": "161092c2017b5bbab13edb12461a62d5a833871e7cad6d9d475304573de67ac8",
        "accept": "application/json",
        "indeed-locale": "en-US",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 193.1",
        "indeed-app-info": "appv=193.1; appid=com.indeed.jobsearch; osv=16.6.1; os=ios; dtype=phone",
        }
        
        jobList = [] # List to store the jobs
        while len(self.uniqueJobs) < scrapeInput.noOfJobs: # Loop to scrape the jobs
          jobs = self.scrapePage() # Scraping the page
          jobList += jobs # Adding the jobs to the list
        return jobList[:self.scrapeInput.noOfJobs] # Returning the jobs
    
    def scrapePage(self): # Method to scrape the page
        jobsList = [] # List to store the jobs
        position = self.scrapeInput.position.replace('"', '\\') # Position to search
        limit = self.scrapeInput.noOfJobs # Number of jobs to scrape
        query = self.searchQuery.format( # Query to search the jobs
            what = (f'what: "{position}"'), 
            location = (f'location: {{where: "{self.scrapeInput.location}", radius: 35, radiusUnit: MILES}}'), 
            limit = (f'limit: {limit}') if limit else ''
        )
        payload = { # Payload to make the request
            "query": query, 
        }
        self.header["indeed-co"] = 'SG' # Setting the country to Singapore
        response = self.session.post( # Making a post request
            self.apiUrl, # API URL
            headers=self.header, # Header
            json=payload, # Payload
            timeout = 10, # Timeout
        ) 
        if response.status_code != 200: # Checking the status code
            print(f'{response.status_code} STATUS CODE NOT RIGHT {response.reason}') # Printing the status code if not right
            return jobs # Returning the jobs if status code is not right
        data = response.json() # Getting the response in JSON format
        if "data" in data and "jobSearch" in data["data"] and "results" in data["data"]["jobSearch"]: # Checking the data structure
            jobs = data["data"]["jobSearch"]["results"] # Getting the jobs
        else: 
            print("WRONG DATA STRUCTURE!!") # Printing the message if wrong data structure
        jobs = data["data"]["jobSearch"]["results"] # Getting the jobs
        jobsList.append(jobs) # Adding the jobs to the list
        JobsDetailsList = [self.getJobsDetails(job["job"]) for job in jobs] # Getting the jobs details by calling the method for each job
        for i in JobsDetailsList: # Loop to check the None values
          for j in range(len(i)): 
            if i[j] is None:  # Checking if the value is None
              i[j] = 'NIL' # Setting the value to NIL if None
        with open('jobs.csv', 'w', newline='') as f: # Opening the file to write the jobs
          writer = csv.writer(f, delimiter=',') # Creating a CSV writer object to write the jobs with delimiter as comma
          writer.writerow(['ID', 'Title','Company name', 'City', 'Country Code', 'Country Name', 'Postal Code', 'Street Address', 'Job Description', 'Job post date', 'Job URL']) # Writing the header
          writer.writerows(JobsDetailsList) # Writing the jobs details
        # with open('jobs.txt', 'w') as f:
        #   f.write('ID, Title, City, Country Code, Country Name, Postal Code, Street Address, Description, Job post date, Job URL' + '\n')
        #   for i in JobsDetailsList:
        #       f.writelines(j + ',' for j in i)
        #       f.write('-' * 100)
        
        return jobsList # Returning the jobs list
      
    def getJobsDetails(self, job:dict): # Method to get the jobs details
      jobData = [] # List to store the job data
      jobUrl = f'{self.siteUrl}/viewjob?jk={job["key"]}' # Job URL
      if jobUrl in self.uniqueJobs: # Checking if the job URL is unique
        return # Returning and stop the execution of the function and go to the next job if the job URL is not unique
      self.uniqueJobs.add(jobUrl) # Adding the job URL to the unique jobs
      description = job["description"]["html"] # Description of the job
      if description is not None: # Checking if the description is not None
        descripMD = markdownify(description) # Converting the description to markdown, from HTML format to markdown format
        description = descripMD.strip().replace('\u2800','') # Stripping the empty spaces
        
      jobPostDate = datetime.datetime.fromtimestamp(job["datePublished"]/1000).strftime('%Y-%M-%d') # Job post date
      jobData.append(str(job['key'])) # Adding the job key to the job data
      jobData.append(job['title']) # Adding the job title to the job data
      jobData.append(job.get('employer', '').get('name')) 
      jobData.append(job.get("location", '').get("city")) # Adding the job city to the job data
      jobData.append(job.get("location", '').get("countryCode")) # Adding the job country code to the job data
      jobData.append(job.get("location", '').get("countryName")) # Adding the job country name to the job data
      jobData.append(job.get("location", '').get("postalCode"))  # Adding the job postal code to the job data
      jobData.append(job.get("location", '').get("streetAddress")) # Adding the job street address to the job data
      jobData.append(description) # Adding the job description to the job data
      jobData.append(jobPostDate) # Adding the job post date to the job data
      jobData.append(jobUrl) # Adding the job URL to the job data
      jobData.append('\n' * 8) # Adding 8 new lines to the job data to separate the jobs and make it more readable in the CSV file

      return jobData # Returning the job data
    
    searchQuery = """ # Search query to search the jobs 
        query GetJobData {{  # Query to get the job data
          jobSearch( # Job search query
            {what} # job/search term to search
            {location} # location to search
            {limit} # limit to search the number of jobs
            sort: RELEVANCE # Sorting the jobs by relevance
          ) {{ 
            results {{ # Results to store the jobs
              trackingKey # Tracking key to track the job
              job {{ # Job details
                source {{ # Source of the job
                  name # Name of the source
                }}
                key # ID of the job
                title # Title of the job
                datePublished # Date published of the job
                dateOnIndeed # Date on Indeed of the job
                description {{ # Description of the job
                  html # HTML format of the description
                }}
                employer {{
                  name
                }}
                location {{ # Location of the job
                  countryName # Country name
                  countryCode # Country code
                  admin1Code # Admin code
                  city # City
                  postalCode # Postal code
                  streetAddress # Street address
                  formatted {{ # Formatted address
                    short # Short address
                    long  # Long address
                  }}
                }}
              }}
            }}
          }}
        }}
        """ 
        
        
    
class timesJobsScraper(): # TimesJobs scraper class to scrape the jobs from TimesJobs site 
    pass 

class linkedinScraper(): # LinkedIn scraper class to scrape the jobs from LinkedIn site
    pass

def scrapeJobs( # Function to scrape the jobs
    sitePlatform: str | list[str], # Site platform
    position: str | None = None, # Position to search
    location: str | None = None, # Location to search
    country: str | None = None, # Country to search
    proxies: list[str] | str | None = None, # Proxies
    noOfjobs: int | None = 0, # Number of pages
):
    SCRAPEPLATFORM = { # Dictionary to store the site platform
        Site.INDEED: indeedScraper, # Indeed site
        Site.LINKEDIN: linkedinScraper, # LinkedIn site
        Site.TIMESJOBS: timesJobsScraper # TimesJobs site
    }
    def siteName(site: str): # Function to get the site name in uppercase format
        return Site[site.upper()] # Returning the site name in uppercase format if the site is present in the site platform list 
    
    def siteType(): # Function to get the site type
        siteType = list(Site) # List of sites
        if isinstance(sitePlatform, str): # Checking if the site platform is a string
            siteType = [siteName(sitePlatform)] # Getting the site name in uppercase format
        elif isinstance(sitePlatform, list): # Checking if the site platform is a list
            siteType = [siteName(site) if isinstance(site, str) else site for site in sitePlatform] # Getting the site name in uppercase format
        return siteType # Returning the site type
    
    scrapeInput = UserInput( # User input to scrape the jobs
        scrapSites=siteType(), # Site type
        country = "singapore", # Country
        position = position, # Position
        location = "singapore", # Location
        noOfJobs = noOfjobs # Number of jobs the user want to scrape
    )
    
    def scrapePlatform(site: Site): # Function to scrape the platform
        siteToScrape = SCRAPEPLATFORM[site[0]] # Site to scrape
        scraper = siteToScrape() # Scraper object
        data = scraper.scrape(scrapeInput) # Scraping the data
        print("Scrape done") # Printing the message to show that the scraping is done
        return site, data # Returning the site and data
    
    def scrapedInfo(site): # Function to get the scraped info
        siteValue, scraped_info = scrapePlatform(site) # Getting the site value and scraped info
        return siteValue, scraped_info # Returning the site value and scraped info
    
    return scrapedInfo(scrapeInput.scrapSites) # Returning the scraped info

def main(position, noOfjobs): # Main function to run the program
  while True:
    if noOfjobs == '':
      noOfjobs = 25
    if noOfjobs > 100:
      noOfjobs = 100
      print("Max job indeed is 100")
    try: 
      noOfjobs = int(noOfjobs)
    except ValueError:
      print("Enter valid integer")
      continue

    jobs = scrapeJobs( # Scraping the jobs
        sitePlatform=["indeed"], # Site platform
        position=position, # Position
        location="singapore", # Location
        country="singapore", # Country
        noOfjobs=noOfjobs # Number of jobs the user want to scrape
    )
    return jobs


if __name__ == '__main__':
  main()