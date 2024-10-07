import tkinter as tk  # Import the tkinter library for GUI components
from tkinter import messagebox  # Import messagebox for displaying messages
from tkinter import ttk  # Import ttk for themed widgets
import customtkinter as ctk  # Import customtkinter for custom themed widgets
import indeed_scraper  # Import indeed_scraper module
import timesJob_scraper  # Import timesJob_scraper module
import Cleandata as cleandata  # Import Cleandata module
import TopSkills as topskills  # Import TopSkills module

def formatData(jobs):  # Function to format job data
    formatted_jobs = []  # Initialize an empty list to store formatted jobs
    for job in jobs:  # Iterate through each job in the jobs list
        title = job.get('title', 'N/A')  # Get the job title, default to 'N/A' if not found
        link = job.get('link', 'N/A')  # Get the job link, default to 'N/A' if not found
        description = job.get('description', 'N/A')  # Get the job description, default to 'N/A' if not found
        formatted_jobs.append((title, link, description))  # Append the formatted job to the list
    return formatted_jobs  # Return the list of formatted jobs

def on_submit():  # Function to handle the submit button click event
    position = JobPositionEntry.get()  # Get the job position from the entry field
    location = JobLocationEntry.get()  # Get the job location from the entry field
    user_skills = JobSkillsEntry.get().replace(' ', '').split(',')  # Get and process the user skills from the entry field
    try:
        page_number = int(PageNumberEntry.get())  # Get the page number from the entry field and convert to integer
    except ValueError:
        messagebox.showerror("Input Error", "Enter a valid integer for page number")  # Show error if page number is not a valid integer
        return  # Exit the function

    progress['value'] = 0  # Reset the progress bar value to 0
    progress['maximum'] = page_number * 20  # Set the maximum value of the progress bar

    selected_sites = []  # Initialize an empty list to store selected sites
    if indeed_var.get():  # Check if Indeed checkbox is selected
        selected_sites.append('Indeed')  # Add Indeed to the selected sites list
    if timesjobs_var.get():  # Check if TimesJobs checkbox is selected
        selected_sites.append('TimesJobs')  # Add TimesJobs to the selected sites list

    if not selected_sites:  # Check if no site is selected
        messagebox.showerror("Input Error", "Select at least one site to scrape")  # Show error if no site is selected
        return  # Exit the function

    jobs = []  # Initialize an empty list to store jobs
    jobs_count = 0  # Initialize a counter for the number of jobs
    for site in selected_sites:  # Iterate through each selected site
        if site == 'Indeed':  # Check if the site is Indeed
            site_jobs, site_jobs_count = indeed_scraper.find_job(position.lower(), location.lower(), user_skills, page_number, progress)  # Scrape jobs from Indeed
        elif site == 'TimesJobs':  # Check if the site is TimesJobs
            site_jobs, site_jobs_count = timesJob_scraper.find_job(position.lower(), location.lower(), user_skills, page_number, progress)  # Scrape jobs from TimesJobs
        jobs.extend(site_jobs)  # Add the scraped jobs to the jobs list
        jobs_count += site_jobs_count  # Increment the jobs count

    formattedData = formatData(jobs)  # Format the scraped jobs

    if user_skills == ['']:  # Check if no skills are provided
        messagebox.showinfo("Job Search", f"Total jobs extracted: {jobs_count}")  # Show the total number of jobs extracted
    else:
        matched_jobs = [job for job in formattedData if any(skill in job[2] for skill in user_skills)]  # Filter jobs that match the user skills
        messagebox.showinfo("Job Search", f"Total jobs related to your skillset extracted: {len(matched_jobs)}")  # Show the number of jobs related to the user skills

    if cleandata_var.get():  # Check if the cleandata checkbox is selected
        cleandata.clean(formattedData)  # Run the cleandata script
    if topskills_var.get():  # Check if the topskills checkbox is selected
        topskills.analyze(formattedData)  # Run the topskills script

