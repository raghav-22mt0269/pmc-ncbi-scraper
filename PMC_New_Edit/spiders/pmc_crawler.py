
######################################################
import scrapy
import scrapy.utils.misc
import scrapy.core.scraper
def warn_on_generator_with_return_value_stub(spider, callable):
    pass


scrapy.utils.misc.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub
scrapy.core.scraper.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub
import pandas as pd
from fuzzywuzzy import fuzz
#from ncbi_pmc.selenium_driver.selenium_part import NCBI_Crawler

class PmcCrawlerSpider(scrapy.Spider):
    name = "pmc_crawler"
    allowed_domains = ["https://www.ncbi.nlm.nih.gov"]

    def __init__(self, name=name, filename = None, page_no = None, **kwargs):
        super().__init__(name, **kwargs)
        print(f"Filename in class Spider is {filename}")
        #print(f"User Agent for Scrapy is --> {agent}")
        #self.agent = {"User-Agent": agent}
        self.rename_file = filename + "_" + str(page_no)
        #rename_file = filename + "_" + str(page_no)
    def start_requests(self):
        super().start_requests()
        
        with open(f"{self.rename_file}" + "_urls.csv", "r", encoding="utf-8", newline="") as f:
            start_urls = [url.strip() for url in f.readlines()]

        for url in start_urls:
            yield scrapy.Request(url, callback=self.parse,)#headers=self.headers
    

        
    @classmethod    
    def update_settings(cls, settings):
            settings.setdefault("FEEDS",{}).update(cls.custom_settings)
            #settings.setdefault("LOG_FILE",{}).update(cls.custom_settings)           
    def parse(self, response, **kwargs):
        main_div_xpath = '//div[@id="article-1aff-info"]'
        div_id_list = ["c001","FN1","awz401-cor1","cor1","ocz086-cor1","cor001","au1","CR1"]
        diff_id = ["cor001","au1","CR1","cor1"]
        corr_div_xpath = '//div[@id="corresp-1"]'
        contrib_span_xpath = '//div/span[starts-with(@id, "contrib-")]'
        correspond_xpath = '//div[contains(text(),"Correspond")]'
        div_strong_xpath = '//div/strong[starts-with(text(), "Correspond")]'
        div_span_xpath = '//div[@id = "CR1"]'
        #div_cor1_xpath = '//div[@id="cor]'
        div_xpath = '//div[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "correspond")]/a/@data-email'
        pmcid_xpath = '//div[@class = "fm-citation-pmcid"]/child::span[2]/text()'
        title_xpath = '//h1[@class="content-title"]/text()'
        headers = ["PMCID","emails","names"]
        
            
        pmcid = response.xpath(pmcid_xpath).get()
        title = response.xpath(title_xpath).get()
        names = response.xpath('//div[@class = "contrib-group fm-author"]/a[@co-class="co-affbox"]/text()').getall()
        
        try:
            if response.xpath(main_div_xpath+'//child::p/child::span[@class="fm-affl"][2]/a/@data-email'):
                    p_elements = response.xpath(main_div_xpath + '/child::p')
                    for p in p_elements:
                        email = p.xpath('.//child::span[@class="fm-affl"][2]/a/@data-email').get()
                        name = p.xpath('.//child::span[@class="fm-affl"][1]/text()').get()
                        
                        if email:
                            yield {
                                "PMCID":pmcid+"MAIN_DIV",
                                #"Title":title,
                                "emails": email[::-1],
                                "names": name.replace(",", "", -1) if name else None,
                                "Match_Score": 100
                            }
                        else:
                            results = self.matchNames_case(response=response,pmc_id=pmcid,heading=title,condtn = "_MainDiv")
                            for result in results:
                                yield result
            elif response.xpath(contrib_span_xpath+'/a/@data-email'):
                    span_id = response.xpath(contrib_span_xpath)
                    for span in span_id:
                        
                        email = span.xpath('.//a/@data-email').get()
                        name = span.xpath('.//text()').get()
                        
                        if email:
                            yield {
                                "PMCID":pmcid+"Contrib",
                               # "Title":title,
                            "emails": email[::-1],
                            "names": name.replace(":","",-1) if name else None,
                            "Match_Score": 100
                        }
                        else:
                            results = self.matchNames_case(response=response,pmc_id=pmcid,heading=title,condtn = "_Contrib")
                            for result in results:
                                yield result
            elif response.xpath('//img[@src = "/corehtml/pmc/pmcgifs/corrauth.gif"]'):
                    email = response.xpath('//a[@href="mailto:dev@null"]/@data-email').get()
                    name = response.xpath('//img[@src = "/corehtml/pmc/pmcgifs/corrauth.gif"]/parent::*/preceding-sibling::a[1]/text()').get()
                    
                    if email:
                            yield {
                                "PMCID":pmcid+"envelop",
                               # "Title":title,
                            "emails": email[::-1],
                            "names": name if name else None,
                            "Match_Score": 100
                        }
            elif response.xpath(div_xpath):
                e_res = response.xpath(div_xpath).getall()
                if e_res:
                    
                    email_s = [e[::-1] for e in e_res]
                    emails = set(email_s)
                    emails = list(emails)
                    matching_tuples = [max([(fuzz.token_set_ratio(i.split("@")[0],j),j )for j in names]) for i in emails]
                    match_score , fuzzy_match = map(list, zip(*matching_tuples))   
                    df=pd.DataFrame({"PMCID":pmcid+"Fuzzy_corresp", "emails":emails,"names":fuzzy_match,"Match_Score":match_score})#"Title":title,
                    results =  df.to_dict("records")
                    for result in results:
                        yield result 
                else:
                    results = self.matchNames_case(response=response,pmc_id=pmcid,heading=title,condtn = "_corresp")
                    for result in results:
                        yield result 
            elif response.xpath('//div[contains(text(),"-mail:")]/text()').re(r"[A-Za-z0-9._+%-]+@[a-zA-Z0-9]+\.[a-z.]+"):
                
                    e_res = response.xpath('//div[contains(text(),"-mail:")]/text()').re(r"[A-Za-z0-9._+%-]+@[a-zA-Z0-9]+\.[a-z.]+")
                    
                    email_s = [e for e in e_res if e != "journals.permissions@oup.com"]
                    nam_s = [name for name in names]
                    if email_s:
                        emails = set(e_res)
                        emails = list(emails)
                        matching_tuples = [max([(fuzz.token_set_ratio(i.split("@")[0],j),j) for j in nam_s]) for i in emails]
                        match_score, fuzzy_match = map(list,zip(*matching_tuples))
                        df=pd.DataFrame({"PMCID":pmcid+"Fuzzy", "emails":emails,"names":fuzzy_match,"Match_Score":match_score}) #"Title":title,
                        results =  df.to_dict("records")
                        for result in results:
                            yield result
                    else:
                        results = self.matchNames_case(response=response,pmc_id=pmcid,heading=title, condtn = "_FuzzyText")
                        for result in results:
                            yield result
            else:
                results = self.matchNames_case(response=response,pmc_id=pmcid,heading=title, condtn = "_elseLoop")
                for result in results:
                    yield result
                
            
        except Exception as e:
            for id in div_id_list:
                res = response.xpath(f'//div[@id="{id}"]')
                if res:
                    e_mail = res.xpath('.//a/@data-email').getall()
                    if e_mail:
                        n_res = res.xpath('.//text()').getall()
                        
                        for email in e_mail:
                                for name in n_res:
                                    if "Corresspond" in name and ":" in name:
                                        n = name.split(":")[1]
                                        yield {
                                                "PMCID":pmcid+"DIV_ID","emails":email[::-1],"names":n if n else None,
                                                "Match_Score": 100
                                            } #"Title":title,
                                for name in names:
                                    if name.lower() in email[::-1].split("@")[0]:
                                        yield{
                                            "PMCID":pmcid+"Match_DIV","emails":email[::-1],"names":name if n else None,
                                                "Match_Score": 100
                                        }#"Title":title,
        
            
    def matchNames_case(self,response,pmc_id,heading,condtn):
        e_res = response.xpath('//a[@href = "mailto:dev@null"]/@data-email')
        n_res = response.xpath('//div[@class = "contrib-group fm-author"]/a/text()')
        email_s = [e.get()[::-1] for e in e_res]
        names = [name.get() for name in n_res]
        emails = set(email_s)
        emails = list(emails)
        match_tuple = [max([(fuzz.token_set_ratio(i.split("@")[0],j),j) for j in names]) for i in emails]
        match_scores, fuzzy_match = map(list, zip(*match_tuple))
        df = pd.DataFrame({"PMCID":pmc_id+"ElseFuzzy"+condtn,"emails":emails,"names":fuzzy_match,"Match_Score":match_scores})#"Title":heading,
        results = df.to_dict("records")
        return results
        
    
