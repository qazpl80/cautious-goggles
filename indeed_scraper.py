from enum import Enum
from pydantic import BaseModel
import requests
import csv
from requests.adapters import HTTPAdapter, Retry
from markdownify import markdownify
import datetime


class RequestSession(requests.Session):

    def __init__(self):
        requests.Session.__init__(self)
        
    def request(self, method, url, **kwargs):
        return requests.Session.request(self, method, url, **kwargs)


def create_session() -> requests.Session:
    session = RequestSession()
    return session


class Site(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    TIMESJOBS = "timesjobs"
    
class UserInput(BaseModel):
    scrapSites: list[Site]
    position: str
    location: str | None = None
    country: str = "singapore"
    noOfJobs: int = 20

class indeedScraper():
    def __init__(self, proxiesList :list[str] | str | None = None):
        self.session = create_session()
        self.site = Site.INDEED
        self.scrapeInput = None
        self.header = None
        self.uniqueJobs = set()
        self.apiUrl = "https://apis.indeed.com/graphql"
        self.siteUrl = "https://sg.indeed.com"
        
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500,502,503,504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def scrape(self, scrapeInput: UserInput):
        self.scrapeInput = scrapeInput
        self.header = {
        "Host": "apis.indeed.com",
        "content-type": "application/json",
        "indeed-api-key": "161092c2017b5bbab13edb12461a62d5a833871e7cad6d9d475304573de67ac8",
        "accept": "application/json",
        "indeed-locale": "en-US",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 193.1",
        "indeed-app-info": "appv=193.1; appid=com.indeed.jobsearch; osv=16.6.1; os=ios; dtype=phone",
        }
        
        jobList = []
        while len(self.uniqueJobs) < scrapeInput.noOfJobs:
          jobs = self.scrapePage()
          jobList += jobs
        return jobList[:self.scrapeInput.noOfJobs]
    
    def scrapePage(self):
        jobsList = []
        position = self.scrapeInput.position.replace('"', '\\')
        limit = self.scrapeInput.noOfJobs
        query = self.searchQuery.format(
            what = (f'what: "{position}"'),
            location = (f'location: {{where: "{self.scrapeInput.location}", radius: 35, radiusUnit: MILES}}'),
            limit = (f'limit: {limit}')
        )
        payload = {
            "query": query,
        }
        self.header["indeed-co"] = 'SG'
        response = self.session.post(
            self.apiUrl,
            headers=self.header,
            json=payload,
            timeout = 10,
        )
        if response.status_code != 200:
            print(f'{response.status_code} STATUS CODE NOT RIGHT {response.reason}')
            return jobs
        data = response.json()
        if "data" in data and "jobSearch" in data["data"] and "results" in data["data"]["jobSearch"]:
            jobs = data["data"]["jobSearch"]["results"]
        else:
            print("WRONG DATA STRUCTURE!!")
        jobs = data["data"]["jobSearch"]["results"]
        jobsList.append(jobs)
        JobsDetailsList = [self.getJobsDetails(job["job"]) for job in jobs]
        for i in JobsDetailsList:
          for j in range(len(i)):
            if i[j] is None:
              i[j] = 'NIL'
        with open('jobs.csv', 'w', newline='') as f:
          writer = csv.writer(f, delimiter=',')
          writer.writerow(['ID', 'Title', 'City', 'Country Code', 'Country Name', 'Postal Code', 'Street Address', 'Description', 'Job post date', 'Job URL'])
          writer.writerows(JobsDetailsList)
        with open('jobs.txt', 'w') as f:
          f.write('ID, Title, City, Country Code, Country Name, Postal Code, Street Address, Description, Job post date, Job URL' + '\n')
          for i in JobsDetailsList:
              f.writelines(j + ',' for j in i)
              f.write('-' * 100)
        
        return jobsList
      
    def getJobsDetails(self, job:dict):
      jobData = []
      jobUrl = f'{self.siteUrl}/viewjob?jk={job["key"]}'
      if jobUrl in self.uniqueJobs:
        return
      self.uniqueJobs.add(jobUrl)
      description = job["description"]["html"]
      if description is not None:
        descripMD = markdownify(description)
        description = descripMD.strip()
      jobPostDate = datetime.datetime.fromtimestamp(job["datePublished"]/1000).strftime('%Y-%M-%d')
      jobData.append(str(job['key']))
      jobData.append(job['title'])
      jobData.append(job.get("location", '').get("city"))
      jobData.append(job.get("location", '').get("countryCode"))
      jobData.append(job.get("location", '').get("countryName"))
      jobData.append(job.get("location", '').get("postalCode"))
      jobData.append(job.get("location", '').get("streetAddress"))
      jobData.append(description)
      jobData.append(jobPostDate)
      jobData.append(jobUrl)
      jobData.append('\n' * 8)

      return jobData
    
    searchQuery = """
        query GetJobData {{
          jobSearch(
            {what}
            {location}
            {limit}
            sort: RELEVANCE
          ) {{
            results {{
              trackingKey
              job {{
                source {{
                  name
                }}
                key
                title
                datePublished
                dateOnIndeed
                description {{
                  html
                }}
                location {{
                  countryName
                  countryCode
                  admin1Code
                  city
                  postalCode
                  streetAddress
                  formatted {{
                    short
                    long
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        
        
    
class timesJobsScraper():
    pass

class linkedinScraper():
    pass

def scrapeJobs(
    sitePlatform: str | list[str],
    position: str,
    location: str,
    indeedCountry: str = 'singapore',
    proxies: list[str] | str | None = None,
    pages: int | None = 0,
):
    SCRAPEPLATFORM = {
        Site.INDEED: indeedScraper,
        Site.LINKEDIN: linkedinScraper,
        Site.TIMESJOBS: timesJobsScraper
    }
    def siteName(site: str):
        return Site[site.upper()]
    
    def siteType():
        siteType = list(Site)
        if isinstance(sitePlatform, str):
            siteType = [siteName(sitePlatform)]
        elif isinstance(sitePlatform, list):
            siteType = [siteName(site) if isinstance(site, str) else site for site in sitePlatform]
        return siteType
    
    scrapeInput = UserInput(
        scrapSites=siteType(),
        country = "singapore",
        position = 'cyber security',
        location = "singapore",
        noOfJobs = 3
    )
    
    def scrapePlatform(site: Site):
        siteToScrape = SCRAPEPLATFORM[site[0]]
        scraper = siteToScrape()
        data = scraper.scrape(scrapeInput)
        print("Scrape done")
        return site, data
    
    def scrapedInfo(site):
        siteValue, scraped_info = scrapePlatform(site)
        return siteValue, scraped_info
    
    return scrapedInfo(scrapeInput.scrapSites)
    
jobs = scrapeJobs(
    sitePlatform=["indeed"],
    position="cyber security",
    location="singapore",
    indeedCountry="singapore"
)

print(f"Found {len(jobs)} jobs")