from bs4 import BeautifulSoup
import requests
import csv

def find_job(position, location, user_skills, page_number):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6"
    }
    page_count = 1
    info = []  # list containing all the search results (position, company name, and skillset required)
    seen_jobs = set()  # set to track unique job postings
    job_count = 0
    dup_count = 0
    while page_count <= page_number:
        url = f'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords={position}&txtLocation={location}&pDate=I&sequence={page_count}&startPage=1'
        # url2 = f'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords={position}&txtLocation={location}&pDate=I&sequence=100&startPage=1'
        print(f'TimesJobs scraper scraping page {page_count}')
        response = requests.get(url, headers=header)
        # response2 = requests.get(url2, headers=header)
        # text = response2.text
        # soup2 = BeautifulSoup(text, 'html.parser')
        # jobs2 = soup2.find_all('li', class_='clearfix job-bx wht-shd-bx')
        # print('fishingforleaf', jobs2)
        if response.status_code != 200:
            print("Response error", response.status_code, response.reason)
            return
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')  # finds all the jobs
        if not jobs:
            print(f'no more jobs from page {page_count} onwards')
            break
        for index, job in enumerate(jobs):
            eachJob = []  # to isolate each job and add into info list as a list of its own
            title = ''  # title/position offered
            company_name = ''  # the name of the company
            requiredSkills = (job.find('span', class_='srp-skills').text.replace('\n', ',').replace('  ', '').replace('&', ' & ').replace('.', '')).split(',')  # to find all the required skills for that job and to clean the text that we get back
            jobUrl = job.header.h2.a['href']  # to get the url link to access the job's posting page
            jobHtml = requests.get(str(jobUrl)).text
            jobSoup = BeautifulSoup(jobHtml, 'html.parser')
            title = jobSoup.find_all('h1', class_='jd-job-title')[0].text.replace('\n', '').replace('\t', '').replace('  ', ' ').replace('"', '').replace('  ', '')  # to get the position/title offered by the company
            jobdescription = jobSoup.find('div', class_='jd-desc job-description-main').text.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ')  # to get the job description
            jobdescription = ' '.join(jobdescription.split())  # reformat job description to make it more compact
            company_name = job.find('h3', class_='joblist-comp-name').text.replace('\n', '').replace('(More Jobs)', '').replace('  ', '')
            location_span = job.find_all('span')
            job_location = [span.get('title') for span in location_span if span.get('title')]
            
            # Check for duplicate jobs
            job_key = (title, company_name)
            if job_key in seen_jobs:
                dup_count += 1
                # print('duplicate', job_key)
                continue
            seen_jobs.add(job_key)
            
            eachJob.append(title)  # append the position/title offered by the company to a list (which contains the details of the job posting)
            eachJob.append(company_name)  # append the company name to a list (which contains the details of the job posting)
            eachJob.append(requiredSkills)  # append the required skillset of the job as a list to another list (which contains the details of the job posting)
            eachJob.append(jobdescription)  # append the job description to the list of job posting
            eachJob.append(jobUrl)  # append the url of the job posting to the list of job posting
            eachJob.append(job_location)
            info.append(eachJob)  # finally append that one job posting to the list of job postings
            job_count += 1
        page_count += 1
    return info, job_count, dup_count

def formatData(info):  # this is to format data of the required skillset so we can match and filter the skills
    for jobs in info:
        for skill in jobs[2]:  # jobs[2] is the list of skills required by the job
            if skill == '':  # if it is empty, remove it
                jobs[2].remove('')
                skill.replace('.', '')  # removing the full stops
        jobs[2] = [skill.lower() for skill in jobs[2]]  # to make all the words lowercase so we can match the skills of the user input
    return info

def save_to_csv(info):
    if info == []:  # if there is no such job
        print("No such job in TimesJobs listing with your skillsets or location")
    else:
        with open('timesjobs.csv', 'w', newline='', encoding='utf-8', errors='replace') as jf:
            writer = csv.writer(jf, delimiter=',')
            writer.writerow(["Position/Title", "Company Name", "Required Skills", "Job Description", "Link to Job"])  # write the title of the columns (categories the data)
            writer.writerows(info)  # write all the job that fits the user via their skillset into the csv
        print("File saved")

def filterViaSkills(JobInfo, user_skills):
    filteredJobs = []  # this is a list containing the list of jobs that match the skillset of the user input
    for job in JobInfo:  # for each job in the job list
        for skill in user_skills:  # for each skill entered by the user input
            for skill in job[2]:
                if skill.lower() in job[2]:  # lowercase all the words so to match the words
                    filteredJobs.append(job)  # if the user's skill is in the required skill list of the job, then add to the filteredJobs list
                    break
    return filteredJobs

def main(position, location, user_skills, page_number): 
    if page_number == '':  # if user decided not to input any page number, then it will only search for 1 page of the results
        page_number = 1
    # check for at least 1 input in either position, location or skills
    if (position == '' and location == '' and user_skills == ['']):
        print("Please enter at least 1 input")
    else:
        jobs, jobs_count, dups_count = find_job(position.lower(), location.lower(), user_skills, int(page_number))
        formattedData = formatData(jobs)  # to format the data so we can use it to filter jobs in the next function
        if user_skills == [''] or user_skills == '':  # if user decided not to put any skills
            save_to_csv(formattedData)
            return jobs, jobs_count, dups_count
        else:
            filteredJobs = filterViaSkills(formattedData, user_skills)  # to get all the jobs matching the user input of their skills
            save_to_csv(filteredJobs)
            return filteredJobs, jobs_count, dups_count
        
# def main2(position, location, user_skills, page_number): 
#     if page_number == '':  # if user decided not to input any page number, then it will only search for 1 page of the results
#         page_number = 1
#     # check for at least 1 input in either position, location or skills
#     if (position == '' and location == '' and user_skills == ['']):
#         print("Please enter at least 1 input")
#     else:
#         jobs, jobs_count, dups_count = find_job(position.lower(), location.lower(), user_skills, int(page_number))
#         formattedData = formatData(jobs)  # to format the data so we can use it to filter jobs in the next function
#         if user_skills == [''] or user_skills == '':  # if user decided not to put any skills
#             return jobs, jobs_count, dups_count
#         else:
#             filteredJobs = filterViaSkills(formattedData, user_skills)  # to get all the jobs matching the user input of their skills
#             return filteredJobs, jobs_count, dups_count
        

if __name__ == "__main__":
    main('cyber security', 'singapore','', 2)