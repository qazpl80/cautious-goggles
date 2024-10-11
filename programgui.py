from tkinter import messagebox
from collections import defaultdict
import customtkinter as ctk
import pandas as pd
import timesJob_scraper
import indeed_scraper
import Cleandata
import TopSkills
import threading
import queue

#update the result box with the message
def update_result_box(message):
    result_box.configure(state='normal') #enable the result box
    result_box.insert('end', message + '\n') #insert the message to the result box
    result_box.configure(state='disabled') #disable the result box

#clear the result box
def clear_result_box():
    result_box.configure(state='normal') #enable the result box
    result_box.delete('1.0', 'end') #delete the contents of the result box
    result_box.configure(state='disabled') #disable the result box

#function to get the selected sites
def get_selected_sites():
    selected_sites = []                                                             #create an empty list to store the selected sites
    if indeed_var.get():
        selected_sites.append('indeed')                                             #if the user selects indeed, then append it to the list
    if timesjobs_var.get():                                                         
        selected_sites.append('timesjobs')                                          #if the user selects timesjobs, then append it to the list
    if not selected_sites:
        messagebox.showerror("Input Error", "Select at least one site to scrape")   #if the user does not select any site, then show an error message
        update_result_box("Select at least one site to scrape")                     #update the result box with the message
    return selected_sites                                                           #return the list of selected sites

def on_Clean_Data():
    # Function to run data cleaning in a separate thread
    def clean_data_thread():
        update_result_box("Cleaning job descriptions...")
        progress.set(0.8)
        guiwindow.update_idletasks()
        cleaned_outputfile, success = Cleandata.clean_job_descriptions()
        if success:
            guiwindow.after(0, update_result_box, f"Cleaned job descriptions saved to {cleaned_outputfile}.")  
        else:
            guiwindow.after(0, update_result_box, "Failed to clean job descriptions.")  
            
    threading.Thread(target=clean_data_thread, daemon=True).start()  # Start the cleaning thread

def scrape_indeed_jobs(position, noOfjobs, result_queue):
    indeed_job_list = []
    try:
        update_result_box("Scraping Indeed...")
        progress.set(0.45)
        indeed_jobs = indeed_scraper.main(position, noOfjobs)  # Get job details from Indeed scraper
        for job in indeed_jobs[1][0]:  # Job details are stored in the 2nd index of the list
            jobs_info = {
                'Company Name': job.get('job').get('employer').get('name') if job.get('job').get('employer') else 'NIL',
                'Position': job.get('job').get('title'),
                'Location': job.get('job').get('location').get('countryName'),
                'Job Description': job.get('job').get('description').get('html'),
                'Job URL': f'https://sg.indeed.com/viewjob?jk={job.get("job").get("key")}'
            }
            indeed_job_list.append(jobs_info)
        result_queue.put((len(indeed_job_list), "Found {} jobs on Indeed.".format(len(indeed_job_list))))  # Queue results
    except Exception as e:
        result_queue.put((0, f"Error scraping Indeed: {str(e)}"))

def scrape_timesjobs_jobs(position, location, user_skills, page_number, result_queue):
    timesjob_list = []
    try:
        update_result_box("Scraping TimesJobs...")
        progress.set(0.50)
        timesjobs_jobs, timesjobs_count, timesjob_dups = timesJob_scraper.main(position, location, user_skills, page_number)
        for job in timesjobs_jobs:  # The job details are stored in the 1st index of the list
            jobs_info = {
                'Position': job[0],
                'Company Name': job[1],
                'Location': job[5],
                'Skillset Required': job[2],
                'Job Description': job[3],
                'Job URL': job[4]
            }
            timesjob_list.append(jobs_info)
        result_queue.put((len(timesjob_list), "Found {} jobs on TimesJobs.".format(timesjobs_count)))  # Queue results
    except Exception as e:
        result_queue.put((0, f"Error scraping TimesJobs: {str(e)}"))

def scrape_jobs(selected_sites, position, location, user_skills, page_number):
    total_jobs_count = 0  # Initialize total jobs count
    indeed_job_list = []  # Create an empty list to store the Indeed job details
    timesjob_list = []    # Create an empty list to store the TimesJobs job details
    result_queue = queue.Queue()  # Create a queue to get results from threads

    def worker():
        if 'indeed' in selected_sites:
            noOfjobs = 25 * page_number  # Following the same logic as TimesJobs
            scrape_indeed_jobs(position, noOfjobs, result_queue)
        if 'timesjobs' in selected_sites:
            scrape_timesjobs_jobs(position, location, user_skills, page_number, result_queue)
        save_results_to_excel(indeed_job_list, timesjob_list)

    threading.Thread(target=worker, daemon=True).start()  # Start the scraping worker thread

    # Update the result box in the main thread
    guiwindow.after(100, check_queue, result_queue)

