from enum import Enum
from pydantic import BaseModel
import requests
import csv
from requests.adapters import HTTPAdapter, Retry
from concurrent.futures import ThreadPoolExecutor, Future
import json

class RequestsRotating(requests.Session):

    def __init__(self, proxies=None, has_retry=False, delay=1, clear_cookies=False):
        requests.Session.__init__(self)
        self.clear_cookies = clear_cookies
        self.allow_redirects = True
        self.setup_session(has_retry, delay)

    def setup_session(self, has_retry, delay):
        if has_retry:
            retries = Retry(
                total=3,
                connect=3,
                status=3,
                status_forcelist=[500, 502, 503, 504, 429],
                backoff_factor=delay,
            )
            adapter = HTTPAdapter(max_retries=retries)
            self.mount("http://", adapter)
            self.mount("https://", adapter)
            
    def request(self, method, url, **kwargs):
        return requests.Session.request(self, method, url, **kwargs)

# class RequestsRotating(requests.Session):

#     def __init__(self, proxies=None, has_retry=False, delay=1, clear_cookies=False):
#         requests.Session.__init__(self)
#         self.clear_cookies = clear_cookies
#         self.allow_redirects = True
#         self.setup_session(has_retry, delay)

#     def setup_session(self, has_retry, delay):
#         if has_retry:
#             retries = Retry(
#                 total=3,
#                 connect=3,
#                 status=3,
#                 status_forcelist=[500, 502, 503, 504, 429],
#                 backoff_factor=delay,
#             )
#             adapter = HTTPAdapter(max_retries=retries)
#             self.mount("http://", adapter)
#             self.mount("https://", adapter)

#     def request(self, method, url, **kwargs):
#         return requests.Session.request(self, method, url, **kwargs)

def create_session(
    *,
    proxies: dict | str | None = None,
    is_tls: bool = True,
    has_retry: bool = False,
    delay: int = 1,
    clear_cookies: bool = False,
) -> requests.Session:
    """
    Creates a requests session with optional tls, proxy, and retry settings.
    :return: A session object
    """
    session = RequestsRotating(
        proxies=proxies,
        has_retry=has_retry,
        delay=delay,
        clear_cookies=clear_cookies,
    )

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
        jobs = self.scrapePage()
        print(jobs)
        # page = 0
        # count = 0
        # while page < scrapeInput.noOfJobs:
        #     jobs = self.scrapePage()
        #     if not jobs:
        #         break
        #     jobList += jobs
        #     page += 1
        #     count += 1
        # print("counttttttttttttttttttttttttt", count)
        # return jobs
        
        # for i in range(page):
        #     scrapedData = self.scrapePage()
        #     jobList += scrapedData
        # return jobList
    
    def scrapePage(self):
        jobs = []
        position = self.scrapeInput.position.replace('"', '\\')
        query = self.searchQuery.format(
            what = (f'what: "{position}"'),
            location = (f'location: {{where: "{self.scrapeInput.location}", radius: 50, radiusUnit: MILES}}')
        )
        payload = {
            "query": query,
        }
        print("Payload:", payload)
        print("Headers:", self.header)
        self.header["indeed-co"] = 'SG'
        response = self.session.post(
            self.apiUrl,
            headers=self.header,
            json=payload,
            timeout = 10,
        )
        print(response.status_code)
        if response.status_code != 200:
            print(f'{response.status_code} STATUS CODE NOT RIGHT {response.reason}')
            return jobs
        data = response.json()
        print("Response JSON:", data)
        if "data" in data and "jobSearch" in data["data"] and "results" in data["data"]["jobSearch"]:
            jobs = data["data"]["jobSearch"]["results"]
        else:
            print("Expected data structure not found in response")
        jobs = data["data"]["jobSearch"]["results"]
        print('jobbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbs', jobs)
        #new_cursor = data["data"]["jobSearch"]["pageInfo"]["nextCursor"]
        with open('jobs.txt', 'w') as f:
          for i in jobs:
            f.write(json.dumps(i))
        return jobs, #new_cursor
    
    # searchQuery = """
    #     query GetJobData {{
    #       jobSearch(
    #         {what}
    #         {location}
    #         limit: 100
    #         sort: RELEVANCE
    #       ) {{
    #         pageInfo {{
    #           nextCursor
    #         }}
    #         results {{
    #           trackingKey
    #           job {{
    #             source {{
    #               name
    #             }}
    #             key
    #             title
    #             datePublished
    #             dateOnIndeed
    #             description {{
    #               html
    #             }}
    #             location {{
    #               countryName
    #               countryCode
    #               admin1Code
    #               city
    #               postalCode
    #               streetAddress
    #               formatted {{
    #                 short
    #                 long
    #               }}
    #             }}
    #             compensation {{
    #               estimated {{
    #                 currencyCode
    #                 baseSalary {{
    #                   unitOfWork
    #                   range {{
    #                     ... on Range {{
    #                       min
    #                       max
    #                     }}
    #                   }}
    #                 }}
    #               }}
    #               baseSalary {{
    #                 unitOfWork
    #                 range {{
    #                   ... on Range {{
    #                     min
    #                     max
    #                   }}
    #                 }}
    #               }}
    #               currencyCode
    #             }}
    #             attributes {{
    #               key
    #               label
    #             }}
    #             employer {{
    #               relativeCompanyPageUrl
    #               name
    #               dossier {{
    #                   employerDetails {{
    #                     addresses
    #                     industry
    #                     employeesLocalizedLabel
    #                     revenueLocalizedLabel
    #                     briefDescription
    #                     ceoName
    #                     ceoPhotoUrl
    #                   }}
    #                   images {{
    #                         headerImageUrl
    #                         squareLogoUrl
    #                   }}
    #                   links {{
    #                     corporateWebsite
    #                 }}
    #               }}
    #             }}
    #             recruit {{
    #               viewJobUrl
    #               detailedSalary
    #               workSchedule
    #             }}
    #           }}
    #         }}
    #       }}
    #     }}
    #     """
    
    searchQuery = """
        query GetJobData {{
          jobSearch(
            {what}
            {location}
            limit: 100
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
                  city
                  postalCode
                  streetAddress
                  formatted {{
                    short
                    long
                  }}
                }}
                
                employer {{
                  relativeCompanyPageUrl
                  name
                  dossier {{
                      employerDetails {{
                        addresses
                        industry
                        employeesLocalizedLabel
                        revenueLocalizedLabel
                        briefDescription
                        ceoName
                        ceoPhotoUrl
                      }}
                      images {{
                            headerImageUrl
                            squareLogoUrl
                      }}
                      links {{
                        corporateWebsite
                    }}
                  }}
                }}
                recruit {{
                  viewJobUrl
                  detailedSalary
                  workSchedule
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
        noOfJobs = 20
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
print(jobs.head())
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)