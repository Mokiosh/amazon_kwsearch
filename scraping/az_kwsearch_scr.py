"""This is a scraping program to get search result data on each kw"""

import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


today = datetime.datetime.today().strftime("%Y%m%d%p")
filename_sb = f"{today}_SB.csv"
filename_sp = f"{today}_SP.csv"
filename_og = f"{today}_OG.csv"
filename = [filename_sb, filename_sp, filename_og]

options = Options()
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument('--lang=ja-JP')
# options.add_argument("--disable-gpu")
# options.add_argument("--disable-extensions")
# options.add_argument("--proxy-server='direct://'")
# options.add_argument("--proxy-bypass-list=*")
# options.add_argument("--start-maximized")
# options.add_argument("--headless")
# options.add_argument('--headless') #doesnt work with headless..dont know why

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
URL = "https://www.amazon.co.jp/"
search_times = 1

sp_xpath = "//*[@data-component-type='sp-sponsored-result']/descendant::h2"
sp_asin_xpath = "//*[@data-component-type='sp-sponsored-result']" \
                "/../../../../div"
sb_xpath = "//*[@class='a-truncate-full a-offscreen']/../span"
sb_asin_xpath = "//*[@class='a-truncate-full a-offscreen']" \
                "/../../../../../div"
organic_xpath = "//*[@class='sg-col-4-of-12 s-result-item s-asin " \
                "sg-col-4-of-16 sg-col sg-col-4-of-20']/descendant::h2"
organic_asin_xpath = "//*[@class='sg-col-4-of-12 s-result-item s-asin " \
                "sg-col-4-of-16 sg-col sg-col-4-of-20']"

input_dir_path = 'az_kwsearch_scr/input_dir'
output_dir_path = 'az_kwsearch_scr/output_dir'
input_file = 'amazon_kwlist.csv'


def search_kw(kwd, URL, search_repeat):
    """Use chrome driver for scraping"""

    # connect to internet
    driver.get(URL)
    driver.implicitly_wait(10)
    driver.find_element_by_xpath("//*[@value='検索']").click()
    driver.implicitly_wait(10)

    # search keyword
    searchbox = driver.find_element_by_id("twotabsearchtextbox")
    searchbox.send_keys(kwd)
    driver.find_elements_by_class_name("nav-input")[1].click()
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located)

    # scraping data
    sb = driver.find_elements_by_xpath(sb_xpath)
    sb_asin = driver.find_elements_by_xpath(sb_asin_xpath)
    sp = driver.find_elements_by_xpath(sp_xpath)
    sp_asin = driver.find_elements_by_xpath(sp_asin_xpath)
    organic = driver.find_elements_by_xpath(organic_xpath)
    organic_asin = driver.find_elements_by_xpath(organic_asin_xpath)

    title = str(kwd).replace("'", "").replace("[", "").replace("]", "")
    sb_list = []
    sp_list = []
    og_list = []

    rank = 0
    for (name, asin) in zip(sb, sb_asin):
        temp_list = [today, title, f"try_{search_repeat}", "SBA", str(rank + 1)]
        sb_name_data = name.text.replace(",", "")
        sb_asin_data = asin.get_attribute("data-asin")
        temp_list.append(str(sb_asin_data))
        temp_list.append(sb_name_data)
        sb_list.append(temp_list)
        print(sb_list)
        rank += 1

    rank = 0
    for (name, asin) in zip(sp, sp_asin):
        temp_list = [today, title, f"try_{search_repeat}", "SPA", str(rank + 1)]
        sp_name_data = name.text.replace(",", "")
        sp_asin_data = asin.get_attribute("data-asin")
        if sp_asin_data is None:
            sp_asin_data = ""
        else:
            pass
        
        temp_list.append(sp_asin_data)
        temp_list.append(sp_name_data)
        sp_list.append(temp_list)
        rank += 1

    rank = 0
    for (name, asin) in zip(organic, organic_asin):
        temp_list = [today, title, f"try_{search_repeat}", "Organic", str(rank +
                                                                          1)]
        organic_result = name.text.replace(",", "")
        organic_asin = asin.get_attribute("data-asin")
        temp_list.append(organic_asin)
        temp_list.append(organic_result)
        og_list.append(temp_list)
        rank += 1

    return sb_list, sp_list, og_list


def get_data(csv):
    """Get search keyword data from CSV file"""

    items = []
    for l in open(csv):
        items.append(l)

    num_items = len(items)

    for i, line in enumerate(open(csv)):
        progress = int(i / num_items * 100)
        print(f'Getting results...: {progress}%', end='\r')
        yield line.strip().split(",")
    print()


def flatten_2d(data):
    """Flatten 3d list to 2d"""

    for block in data:
        for elem in block:
            yield elem


def make_list(l):
    """Convert raw scraping list to CSV optimized format"""

    flatten_list = list(flatten_2d(l))
    print(flatten_list)
    final_list = "\n".join(",".join(i) for i in flatten_list)
    print(final_list)
    return final_list


def write_csv(writing_list, filename):
    """Write CSV in output directory"""

    os.chdir(f'../../{output_dir_path}')
    for i, j in zip(writing_list, filename):
        with open(j, "w") as f:
            f.write(i)
    os.chdir(f'../../{input_dir_path}')


SB_list = []
SP_list = []
OG_list = []

os.chdir("input_dir")
current_repeat = 1
for kwd in get_data(input_file):
    while current_repeat < search_times + 1:
        sb_list, sp_list, og_list = search_kw(kwd, URL, current_repeat)
        SB_list.append(sb_list)
        SP_list.append(sp_list)
        OG_list.append(og_list)
        current_repeat += 1
    current_repeat = 1
driver.close()

print(SP_list)

writing_list = \
    [make_list(SB_list), make_list(SP_list), make_list(OG_list)]

write_csv(writing_list, filename)
print('Done Scraping')
