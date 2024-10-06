#Main

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
    while page_count <= page_number:
        job_count = 0
        html_text = requests.get(f'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords={position}&txtLocation={location}&pDate=I&sequence={page_count}&startPage=1', headers=header).text
        soup = BeautifulSoup(html_text, 'html.parser')
        jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')  # finds all the jobs
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
            
            # Check for duplicate jobs
            job_key = (title, company_name)
            if job_key in seen_jobs:
                continue
            seen_jobs.add(job_key)
            
            eachJob.append(title)  # append the position/title offered by the company to a list (which contains the details of the job posting)
            eachJob.append(company_name)  # append the company name to a list (which contains the details of the job posting)
            eachJob.append(requiredSkills)  # append the required skillset of the job as a list to another list (which contains the details of the job posting)
            eachJob.append(jobdescription)  # append the job description to the list of job posting
            eachJob.append(jobUrl)  # append the url of the job posting to the list of job posting
            info.append(eachJob)  # finally append that one job posting to the list of job postings
            job_count += 1
        page_count += 1
    return info, job_count

def formatData(info):  # this is to format data of the required skillset so we can match and filter the skills
    for jobs in info:
        for skill in jobs[2]:  # jobs[2] is the list of skills required by the job
            if skill == '':  # if it is empty, remove it
                jobs[2].remove('')
                skill.replace('.', '')  # removing the full stops
        jobs[2] = [skill.lower() for skill in jobs[2]]  # to make all the words lowercase so we can match the skills of the user input
    return info

def filterViaSkills(JobInfo, user_skills):
    filteredJobs = []  # this is a list containing the list of jobs that match the skillset of the user input
    for job in JobInfo:  # for each job in the job list
        for skill in user_skills:  # for each skill entered by the user input
            if skill.lower() in job[2]:  # lowercase all the words so to match the words
                filteredJobs.append(job)  # if the user's skill is in the required skill list of the job, then add to the filteredJobs list
    return filteredJobs

def save_to_csv(info):
    if info == []:  # if there is no such job
        print("No such job in TimesJobs listing with your skillsets or location")
    else:
        with open('jobs.csv', 'w', newline='') as jf:
            writer = csv.writer(jf, delimiter=',')
            writer.writerow(["Position/Title", "Company Name", "Required Skills", "Job Description", "Link to Job"])  # write the title of the columns (categories the data)
            writer.writerows(info)  # write all the job that fits the user via their skillset into the csv
        print("File saved")

def main():
    while True:
        position = input("Enter position/job (Type \"exit\" to stop the program): ")
        if position.lower() == 'exit':
            break
        location = input("Enter location (Type \"exit\" to stop the program): ")
        if location.lower() == 'exit':
            break
        user_skills = input("Enter your skills (Type \"exit\" to stop the program): ").split(',')
        user_skills = [i.lower() for i in user_skills]
        if user_skills[0].lower() == 'exit':
            break
        # check for at least 1 input in either position, location or skills
        if (position == '' and location == '' and user_skills == ['']):
            print("Please enter at least 1 input")
        else:
            page_number = input("Enter number of pages to search: ")
            if page_number == '':  # if user decided not to input any page number, then it will only search for 1 page of the results
                page_number = 1
            else:
                try:
                    page_number = int(page_number)  # input validation for page_number
                except ValueError:
                    print("Enter a valid integer")
                    continue
            jobs, jobs_count = find_job(position.lower(), location.lower(), user_skills, page_number)
            formattedData = formatData(jobs)  # to format the data so we can use it to filter jobs in the next function
            if user_skills == ['']:  # if user decided not to put any skills
                save_to_csv(formattedData)  # then just save all the job posting found into the csv
            else:
                filteredJobs = filterViaSkills(formattedData, user_skills)  # to get all the jobs matching the user input of their skills
                save_to_csv(filteredJobs)  # save the results in a csv file
                print(f"Total jobs related to your skillset extracted: {jobs_count}")
            break

if __name__ == "__main__":
    main()