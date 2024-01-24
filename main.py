import sys, os, time
from PMC_New_Edit.spiders.pmc_crawler import PmcCrawlerSpider

from PMC_New_Edit.selenium_driver.selenium_part import NCBI_Crawler
#from ..selenium_driver.selenium_part import NCBI_Crawler
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
sys.path.append(os.getcwd())
print(f"current working directory is :: {os.getcwd()}")
import subprocess
import pandas as pd
import logging, random

def ChangeVPN():
        countries = ["Georgia","Serbia","Moldova","'North Macedonia'","Jersey","Monaco","Slovakia",
                     "Slovenia","Croatia","Albania","Cyprus","Liechtenstein","Malta","Ukraine",
                     "Belarus","Bulgaria","Hungary","Luxembourg","Montenegro","Andorra",
                     "'Czech Republic'","Estonia","Latvia","Lithuania","Poland","Armenia","Austria",
                     "Portugal","Greece","Finland","Belgium","Denmark","Norway","Iceland","Ireland",
                     "Spain","Romania","Italy","Sweden","Turkey","Singapore","Japan",
                     "Australia","'South Korea - 2'","Malaysia","Pakistan","'Sri Lanka'","Kazakhstan",
                     "Thailand","Indonesia","'New Zealand'","Taiwan - 3","Cambodia","Vietnam","Macau",
                     "Mongolia","Laos","Bangladesh","Uzbekistan","Myanmar","Nepal","Brunei","Bhutan",
                     "'United Kingdom'", "'United States'","Japan", "Germay", "'Hong Kong'", "Netherlands",
                     "Switzerland","Algeria","France","Egypt"] 
        choice = random.choice(countries)
        print(f"Selected Country is {choice}")
        
        process = subprocess.Popen(["powershell",".\expresso.exe", "connect", "--change",
                            f"{str(choice)}"],shell=True)
        result = process.communicate()[0]
        print(result)    
def run_spider(filename, page):
    try:
        import scrapy
        import asyncio
        #os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'settings')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        from twisted.internet import asyncioreactor
        scrapy.utils.reactor.install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
        print("$$**"*5)
        is_asyncio_reactor_installed = scrapy.utils.reactor.is_asyncio_reactor_installed()
        
        print(f"Is asyncio reactor installed: {is_asyncio_reactor_installed}")
        from twisted.internet import reactor, defer
        from scrapy.crawler import CrawlerProcess

        #from ncbi_pmc.spiders.main_extractn import NCBI_pmc_extract
        
        strout = filename + "_" + str(page)+ "_results.csv"
        custom_args = {
            "FEEDS": {
                f"{strout}": {"format": "csv"},
            },
        }
        settings = dict(get_project_settings(), **custom_args)
        configure_logging(settings)
        #f = open("db-1.txt", "r")
        #a = f.readlines()
        #b = random.choice(a).strip('\n')
        
        
        runner = CrawlerProcess(settings=settings)
        @defer.inlineCallbacks
        def crawl():
            # Create the process with custom settings
            yield runner.crawl(PmcCrawlerSpider, filename=filename, page_no=page)
            #yield runner.crawl(MySpider2)
            print(f" Runner.spider_loader printing ... : {runner.spider_loader}")
            #d.addCallback(lambda _: runner.stop())
            runner.stop()
            
            print(f" Runner.crawler printing .... : {runner.crawlers}")
        crawl()
        runner.start(stop_after_crawl=True,install_signal_handlers=True)
        if "twisted.internet.reactor" in sys.modules:
            del sys.modules["twisted.internet.reactor"]
        else: 
            print("twisted.internet.reactor modules not Found in Sys")
        
        print("Rextor is Stopped!")
    except Exception as e:
        print(f"Exception Error occurred : {str(e)}")
        



if __name__ == "__main__":        
    filename = input("For Saving Data to a file, Enter Filename: ")
    Keyword_input = input("Enter the Keyword: ")
    s_year = input("Enter the start year: ")
    s_month = input("Enter the start month: ")
    s_day = input("Enter the start day: ")
    e_year = input("Enter the end year: ")
    e_month = input("Enter the end month: ")
    e_day = input("Enter the end day: ")
    
    init_page = input("From which page no. you want to scrape? ")
    dates_range = [s_year,s_month,s_day,e_year,e_month,e_day]
    print(dates_range)
    start_list = []
    #page_no = 0
    with NCBI_Crawler() as bot:
        bot.start_browser(Keyword_input,s_year,s_month,s_day,e_year,e_month,e_day)
        print(f"Session ID for Bot chrom ==> {bot.browser_pid}")
        ranges_list = bot.Page_Ranges()
        print(ranges_list)
        if init_page != 0:
            print(f"User want to start from {init_page}th page. ")
            start_list = [i for i in ranges_list if int(init_page) < i]
            start_list.append(int(init_page))
            start_list.sort()
            
        else : 
            start_list = ranges_list
        
        print(f" Check for processes still running ? {bot.service.assert_process_still_running()}")
        print(f"Service.process.pid for chrome bot is : {bot.service.process.pid}")
        #subprocess.run(['kill',f'{bot.service.process.pid}'],shell=True)
        os.system(r'.\\kill.bat ' + str(bot.browser_pid))
        time.sleep(3)
        
        bot.quit()
    lim4loop = 50
    if init_page != 0 and start_list[0] != 0:
        lim4loop  = start_list[1] - start_list[0]   
    print(f" While loop will run until i  = {lim4loop}") 
    for page in start_list:
            logging.getLogger("selenium.webdriver.remote.remote_connection").propagate = False
            logging.getLogger("urllib3.connectionpool").propagate = False
            with NCBI_Crawler() as bot:
                bot.start_browser(Keyword_input,s_year,s_month,s_day,e_year,e_month,e_day)
                
                print(f"Session ID for Bot chrom ==> {bot.browser_pid}")
                bot.implicitly_wait(5)
                bot.getArticleLinks(page,filename,lim4loop)
                
                os.system(r'.\\kill.bat ' + str(bot.browser_pid))
                #subprocess.run(['kill',f'{bot.service.process.pid}'],shell=True)
                time.sleep(3)
                bot.quit()
            ChangeVPN()
            url_files  = f"{filename}" + f"_{str(page)}_urls.txt"
            url_out_file = f"{filename}" + f"_{str(page)}_urls.csv"
            df = pd.read_csv(url_files,header=None)
            df.drop_duplicates(inplace=True)
            df.to_csv(url_out_file,lineterminator="\n" ,sep=",", header=None, index=False)
            os.remove(url_files)
            
            run_spider(filename,page)
            ChangeVPN()
            time.sleep(20)
            
    
    
    
    
    