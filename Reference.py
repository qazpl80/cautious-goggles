import time
import selenium
import pandas as pd 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


#path = '\\Users\\marcu\\Downloads\\chromedriver.exe'
#can either be path or ChromeDriverManager().install())
driver = webdriver.Chrome(ChromeDriverManager().install())

# Maximize Window
driver.maximize_window() 
driver.minimize_window() 
driver.maximize_window() 
driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(10)

# Enter to the site
driver.get('https://www.linkedin.com/login');
time.sleep(2)

# User Credentials
# Reading txt file where we have our user credentials
with open('C:\\Users\\jiawe\\OneDrive\\SIT\\INF1002 - Programming Fundamentals\\Project\\user_credentials.txt', 'r',encoding="utf-8") as file:
    user_credentials = file.readlines()
    user_credentials = [line.rstrip() for line in user_credentials]
user_name = user_credentials[0] # First line
password = user_credentials[1] # Second line
driver.find_element("xpath", "/html/body/div/main/div[2]/div[1]/form/div[1]/input").send_keys(user_name)
driver.find_element("xpath", "/html/body/div/main/div[2]/div[1]/form/div[2]/input").send_keys(password)
time.sleep(1)

# Login button
driver.find_element("xpath", "/html/body/div/main/div[2]/div[1]/form/div[3]/button").click()
driver.implicitly_wait(30)

# Go to search results directly via link
driver.find_element("xpath",'//*[@id="global-nav"]/div/nav/ul/li[3]').click()
time.sleep(3)
driver.get("https://www.linkedin.com/jobs/search/?currentJobId=3289741756&f_T=30000&geoId=102454443&keywords=cyber%20security%20analyst&location=Singapore&refresh=true&sortBy=R")
time.sleep(2)

# Get all links for these offers
links = []

# Navigate 12 pages
print('Links are being collected now.')
#change the 3 to 14 for the full process
for page in range(2,7):
    time.sleep(2)
    jobs_block = driver.find_element(By.CLASS_NAME, 'jobs-search-results-list')
    jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')

    for job in jobs_list:
        all_links = job.find_elements(By.TAG_NAME, 'a')
        for a in all_links:
            if str(a.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links: 
                links.append(a.get_attribute('href'))
            else:
                pass
        # scroll down for each job element
        driver.execute_script("arguments[0].scrollIntoView();", job)

    print(f'Collecting the links in the page: {page-1}')
# go to next page:
    driver.find_element(By.XPATH,f"//button[@aria-label='Page {page}']").click()
    time.sleep(3)
#except:
#pass
print('Found ' + str(len(links)) + ' links for job offers')

# Create empty lists to store information
job_titles = []
company_names = []
company_locations = []
job_desc = []
position_level = [] 
post_dates = []

#Click the See more button.
#driver.find_element_by_class_name(“artdeco-card__actions”).click()

i=0
j=1

print("Visiting the links and collecting information")

for i in range(len(links)):
    try:
        driver.get(links[i])
        i=i+1
        time.sleep(2)
        #see more button
        driver.find_element(By.CLASS_NAME,"artdeco-card__actions").click()
        time.sleep(2)
    except:
        pass

    #top part of the link
    contents = driver.find_elements(By.CLASS_NAME,'p5')
    for content in contents:
        try:
            job_titles.append(content.find_element(By.TAG_NAME,"h1").text)
            company_names.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__company-name").text)
            company_locations.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__bullet").text)
            post_dates.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__posted-date").text)
            position_level.append(content.find_element(By.CLASS_NAME,"jobs-unified-top-card__job-insight").text)
            print(f'Scraping the Job Offer {j} Done.')
            j+=1
            
        except:
            pass

        time.sleep(2)
    
        #Scraping Job Description, second part of the link
        job_description = driver.find_elements(By.CLASS_NAME,'jobs-description__content')
        for job in job_description:
            job_text = job.find_element(By.CLASS_NAME,"jobs-box__html-content").text
            job_desc.append(job_text)
            print(f'Scraping the Job Offer {j}')
            time.sleep(3)  
        


# Creating the dataframe 
datacleaner = pd.DataFrame(list(zip(job_titles,company_names,company_locations,post_dates,position_level,job_desc)),
columns =['job_title', 'company_name','company_location','post_date','position_level','job_desc'])

# Storing the data to csv file
datacleaner.to_csv('job_offers.csv', index=False)

# Output job descriptions to txt file
with open('job_descriptions.txt', 'w',encoding="utf-8") as f:
    for line in job_desc:
        f.write(line)
        f.write('\n')