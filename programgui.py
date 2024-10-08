from tkinter import messagebox
from tkinter import ttk
import customtkinter as ctk
import pandas as pd
from timesJob_scraper import find_job, formatData, filterViaSkills, save_to_csv as save_timesjobs_to_csv
from indeed_scraper import scrapeJobs
from Cleandata import clean_job_descriptions
from TopSkills import run_extraction

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

    jobs = []
    total_jobs_count = 0
    jobs_dict = {}

    for site in selected_sites:
        if site == 'indeed':
            noOfjobs = 25 * page_number
            indeed_jobs = scrapeJobs('indeed', position, location, noOfjobs=noOfjobs)
            for job in indeed_jobs:
                if isinstance(job, dict):
                    job['Source'] = 'Indeed'
            jobs_dict['Indeed'] = indeed_jobs
            total_jobs_count += len(indeed_jobs)
        elif site == 'timesjobs':
            timesjobs_jobs, _ = find_job(position.lower(), location.lower(), user_skills, page_number)
            formatted_jobs = formatData(timesjobs_jobs)
            for job in formatted_jobs:
                if isinstance(job, dict):
                    job['Source'] = 'TimesJobs'
            jobs_dict['TimesJobs'] = formatted_jobs
            total_jobs_count += len(formatted_jobs)
        else:
            messagebox.showerror("Input Error", "Invalid site selected.")
            return

        progress.set(progress.get() + 20)

    if jobs_dict:
        with pd.ExcelWriter('jobs.xlsx', engine='xlsxwriter') as writer:
            for site, jobs in jobs_dict.items():
                # Define columns based on the site
                if site == 'Indeed':
                    columns = ["Title/Position", "Company Name", "Location", "Job Description", "Job URL"]
                elif site == 'TimesJobs':
                    columns = ["Title/Position", "Company Name", "Location", "Skillset Required", "Job URL"]
                else:
                    columns = ["Title/Position", "Company Name", "Location", "Job Description", "Job URL"]

                # Ensure all job dictionaries have all the required keys and merge fields
                filtered_jobs = []
                for job in jobs:
                    if isinstance(job, dict):
                        if site == 'TimesJobs':
                            job['Location'] = f"{job.get('City', 'NIL')}, {job.get('Postal Code', 'NIL')}, {job.get('Country', 'NIL')}".strip(', ')
                        for column in columns:
                            if column not in job or not job[column]:
                                job[column] = 'NIL'
                        filtered_jobs.append({key: job[key] for key in columns})

                jobs_df = pd.DataFrame(filtered_jobs)
                jobs_df = jobs_df[columns]  # Ensure the DataFrame has the correct column order
                jobs_df.to_excel(writer, sheet_name=site, index=False)

        messagebox.showinfo("Results", f"Found {total_jobs_count} jobs. Results saved to jobs.xlsx.")

        if cleandata_var.get():
            clean_job_descriptions('jobs.xlsx', 'cleaned_job_descriptions.xlsx')
            messagebox.showinfo("Results", "Cleaned job descriptions saved to cleaned_job_descriptions.xlsx.")

        if topskills_var.get():
            run_extraction('cleaned_job_descriptions.xlsx', 'skills.json', 20)
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