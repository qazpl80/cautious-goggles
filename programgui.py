from tkinter import messagebox
from tkinter import ttk
import customtkinter as ctk
import pandas as pd
import timesJob_scraper
import indeed_scraper
import Cleandata
import TopSkills
from collections import defaultdict

def get_selected_sites():
    selected_sites = []
    if indeed_var.get():
        selected_sites.append('indeed')
    if timesjobs_var.get():
        selected_sites.append('timesjobs')
    if not selected_sites:
        messagebox.showerror("Input Error", "Select at least one site to scrape")
    return selected_sites

def on_submit():
    position = JobPositionEntry.get().strip()
    location = JobLocationEntry.get().strip()
    user_skills = JobSkillsEntry.get().replace(' ', '').split(',')

    # Ensure at least one of the fields is filled
    if not position and not location and not any(user_skills):
        messagebox.showerror("Input Error", "Please enter at least one value in position, location, or skills.")
        return

    page_number = str(PageNumberEntry.get())

    if page_number == '':  # if user decided not to input any page number, then it will only search for 1 page of the results
        page_number = 1

    try:
        page_number = int(page_number)  # input validation for page_number
        if page_number < 1:
            page_number = 1
        elif page_number > 20:
            page_number = 20
            messagebox.showinfo("Input Info", "The maximum number of pages to search is 20. Setting to 20.")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for pages.")
        return

    progress.set(0)
    progress['maximum'] = page_number * 20

    selected_sites = get_selected_sites()
    if not selected_sites:
        return

    total_jobs_count = 0
    indeed_job_list = []
    timesjobs_jobs = []

    for site in selected_sites:
        if site == 'indeed':
            noOfjobs = 25 * page_number
            indeed_jobs = indeed_scraper.main(position, noOfjobs)
            jobs_info = defaultdict(str)
            while True:
                if len(indeed_job_list) <= 25:
                    for job in indeed_jobs[1][0]:
                        jobs_info['Company Name'] = job.get('job').get('employer').get('name')
                        jobs_info['Position'] = job.get('job').get('title')
                        jobs_info['Location'] = job.get('job').get('location').get('countryName')
                        jobs_info['Job Description'] = job.get('job').get('description').get('html')
                        jobs_info['Job URL'] = f'https://sg.indeed.com/viewjob?jk={job.get('job').get('key')}'
                        indeed_job_list.append(jobs_info.copy())
                else:
                    break
            total_jobs_count += len(indeed_job_list)

        elif site == 'timesjobs':
            timesjobs_jobs, timesjobs_count = timesJob_scraper.main(position, location, user_skills, page_number)
            total_jobs_count += timesjobs_count
        else:
            messagebox.showerror("Input Error", "Invalid site selected.")
            return

        progress.set(progress.get() + 20)

    if indeed_job_list or timesjobs_jobs:
        for site, jobs in {'Indeed': indeed_job_list, 'TimesJobs': timesjobs_jobs}.items():
            # Define columns based on the site
            if site == 'Indeed':
                columns = ["Title/Position", "Company Name", "Location", "Job Description", "Job URL"]
            elif site == 'TimesJobs':
                columns = ["Title/Position", "Company Name", "Location", "Skillset Required", "Job URL"]
            else:
                columns = ["Title/Position", "Company Name", "Location", "Job Description", "Job URL"]

        # Create DataFrame and write to Excel
        df = pd.DataFrame(indeed_job_list)
        df.to_excel('jobs.xlsx', index=False)

        messagebox.showinfo("Results", f"Found {total_jobs_count} jobs. Results saved to jobs.xlsx.")

        if cleandata_var.get():
            Cleandata.clean_job_descriptions('jobs.xlsx', 'cleaned_job_descriptions.xlsx')
            messagebox.showinfo("Results", "Cleaned job descriptions saved to cleaned_job_descriptions.xlsx.")

        if topskills_var.get():
            TopSkills.run_extraction('cleaned_job_descriptions.xlsx', 'skills.json', 20)
    else:
        messagebox.showinfo("Results", "No jobs found.")

