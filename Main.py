import timesJob_scraper
import indeed_scraper
#import programgui

def inputSiteType():
    scrapeSites = ['indeed','timesjobs']
    while True:
        scraperType = input('Which site to scrape? (Indeed, TimesJobs): '.lower())
        if scraperType in scrapeSites:
            return scraperType
        else:
            print('Invalid site, please enter either only Indeed or TimesJobs')

scrapeSite = inputSiteType()
if scrapeSite == 'indeed':
    indeed_scraper.main()
elif scrapeSite == 'timesjobs':
    timesJob_scraper.main()

# RUNS GUI PROGRAM-REMOVE ALL OF THE ABOVE WHEN FINALISED EXCEPT "import programgui"
# if __name__ == "__main__":
#     programgui.initialize_gui()