from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import json
import logging
from pprint import pprint

# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as bs
from time import sleep
import pandas as pd
    
def run_driver(url, proxy=None):
    try:
        #啟用瀏覽器工具選項
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')#最大化視窗
        options.add_argument('--disable-popup-blocking')#禁用彈出連結
        options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"')#修改瀏覽器產生header
        options.add_experimental_option('detach', True)#設定不自動關閉瀏覽器
        options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})#關閉通知彈跳

        options.set_capability("goog:loggingPrefs", {"browser": "ALL"})#為了console
        options.page_load_strategy = 'normal'

        

        # PROXY = "localhost:8080"
        # options.add_argument('--proxy-server=%s' % PROXY)
        # PROXY.new_har("test")
        
        #使用Chrome的Driver
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
        })#反爬蟲的網頁，會檢測瀏覽器的 window.navigator是否包含 webdriver 屬性，在正常使用瀏覽器的情況下，webdriver 屬性是 undefined，一旦使用了 selenium 函式庫，這個屬性就被初始化為 true，只要藉由 Javascript 判斷這個屬性，進行反爬蟲(將 webdriver 設定為 undefined)

        #訪問網頁
        driver.get(url)
        # print(PROXY.har)
        return driver
    except:
        print("連線失敗、異常")
    # finally:
    #     driver.quit()

def switch_to_flag(driver, flag):
    frame = driver.find_element(By.TAG_NAME, flag)
    driver.switch_to.frame(frame)
    return driver

def select_condition(driver, cities=[], start_year=None, start_month=None, end_year=None, end_month=None):
    #第一步先找出SELECT的縣市，內部有多少區，放進字典中
    cities_districts_info = {}
    for city in cities:
        select_element = driver.find_element(By.ID, "p_city")
        select_object = Select(select_element)
        select_object.select_by_value(city)
        sleep(3)

        html = driver.page_source
        soup = bs(html, 'html.parser')
        district_list = []
        for tag in soup.select('#p_town > option'):
            # district.get_text() #找出點選city後裡面的區
            if tag['value'] != '':
                district_list.append(tag['value'].strip())
        
        cities_districts_info[city] = district_list
        sleep(3)

    check_whether_searched = False
    data_url_list = []
    for key, values in  cities_districts_info.items():
        # #從這邊開始改
        for value in values:
            # try:
            if check_whether_searched == False:
                data_url_dict = {}
                data_url = click_condition_first(driver, key, value, start_year, start_month, end_year, end_month)
                logger.info(f'city{key}, district{value}, s_year{start_year}, s_month{start_month}, e_year{end_year}, e_month{end_month}, 成功')
                sleep(5)
                data_url_dict[value] = data_url
                data_url_list.append(data_url_dict)
                check_whether_searched = True
            
            else:
                data_url_dict = {}
                data_url = click_condition_not_first(driver, key, value)
                logger.info(f'city{key}, district{value}, s_year{start_year}, s_month{start_month}, e_year{end_year}, e_month{end_month}, 成功')
                data_url_dict[value] = data_url
                data_url_list.append(data_url_dict)
                sleep(5)

            # except:
            #     logger.error(f'city{key}, district{value}, s_year{start_year}, s_month{start_month}, e_year{end_year}, e_month{end_month}, 失敗')
    return data_url_list
        
def click_condition_first(driver, city, district, start_year, start_month, end_year, end_month):

    #第一個格子選縣市
    select_element = driver.find_element(By.ID, "p_city")
    select_object = Select(select_element)
    select_object.select_by_value(city)
    sleep(5)
    
    #第二個格子選地區
    select_element = driver.find_element(By.ID, "p_town")
    select_object = Select(select_element)
    select_object.select_by_value(district)
    sleep(1)

    #第三個格子時間(開始年、月)
    select_element = driver.find_element(By.ID, "p_startY")
    select_object = Select(select_element)
    select_object.select_by_value(start_year)

    select_element = driver.find_element(By.ID, "p_startM")
    select_object = Select(select_element)
    select_object.select_by_value(start_month)

    sleep(1)

    #第四個格子時間(開始年、月)
    select_element = driver.find_element(By.ID, "p_endY")
    select_object = Select(select_element)
    select_object.select_by_value(end_year)

    select_element = driver.find_element(By.ID, "p_endM")
    select_object = Select(select_element)
    select_object.select_by_value(end_month)

    #條件設完點選查詢
    driver.find_elements(By.CLASS_NAME, "btn-a")[1].click()
    
    #確認左下查詢結果tag出現後才繼續
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "price_table_info"))
    )
    
    json_url = get_json_url(driver)
    sleep(3)

    #查詢結果網址
    # get_json_url(driver)++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    return json_url

#要篩選的欄位會在第一次查詢後，html tag的id 會改變
def click_condition_not_first(driver, city, district):

    #第一個格子選縣市
    select_element = driver.find_element(By.ID, "l_city")
    select_object = Select(select_element)
    select_object.select_by_value(city)
    sleep(5)
    
    #第二個格子選地區
    select_element = driver.find_element(By.ID, "l_town")
    select_object = Select(select_element)
    select_object.select_by_value(district)
    sleep(1)

    #條件設完點選查詢
    driver.find_elements(By.CLASS_NAME, "btn-a")[1].click()
    
    #確認左下查詢結果tag出現後才繼續
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "price_table_info"))
    )
    
    #查詢結果網址
    json_url = get_json_url(driver)
    sleep(3)

    return json_url

def get_json_url(driver):
    cookies = []
    sleep(3)
    for request in driver.requests: 
        re_url = re.search('https:\/\/lvr\.land\.moi\.gov\.tw\/SERVICE\/QueryPrice\/[\S]+[==$]', request.url)
        if re_url:
            data_url = re_url.group()
            # response = requests.get(data_url)
            # if response.status_code == 200:
            #     data = response.json()
            # else:
            #     logger.error(f'json_url_獲取失敗, status_code{response.status_code}')
            break
    return data_url
    
def set_logger():
    '''
    Logging 設定
    '''
    # 基本設定
    logger = logging.getLogger("data_price_crawler")

    # 設定等級
    logger.setLevel(logging.INFO)

    # 設定輸出格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")

    # 儲存在 log 當中的事件處理器
    file_handler = logging.FileHandler('data_price_crawler.log', mode='a', encoding='utf-8') # a: append, w: write
    file_handler.setFormatter(formatter)

    # 輸出在終端機介面上的事件處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 加入事件
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def save_data_url_list(data_url_list, cities, start_year, start_month, end_year, end_month):
    name = ''
    for city in cities:
        name += city 
        
    with open(f'searched_json_url/{name}_start_{start_year}-{start_month}_end_{end_year}-{end_month}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data_url_list))


if __name__ == '__main__':
    #crawler_condition (t表示今天要撈的條件)
    cities_t = ['C']
    start_year_t = '113'
    start_month_t =  '1'
    end_year_t = '113'
    end_month_t = '2'

    logger = set_logger()#在需要的地方埋入資訊
    driver = run_driver("https://lvr.land.moi.gov.tw")
    driver = switch_to_flag(driver, 'frame')

    data_url_list = select_condition(driver, cities=cities_t, start_year=start_year_t, start_month=start_month_t, end_year=end_year_t, end_month=end_month_t)

    save_data_url_list(data_url_list, cities=cities_t, start_year=start_year_t, start_month=start_month_t, end_year=end_year_t, end_month=end_month_t)

    driver.quit()




