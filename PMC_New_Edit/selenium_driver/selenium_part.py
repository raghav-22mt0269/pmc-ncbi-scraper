from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, SessionNotCreatedException,ElementNotInteractableException
import time
import subprocess

import undetected_chromedriver as browser
import os, logging, random

BROWSER_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
class NCBI_Crawler(browser.Chrome):
    def __init__(self, options: Options = None, service: Service = None):
        
        
        #ua = UserAgent()
        #user_agent = ua.random
        #print(user_agent)
        
        
        
        self.options = browser.ChromeOptions()
        self.options.add_argument("--disable-lazy-loading")
        self.options.add_argument("--disable-print-preview")
       
        self.options.add_argument("--disable-stack-profiler")
        self.options.add_argument("--disable-background-networking")
        
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("excludeSwitches=enable-automation")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-browser-side-navigation")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-popup-blocking")
        
        self.options.add_argument("--disable-crash-reporter")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-logging")
        
        
               
        super(NCBI_Crawler, self).__init__(options = self.options,browser_executable_path=BROWSER_PATH,
                                            suppress_welcome=True,user_multi_procs=True,debug=True,
                                           log_level=2)
        self.maximize_window()
        logging.basicConfig(filename=f'Selenium_part_.log', filemode='w', level=logging.DEBUG)
        #print(f" using logger it prints ==> {logging.Logger.findCaller(self)}")
        #logging.Logger.removeHandler(hdlr=self)
        #logging.getLogger().propagate = False
    def __exit__(self,exc_type , exc_val, exc_to):
          self.stop_client()
          self.service._terminate_process()
          time.sleep(2)
            #self.quit() 
          pass
    def ChangeVPN(self):
        countries = ["Georgia","Serbia","Moldova",'"North Macedonia"',"Jersey","Monaco","Slovakia",
                     "Slovenia","Croatia","Albania","Cyprus","Liechtenstein","Malta","Ukraine",
                     "Belarus","Bulgaria","Hungary","Luxembourg","Montenegro","Andorra",
                     '"Czech Republic"',"Estonia","Latvia","Lithuania","Poland","Armenia","Austria",
                     "Portugal","Greece","Finland","Belgium","Denmark","Norway","Iceland","Ireland",
                     "Spain","Romania","Italy","Sweden","Turkey","Singapore",
                     "Australia",'"South Korea - 2"',"Malaysia","Pakistan",'"Sri Lanka"',"Kazakhstan",
                     "Thailand","Indonesia",'"New Zealand"','"Taiwan - 3"',"Cambodia","Vietnam","Macau",
                     "Mongolia","Laos","Bangladesh","Uzbekistan","Myanmar","Nepal","Brunei","Bhutan",
                     '"United Kingdom"', '"United States"',"Japan", "Germay", '"Hong Kong"', "Netherlands",
                     "Switzerland","Algeria","France","Egypt"] 
        b = random.choice(countries)
        print(f"Selected Country is {b}")
        
        process = subprocess.Popen(["powershell",".\expresso.exe", "connect", "--change",
                            b],shell=True)
        result = process.communicate()[0]
        print(result)        
    def start_browser(self,keyword,s_year,s_month,s_day,e_year,e_month,e_day):  # keyword
        #keyword_input = input("Enter the Keyword:")
        keyword_input = keyword
        try:
            self.get(f"https://www.ncbi.nlm.nih.gov/pmc/?term={keyword_input}")
            WebDriverWait(self, 60).until(EC.presence_of_element_located((By.ID,"display_set" ))).click()
            time.sleep(3)
            
            WebDriverWait(self, 60).until(EC.element_to_be_clickable((By.ID, "ps100"))).click()
            WebDriverWait(self,60).until(EC.element_to_be_clickable((By.ID, "facet_date_rangepubdate"))).click()
            #start_year = WebDriverWait(self,5).until(EC.presence_of_element_located((By.ID, "facet_date_st_yearpubdate")))
            WebDriverWait(self, 60).until(EC.presence_of_element_located((By.ID,"facet_date_range_clearpubdate" ))).click()
            
            #self.find_element(By.ID, "facet_date_range_clearpubdate").click()
            start_year = self.find_element(By.ID, "facet_date_st_yearpubdate")
            start_year.clear()
            start_year.send_keys(s_year)
            #time.sleep(20)
            start_mon = self.find_element(By.ID, "facet_date_st_monthpubdate")
            start_mon.clear()
            start_mon.send_keys([Keys.BACKSPACE] * 5 )
            start_mon.send_keys(int(s_month))
            start_day = self.find_element(By.ID, "facet_date_st_daypubdate")
            start_day.clear()
            start_day.send_keys(int(s_day))
            end_year = self.find_element(By.ID, "facet_date_end_yearpubdate")
            end_year.send_keys(e_year)
            end_month = self.find_element(By.ID, "facet_date_end_monthpubdate")
            end_month.clear()
            end_month.send_keys([Keys.BACKSPACE] * 5 )
            end_month.send_keys(int(e_month))
            end_day = self.find_element(By.ID,"facet_date_end_daypubdate")
            end_day.clear()
            end_day.send_keys(int(e_day))
            #time.sleep(20)
            self.find_element(By.ID, "facet_date_range_applypubdate").click()
        except (NoSuchElementException, TimeoutException,ElementNotInteractableException) as e:
            print(f"#########  NoSuchElementException, TimeoutException or ElementNotInteractableException Occured ... {str(e)}  ########")
            print("#########  Refereshing the page ... ########")
            
            self.refresh()
            self.start_browser(keyword,s_year,s_month,s_day,e_year,e_month,e_day)
        except SessionNotCreatedException:  
             print("########### SessionNotCreatedException Occured ##########")
             print("########### Refresh the Driver by first quitting ########")
             self.quit()
             NCBI_Crawler(browser.Chrome).__init__(options = self.options,browser_executable_path=os.getcwd()+BROWSER_PATH,
                                            suppress_welcome=True,debug=True,keep_alive=False,
                                            version_main=114,log_level=2)
        #filename = input("Enter File Name: ")
    def Page_Ranges(self):
        pageno = WebDriverWait(self,60).until(EC.presence_of_element_located((By.ID , "pageno"))).get_attribute("last")
        
        extreme_left = int(pageno)//100
        #works for 500 paging in loop 
        #range4loop = [500*i for i in range(int(extreme_left/2) + 1)]
        if int(pageno)%100//10 < 5:
            
            range4loop = [50*i for i in range((extreme_left *2) + 1)]
            print(f"range for loop is ==> {range4loop}")
            return range4loop
        else:
            range4loop = [50*i for i in range((extreme_left + 1)*2)]
            print(f"range for loop is ==> {range4loop}")
            return range4loop
    
    def Send_pageNO(self,page_Num):
        page=self.find_element(By.ID, 'pageno')
        page.clear()
        actions = ActionChains(self)
        
        actions.move_to_element(self.find_element(By.NAME, 'EntrezSystem2.PEntrez.PMC.Pmc_ResultsPanel.Entrez_Pager.cPage')).perform()
        actions.send_keys_to_element(page,f"{str(page_Num)}").key_down(Keys.ENTER).perform()
        time.sleep(2)
                
    def getArticleLinks(self, start_page,filename, r_lim):        #,s_year,s_month,s_day,e_year,e_month,e_day
        #offset_values = page_list
        #for i in range(offset_values):
        
        print("#"*20)
        print(filename)    
            #start_page = i#input("which page number you want to start with?")
        #self.start_browser(filename,s_year,s_month,s_day,e_year,e_month,e_day)
        pagestart=self.find_element(By.ID, 'pageno')
        pagestart.clear()
        actions = ActionChains(self)
        
        actions.move_to_element(self.find_element(By.NAME, 'EntrezSystem2.PEntrez.PMC.Pmc_ResultsPanel.Entrez_Pager.cPage')).perform()
        actions.send_keys_to_element(pagestart,f"{str(start_page + 1)}").key_down(Keys.ENTER).perform()
        time.sleep(2)
        #assert self.find_element(By.ID,"pageno").get_attribute("value") == start_page
    
        rename_file = filename + "_"+str(start_page)
        i = 0
        while i < r_lim:  #r_lim
            try:
                page_value = int(self.find_element(By.ID , "pageno").get_attribute("value"))
                last_value = int(self.find_element(By.ID , "pageno").get_attribute("last"))
                """if i in offset:
                    self.ChangeVPN()
                    time.sleep(5)"""    
                if (start_page + i + 1) == last_value:
                    print(f"{start_page + i + 1} matches with the pageno last value ==> {last_value}")
                
                    break  
                elif (start_page + i + 1) == page_value:
                    print(f"{start_page + i + 1} matches with the pageno value ==> {int(self.find_element(By.ID , 'pageno').get_attribute('value'))}")
                    
                    elements = self.find_elements(By.XPATH, '//div[@class="title"]/a[@href]')
                    print(f"Page {start_page+i+1} contains {len(elements)} articles!")
                    for element in elements:
                        with open(f"{rename_file}"+"_urls.txt", "a+",encoding="utf-8",newline="\n") as f:
                            f.writelines(element.get_attribute("href")+'\n')
                        
                    WebDriverWait(self,60).until(EC.element_to_be_clickable((By.XPATH,"//div[@class = 'pagination']/a[@accesskey = 'k']"))).click()
                    i += 1
                elif (start_page +  i + 1) > page_value:
                    print(f"{start_page + i + 1} does not match with the pageno value ==> {page_value}")
                    num_page = start_page + i + 1
                    self.Send_pageNO(num_page)
                    print(f"{start_page + i + 1} matches with the pageno value ==> {int(self.find_element(By.ID , 'pageno').get_attribute('value'))}")
                    
                    elements = self.find_elements(By.XPATH, '//div[@class="title"]/a[@href]')
                    print(f"Page {num_page} contains {len(elements)} articles!")
                    for element in elements:
                        #print(element.get_attribute("href"))
                        with open(f"{rename_file}"+"_urls.txt", "a+",encoding="utf-8",newline="\n") as f:
                            f.writelines(element.get_attribute("href")+'\n')
                        #links.append({"urls":element.get_attribute("href")})
                    WebDriverWait(self,60).until(EC.element_to_be_clickable((By.XPATH,"//div[@class = 'pagination']/a[@accesskey = 'k']"))).click()
                    i += 1
                    #i -= 1
                    continue
                else : 
                    #i += 1
                    self.refresh()
                    continue
                    #self.find_element(By.XPATH, "//div[@class = 'pagination']/a[@accesskey = 'k']").click()    
            except Exception as e:
                print(f"Exception error OCCURRED during Article links retrieval: {str(e)}")
                print("Refreshing...")
                self.refresh()  
                
            finally:
                if i%50 == 0:
                    self.ChangeVPN()
                    time.sleep(10)
        print(f"Articles Links were extracted from page {start_page + 1} to page {start_page + 50}")
         

    
