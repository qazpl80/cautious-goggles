#Main

from bs4 import BeautifulSoup
import requests
import csv



def find_job(position,location,user_skills):
    header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6"
}
    html_text = requests.get(f'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=%22{position}%22&txtLocation={location}', headers=header).text
    soup = BeautifulSoup(html_text, 'html.parser')
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
    info = []
    for index, job in enumerate(jobs):
        indiv = []
        title = ''
        company_name = ''
        skill = job.find('span',class_='srp-skills').text.replace('\n','').replace('  ','').replace('&',' & ')
        for user_skill in user_skills:
            if user_skill in skill:
                title_url = job.header.h2.a['href']
                title_html = requests.get(str(title_url)).text
                title_soup = BeautifulSoup(title_html, 'html.parser')
                title = title_soup.find_all('h1', class_='jd-job-title')[0].text.replace('\n','').replace('\t','').replace('  ','').replace('"','')
                indiv.append(title)
                company_name = job.find('h3', class_='joblist-comp-name').text.replace('\n','').replace('(More Jobs)','').replace('  ','')
                indiv.append(company_name)
                indiv.append(skill)
                info.append(indiv)
            else:
                continue
    return info
            
def save_to_csv(info):
    with open('jobs.csv','w', newline='') as jf:
        writer = csv.writer(jf, delimiter=',')
        writer.writerow(["Position/Title","Company Name","Required Skills"])
        writer.writerows(info)
    print("File saved")

if __name__ == "__main__":
    position = input("Enter position/job: ")
    location = input("Enter location: ")
    user_skills = input("Enter your skills: ").split(',')
    jobs = find_job(position,location,user_skills)
    save_to_csv(jobs)