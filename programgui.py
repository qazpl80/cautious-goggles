from tkinter import messagebox
from collections import defaultdict
import customtkinter as ctk
import pandas as pd
import timesJob_scraper
import indeed_scraper
import Cleandata
import TopSkills

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
    update_result_box("Cleaning job descriptions...")
    guiwindow.update_idletasks()
    cleaned_outputfile, success = Cleandata.clean_job_descriptions()
    if success:
        update_result_box(f"Cleaned job descriptions saved to {cleaned_outputfile}.")
    else:
        update_result_box("Failed to clean job descriptions.")

#function to run when the submit button is clicked
def on_submit():
    clear_result_box()  # Clear the result box
    position = JobPositionEntry.get().strip()                                       #get the position entered by the user
    location = JobLocationEntry.get().strip()                                       #get the location entered by the user
    user_skills = JobSkillsEntry.get().split(',')                                   #get the skills entered by the user

    # Ensure at least one of the fields is filled
    if not position and not location and not any(user_skills):
        messagebox.showerror("Input Error", "Please enter at least one value in position, location, or skills.") #show an error message if the user does not enter any value in position, location, or skills
        update_result_box("Please enter at least one value in position, location, or skills.")                   #update the result box with the message
        return

    page_number = str(PageNumberEntry.get()) #get the page number entered by the user
    if page_number == '':  # if user decided not to input any page number, then it will only search for 1 page of the results
            page_number = 1
    else:
        try:
            page_number = int(page_number)  # input validation for page_number
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for the page number.") #show an error message if the user does not enter a valid number for the page number
            update_result_box("Please enter a valid number for the page number.") #update the result box with the message

    progress.set(0)                 # Reset progress bar
    update_result_box("Program started. Please wait...")
    guiwindow.update_idletasks()    # Force GUI update

    selected_sites = get_selected_sites() #get the selected sites
    if not selected_sites:
        return

    total_jobs_count = 0 #initialize the total number of jobs found to 0
    indeed_job_list = [] #create an empty list to store the indeed job details
    timesjobs_jobs = []  #create an empty list to store the timesjobs job details
    timesjob_list = []   #create an empty list to store the timesjobs jobs

   
    progress.set(0.15)  # increase progressbar to 15%
    update_result_box("Searching for jobs...")
    guiwindow.update_idletasks()    # Force GUI update

    for site in selected_sites:
        #IF THE SITE IS INDEED
        if site == 'indeed':
            update_result_box("Scraping Indeed...") 
            guiwindow.update_idletasks()

            noOfjobs = 25 * page_number                             #following the same logic as timesjobs, we will get 25 jobs per page
            indeed_jobs = indeed_scraper.main(position, noOfjobs)   #get the job details from the indeed_scraper
            jobs_info = defaultdict(str)                            #create a dictionary to store the job details
            for job in indeed_jobs[1][0]:                           #the job details are stored in the 2nd index of the list
                jobs_info['Company Name'] = job.get('job').get('employer').get('name') if job.get('job').get('employer') else 'NIL' #if the company name is not available, then it will be NIL
                jobs_info['Position'] = job.get('job').get('title')                                                                 #get the title of the job
                jobs_info['Location'] = job.get('job').get('location').get('countryName')                                           #get the location of the job
                jobs_info['Job Description'] = job.get('job').get('description').get('html')                                        #get the job description
                jobs_info['Job URL'] = f'https://sg.indeed.com/viewjob?jk={job.get('job').get('key')}'                              #get the url of the job
                indeed_job_list.append(jobs_info.copy())                                                                            #append the job details to the list
            update_result_box(f"Found {len(indeed_job_list)} jobs on Indeed.") #update the result box with the message
            total_jobs_count += len(indeed_job_list) #counting the total number of jobs found
            
            progress.set(0.35)              # Increase progress bar to 35%
            guiwindow.update_idletasks()    # Force GUI update
            
        #IF THE SITE IS TIMESJOBS
        elif site == 'timesjobs':
            update_result_box("Scraping TimesJobs...")
            guiwindow.update_idletasks()

            jobs_info = defaultdict(str) #create a dictionary to store the job details
            timesjobs_jobs, timesjobs_count, timesjob_dups = timesJob_scraper.main(position, location, user_skills, page_number) #get the job details from the timesJob_scraper
            for job in timesjobs_jobs:                                      #the job details are stored in the 1st index of the list
                jobs_info['Position'] = job[0]                              #get the title of the job
                jobs_info['Company Name'] = job[1]                          #get the company name
                jobs_info['Location'] = job[5]                              #get the location of the job
                jobs_info['Skillset Required'] = job[2]                     #get the skillset required for the job
                jobs_info['Job Description'] = job[3]                       #get the job description
                jobs_info['Job URL'] = job[4]                               #get the url of the job
                timesjob_list.append(jobs_info.copy())                      #append the job details to the list
            update_result_box(f"Found {timesjobs_count} jobs on TimesJobs.")#update the result box with the message
            total_jobs_count += len(timesjob_list) + timesjob_dups          #counting the total number of jobs found

            progress.set(0.50)              # Increase progress bar to 50%
            guiwindow.update_idletasks()    # Force GUI update
        else:
            messagebox.showerror("Input Error", "Invalid site selected.") #show an error message if the user selects an invalid site
            update_result_box("Invalid site selected.") #update the result box with the message
            return

    progress.set(0.65) # Increase progress bar to 65%
    update_result_box("Scraping completed. Saving results to Excel file...")
    guiwindow.update_idletasks()  # Force GUI update
    
    if indeed_job_list or timesjob_list:
        for site, jobs in {'Indeed': indeed_job_list, 'TimesJobs': timesjob_list}.items():
            # Define columns based on the site
            if site == 'Indeed' and indeed_job_list:
                df_indeed = pd.DataFrame(indeed_job_list)                                                                       #create a dataframe of the job details for indeed
                #columns = ["Title/Position", "Company Name", "Location", "Job Description", "Job URL"]                          #create a list of columns
            elif site == 'TimesJobs' and timesjob_list:
                df_timesjob = pd.DataFrame(timesjob_list)                                                                       #create a dataframe of the job details for timesjobs
                #columns = ["Title/Position", "Company Name", "Location", "Skillset Required", "Job Description", "Job URL"]     #create a list of columns
                update_result_box(f"Total jobs found: {total_jobs_count}. Results saved to jobs.xlsx.") if not timesjob_dups else update_result_box(f"Total jobs found: {total_jobs_count}. {timesjob_dups} duplicates removed. Results saved to jobs.xlsx.")
        
        progress.set(0.8)               # Increase progress bar to 80%
        guiwindow.update_idletasks()    # Force GUI update

        # Write DataFrames to different sheets in the same Excel file
        with pd.ExcelWriter('jobs.xlsx') as writer:
            if indeed_job_list:
                df_indeed.to_excel(writer, sheet_name='Indeed', index=False)                #write the indeed job details to the excel file but different sheets
            if timesjob_list:
                df_timesjob.to_excel(writer, sheet_name='TimesJob', index=False)            #write the timesjob job details to the excel file but different sheets

        on_Clean_Data()

        update_result_box("Top skills extracted and saved to skills.json.")
        guiwindow.update_idletasks()    # Force GUI update
        TopSkills.run_extraction('cleaned_job_descriptions.csv', 'skills.json', 20)
        

        progress.set(1)               # Increase progress bar to 80%
        guiwindow.update_idletasks()    # Force GUI update
    else:
        update_result_box("No jobs found or matched the criteria.")
        progress.set(1)
        guiwindow.update_idletasks()  # Force GUI update

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