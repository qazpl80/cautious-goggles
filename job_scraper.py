from enum import Enum
from pydantic import BaseModel
import requests
import csv

class RequestSession(requests.Session):  # Request session class to create an object of session
    def __init__(self):  # Constructor to initialize the session
        requests.Session.__init__(self)  # Inheriting the properties of the parent class
        
    def request(self, method, url, **kwargs):  # Method to make a request to the server
        return requests.Session.request(self, method, url, **kwargs)  # Making a request to the server

def create_session() -> requests.Session:  # Function to create a session object
    session = RequestSession()  # Creating a session object
    return session  # Returning the session object

class Site(Enum):  # Enum class to define the sites
    GOOGLE_JOBS = "google_jobs"

class UserInput(BaseModel):  # Base model class to define the user input
    scrapSites: list[Site]  # List of sites to scrape
    position: str = "cyber security"  # Position to search
    location: str | None = None  # Location to search
    country: str = "singapore"  # Country to search
    noOfJobs: int = 20  # Number of jobs to scrape

class GoogleJobsScraper:  # Google Custom Search scraper for job postings
    def __init__(self, api_key: str, search_engine_id: str):
        self.session = create_session()  # Creating a session object
        self.api_key = api_key  # Your Google API Key
        self.search_engine_id = search_engine_id  # Google Custom Search Engine ID
        self.api_url = "https://www.googleapis.com/customsearch/v1"  # Google Custom Search API URL

    def scrape(self, scrape_input: UserInput):  # Method to scrape jobs
        query = f'{scrape_input.position} jobs in {scrape_input.location or scrape_input.country}'  # Job search query
        params = {
            'key': self.api_key,  # API Key
            'cx': self.search_engine_id,  # Search Engine ID
            'q': query,  # Query to search
            'num': scrape_input.noOfJobs  # Limit the number of jobs to fetch
        }

        response = self.session.get(self.api_url, params=params)  # Make the API request
        if response.status_code == 200:
            return self.parse_response(response.json())  # Parse the response if successful
        else:
            print(f"Error: {response.status_code} - {response.reason}")
            return []

    def parse_response(self, data):  # Method to parse the Google Custom Search API response
        jobs = []
        if 'items' in data:
            for item in data['items']:
                job = {
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'description': item.get('snippet'),
                }
                jobs.append(job)
        return jobs  # Returning parsed job listings

def scrapeJobs(
    sitePlatform: str | list[str],
    position: str,
    location: str,
    country: str = 'singapore',
    noOfjobs: int = 20
):
    # Site scraper dictionary
    SCRAPEPLATFORM = {
        Site.GOOGLE_JOBS: GoogleJobsScraper
    }

    def siteName(site: str):  # Function to get the site name
        return Site[site.upper()]  # Return site in uppercase format

    def siteType():  # Function to determine the site type
        site_type = list(Site)
        if isinstance(sitePlatform, str):
            site_type = [siteName(sitePlatform)]
        elif isinstance(sitePlatform, list):
            site_type = [siteName(site) if isinstance(site, str) else site for site in sitePlatform]
        return site_type

    scrapeInput = UserInput(
        scrapSites=siteType(),
        country=country,
        position=position,
        location=location,
        noOfJobs=noOfjobs
    )

    def scrapePlatform(site: Site):  # Scrape platform based on site
        api_key = "AIzaSyC8NH5UMGf_58qNZO3FJKofsaW-MlwOqCk"  # Your Google API Key
        search_engine_id = "d6151e243d5814a7c"  # Your Search Engine ID
        scraper = SCRAPEPLATFORM[site](api_key, search_engine_id)  # Create a scraper instance
        data = scraper.scrape(scrapeInput)  # Scrape the data
        print("Scrape done")  # Inform that scraping is done
        return site, data

    def scrapedInfo(site):  # Get scraped information
        site_value, scraped_info = scrapePlatform(site)
        return site_value, scraped_info

    return scrapedInfo(scrapeInput.scrapSites[0])  # Scrape and return the data from the first site

# Example usage
jobs = scrapeJobs(
    sitePlatform=["google_jobs"],  # Using Google Jobs
    position="cyber security",  # Job position
    location="Singapore",  # Location
    country="Singapore",  # Country
    noOfjobs=10  # Number of job listings to fetch
)

# Print the found jobs
for job in jobs[1]:
    print(f"Job Title: {job['title']}")
    print(f"URL: {job['link']}")
    print(f"Description: {job['description']}")
    print('-' * 40)