def initialize_gui():  # Function to initialize the GUI
    global JobPositionEntry, JobLocationEntry, JobSkillsEntry, PageNumberEntry, progress, guiwindow, indeed_var, timesjobs_var, cleandata_var, topskills_var  # Declare global variables

    ctk.set_appearance_mode("dark")  # Set the theme to dark
    ctk.set_default_color_theme("dark-blue")  # Set the default color theme to dark-blue

    guiwindow = ctk.CTk()  # Create the main window
    guiwindow.title("Job Search")  # Set the title of the window
    guiwindow.geometry("400x500")  # Set the size of the window
    guiwindow.minsize(400, 500)  # Set the minimum size of the window

    JobPositionLabel = ctk.CTkLabel(guiwindow, text="Enter position/job: ")  # Create a label for job position
    JobLocationLabel = ctk.CTkLabel(guiwindow, text="Enter location: ")  # Create a label for job location
    JobSkillsLabel = ctk.CTkLabel(guiwindow, text="Enter your skills: ")  # Create a label for job skills
    PageNumberLabel = ctk.CTkLabel(guiwindow, text="Enter number of pages to search: ")  # Create a label for page number
    SiteLabel = ctk.CTkLabel(guiwindow, text="Select site to scrape: ")  # Create a label for site selection
    PostProcessLabel = ctk.CTkLabel(guiwindow, text="Select post-processing options: ")  # Create a label for post-processing options

    JobPositionEntry = ctk.CTkEntry(guiwindow)  # Create an entry field for job position
    JobLocationEntry = ctk.CTkEntry(guiwindow)  # Create an entry field for job location
    JobSkillsEntry = ctk.CTkEntry(guiwindow)  # Create an entry field for job skills
    PageNumberEntry = ctk.CTkEntry(guiwindow)  # Create an entry field for page number

    indeed_var = tk.BooleanVar()  # Create a Boolean variable for Indeed checkbox
    timesjobs_var = tk.BooleanVar()  # Create a Boolean variable for TimesJobs checkbox
    IndeedCheckbox = ctk.CTkCheckBox(guiwindow, text="Indeed", variable=indeed_var)  # Create a checkbox for Indeed
    TimesJobsCheckbox = ctk.CTkCheckBox(guiwindow, text="TimesJobs", variable=timesjobs_var)  # Create a checkbox for TimesJobs

    cleandata_var = tk.BooleanVar()  # Create a Boolean variable for cleandata checkbox
    topskills_var = tk.BooleanVar()  # Create a Boolean variable for topskills checkbox
    CleanDataCheckbox = ctk.CTkCheckBox(guiwindow, text="Run cleandata.py", variable=cleandata_var)  # Create a checkbox for cleandata
    TopSkillsCheckbox = ctk.CTkCheckBox(guiwindow, text="Run topskills.py", variable=topskills_var)  # Create a checkbox for topskills

    SubmitButton = ctk.CTkButton(guiwindow, text="Submit", command=on_submit)  # Create a submit button

    progress = ttk.Progressbar(guiwindow, orient=tk.HORIZONTAL, length=300, mode='determinate')  # Create a progress bar

    JobPositionLabel.grid(row=0, column=0, padx=10, pady=5, sticky='w')  # Place the job position label in the grid
    JobPositionEntry.grid(row=0, column=1, padx=10, pady=5)  # Place the job position entry field in the grid
    JobLocationLabel.grid(row=1, column=0, padx=10, pady=5, sticky='w')  # Place the job location label in the grid
    JobLocationEntry.grid(row=1, column=1, padx=10, pady=5)  # Place the job location entry field in the grid
    JobSkillsLabel.grid(row=2, column=0, padx=10, pady=5, sticky='w')  # Place the job skills label in the grid
    JobSkillsEntry.grid(row=2, column=1, padx=10, pady=5)  # Place the job skills entry field in the grid
    PageNumberLabel.grid(row=3, column=0, padx=10, pady=5, sticky='w')  # Place the page number label in the grid
    PageNumberEntry.grid(row=3, column=1, padx=10, pady=5)  # Place the page number entry field in the grid
    SiteLabel.grid(row=4, column=0, padx=10, pady=5, sticky='w')  # Place the site label in the grid
    IndeedCheckbox.grid(row=4, column=1, padx=10, pady=5, sticky='w')  # Place the Indeed checkbox in the grid
    TimesJobsCheckbox.grid(row=5, column=1, padx=10, pady=5, sticky='w')  # Place the TimesJobs checkbox in the grid
    PostProcessLabel.grid(row=6, column=0, padx=10, pady=5, sticky='w')  # Place the post-processing label in the grid
    CleanDataCheckbox.grid(row=6, column=1, padx=10, pady=5, sticky='w')  # Place the cleandata checkbox in the grid
    TopSkillsCheckbox.grid(row=7, column=1, padx=10, pady=5, sticky='w')  # Place the topskills checkbox in the grid
    SubmitButton.grid(row=8, columnspan=2, pady=10)  # Place the submit button in the grid
    progress.grid(row=9, columnspan=2, pady=10)  # Place the progress bar in the grid

    for i in range(10):  # Make the grid cells responsive
        guiwindow.grid_rowconfigure(i, weight=1)  # Configure the row weight
    guiwindow.grid_columnconfigure(0, weight=1)  # Configure the first column weight
    guiwindow.grid_columnconfigure(1, weight=1)  # Configure the second column weight

    guiwindow.mainloop()  # Start the GUI main loop

initialize_gui()  # Call the function to initialize the GUI