def check_queue(result_queue):
    try:
        while True:
            count, message = result_queue.get_nowait()  # Get results from the queue
            update_result_box(message)  # Update the result box
            if count > 0:
                # Logic to handle job lists if needed
                pass
    except queue.Empty:
        guiwindow.after(100, check_queue, result_queue)  # Check the queue again later

def save_results_to_excel(indeed_job_list, timesjob_list):
    if indeed_job_list:
        df_indeed = pd.DataFrame(indeed_job_list)  # Create a DataFrame for Indeed job details
    if timesjob_list:
        df_timesjob = pd.DataFrame(timesjob_list)  # Create a DataFrame for TimesJobs job details

    with pd.ExcelWriter('jobs.xlsx') as writer:
        if indeed_job_list:
            df_indeed.to_excel(writer, sheet_name='Indeed', index=False)  # Write the Indeed job details to the Excel file
        if timesjob_list:
            df_timesjob.to_excel(writer, sheet_name='TimesJob', index=False)  # Write the TimesJobs job details to the Excel file

    update_result_box("Job results saved to jobs.xlsx.")
    on_Clean_Data()  # Call function to clean data
    TopSkills.run_extraction('cleaned_job_descriptions.csv', 'skills.json', 20)
    progress.set(1)
    

def on_submit():
    clear_result_box()  # Clear the result box
    progress.set(0)
    position = JobPositionEntry.get().strip()  # Get the position entered by the user
    location = JobLocationEntry.get().strip()  # Get the location entered by the user
    user_skills = JobSkillsEntry.get().split(',')  # Get the skills entered by the user

    # Ensure at least one of the fields is filled
    if not position and not location and not any(user_skills):
        messagebox.showerror("Input Error", "Please enter at least one value in position, location, or skills.")
        update_result_box("Please enter at least one value in position, location, or skills.")
        return

    page_number = str(PageNumberEntry.get())  # Get the page number entered by the user
    if page_number == '':  # If user decided not to input any page number, search for 1 page of results
        page_number = 1
    else:
        try:
            page_number = int(page_number)  # Input validation for page_number
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for the page number.")
            update_result_box("Please enter a valid number for the page number.")
            return

    update_result_box("Program started. Please wait...")
    progress.set(0.15)
    guiwindow.update_idletasks()  # Force GUI update

    selected_sites = get_selected_sites()  # Get the selected sites
    if not selected_sites:
        return

    scrape_jobs(selected_sites, position, location, user_skills, page_number)

def initialize_gui():
    global JobPositionEntry, JobLocationEntry, JobSkillsEntry, PageNumberEntry, progress, guiwindow, indeed_var, timesjobs_var, cleandata_var, topskills_var, result_box

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    guiwindow = ctk.CTk()
    guiwindow.title("Job Search")
    guiwindow.geometry("650x500")
    guiwindow.minsize(650, 500)

    JobPositionLabel = ctk.CTkLabel(guiwindow, text="Enter Position/Job: ")
    JobLocationLabel = ctk.CTkLabel(guiwindow, text="Enter Location: ")
    JobSkillsLabel = ctk.CTkLabel(guiwindow, text="Enter your Skills: ")
    PageNumberLabel = ctk.CTkLabel(guiwindow, text="Enter Number of Pages: ")
    SiteLabel = ctk.CTkLabel(guiwindow, text="Select site to scrape: ")

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

    SubmitButton = ctk.CTkButton(guiwindow, text="Submit", hover_color='#006e00', command=on_submit, fg_color="#018201")

    # Buttons for running Cleandata.py and TopSkills.py
    CleanDataButton = ctk.CTkButton(guiwindow, text="Clean Data", command=on_Clean_Data)
    TopSkillsButton = ctk.CTkButton(guiwindow, text="Show Graph (Top Skills)", command=lambda: TopSkills.run_extraction('cleaned_job_descriptions.csv', 'skills.json', 20))

    progress = ctk.CTkProgressBar(guiwindow, orientation="horizontal", mode='determinate', progress_color='yellow')
    progress.set(0)

    result_box = ctk.CTkTextbox(guiwindow, height=380, width=280)
    result_box.configure(state='disabled')

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
    CleanDataButton.grid(row=6, column=0, padx=10, pady=5, sticky='w')
    TopSkillsButton.grid(row=6, column=1, padx=10, pady=5, sticky='w')
    SubmitButton.grid(row=7, columnspan=2, pady=10)
    progress.grid(row=8, columnspan=2, pady=10)
    result_box.grid(row=0, column=2, rowspan=10, padx=10, pady=10, sticky='ns')

    for i in range(11):
        guiwindow.grid_rowconfigure(i, weight=1)
    guiwindow.grid_columnconfigure(0, weight=1)
    guiwindow.grid_columnconfigure(1, weight=1)

    guiwindow.mainloop()