def initialize_gui():
    global JobPositionEntry, JobLocationEntry, JobSkillsEntry, PageNumberEntry, progress, guiwindow, indeed_var, timesjobs_var, cleandata_var, topskills_var

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    guiwindow = ctk.CTk()
    guiwindow.title("Job Search")
    guiwindow.geometry("400x500")
    guiwindow.minsize(400, 500)

    JobPositionLabel = ctk.CTkLabel(guiwindow, text="Enter position/job: ")
    JobLocationLabel = ctk.CTkLabel(guiwindow, text="Enter location: ")
    JobSkillsLabel = ctk.CTkLabel(guiwindow, text="Enter your skills: ")
    PageNumberLabel = ctk.CTkLabel(guiwindow, text="Enter number of pages to search: ")
    SiteLabel = ctk.CTkLabel(guiwindow, text="Select site to scrape: ")
    PostProcessLabel = ctk.CTkLabel(guiwindow, text="Select post-processing options: ")

    JobPositionEntry = ctk.CTkEntry(guiwindow)
    JobLocationEntry = ctk.CTkEntry(guiwindow)
    JobSkillsEntry = ctk.CTkEntry(guiwindow)
    PageNumberEntry = ctk.CTkEntry(guiwindow, width=50)

    indeed_var = ctk.BooleanVar()
    timesjobs_var = ctk.BooleanVar()
    IndeedCheckbox = ctk.CTkCheckBox(guiwindow, text="Indeed", variable=indeed_var)
    TimesJobsCheckbox = ctk.CTkCheckBox(guiwindow, text="TimesJobs", variable=timesjobs_var)

    cleandata_var = ctk.BooleanVar()
    topskills_var = ctk.BooleanVar()
    CleanDataCheckbox = ctk.CTkCheckBox(guiwindow, text="Run cleandata.py", variable=cleandata_var)
    TopSkillsCheckbox = ctk.CTkCheckBox(guiwindow, text="Run topskills.py", variable=topskills_var)

    SubmitButton = ctk.CTkButton(guiwindow, text="Submit", command=on_submit)

    progress = ctk.CTkProgressBar(guiwindow, orientation="horizontal", mode='determinate')
    progress.set(0)

    JobPositionLabel.grid(row=0, column=0, padx=10, pady=5, sticky='w')
    JobPositionEntry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky='w')
    JobLocationLabel.grid(row=1, column=0, padx=10, pady=5, sticky='w')
    JobLocationEntry.grid(row=1, column=1, padx=(0, 10), pady=5, sticky='w')
    JobSkillsLabel.grid(row=2, column=0, padx=10, pady=5, sticky='w')
    JobSkillsEntry.grid(row=2, column=1, padx=(0, 10), pady=5, sticky='w')
    PageNumberLabel.grid(row=3, column=0, padx=10, pady=5, sticky='w')
    PageNumberEntry.grid(row=3, column=1, padx=(0, 10), pady=5, sticky='w')
    SiteLabel.grid(row=4, column=0, padx=10, pady=5, sticky='w')
    IndeedCheckbox.grid(row=4, column=1, padx=10, pady=5, sticky='w')
    TimesJobsCheckbox.grid(row=5, column=1, padx=10, pady=5, sticky='w')
    PostProcessLabel.grid(row=6, column=0, padx=10, pady=5, sticky='w')
    CleanDataCheckbox.grid(row=6, column=1, padx=10, pady=5, sticky='w')
    TopSkillsCheckbox.grid(row=7, column=1, padx=10, pady=5, sticky='w')
    SubmitButton.grid(row=8, columnspan=2, pady=10)
    progress.grid(row=9, columnspan=2, pady=10)

    for i in range(10):
        guiwindow.grid_rowconfigure(i, weight=1)
    guiwindow.grid_columnconfigure(0, weight=1)
    guiwindow.grid_columnconfigure(1, weight=1)

    guiwindow.mainloop()