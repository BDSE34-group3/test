import requests
from bs4 import BeautifulSoup 
import warnings
import requests
import pandas as pd
import re
import logging
warnings.filterwarnings("ignore")


def set_logger():

    # 基本設定
    logger = logging.getLogger("crawler_591_log")

    # 設定等級
    logger.setLevel(logging.INFO)

    # 設定輸出格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")

    # 儲存在 log 當中的事件處理器
    file_handler = logging.FileHandler('house_price_log/591_crawler.log', mode='a', encoding='utf-8') # a: append, w: write
    file_handler.setFormatter(formatter)

    # 輸出在終端機介面上的事件處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 加入事件
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

def get_info(url):
    #reqrest案件html，透過soup解析(591一定要加hearder)
    headers={'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    res=requests.get(url, headers = headers)
    if res.status_code == 200:
        soup=BeautifulSoup(res.text,'html.parser')

        #############開始找出重要變數#############
        single_entry = {} #一筆row data，全部存在字典中
        #因變數欄位在不同案件中可能會沒有，用for找出區塊有的欄位，再填入字典
        #########################################
        try:
            #總價
            info_price_num = soup.select_one('span.info-price-num').text
            # single_entry['總價'] = re.search(r'(\s+)?(\S+)(\s+)?萬元', info_price_num)
            info_price_num_list = re.split(r'\s+', info_price_num) #可能要切萬元前面字串

            single_entry['總價'] = info_price_num_list[0]
            single_entry['total_price_list'] = info_price_num_list
        except:
            logger.error(f'url:{url} ;  問題:總價部分有問題')


        try:
            #格局、屋齡、權狀坪數
            top_right_block_titles_tags_1 = soup.select('div.info-floor-value')
            for num, item in enumerate(top_right_block_titles_tags_1):
                single_entry[item.text] = soup.select('div.info-floor-key')[num].text

            #樓層、朝向、社區、地址
            top_right_block_titles_tags_2 = soup.select('span.info-addr-key') #找出這個區塊有哪些項目
            for num, item in enumerate(top_right_block_titles_tags_2):
                single_entry[item.text] = soup.select('.info-addr-value')[num].text #對應tilte與對應值放入dict
        except:
            logger.error(f'url:{url} ;  問題:網頁右上房屋資訊有問題')


        try:
            #(房屋介紹)透過迴圈取出內容放入single_entry，屋況特色不在範圍內
            for item in soup.select('div.detail-house-box'):
                if item.select('div.detail-house-value'):
                    if item.select('div.detail-house-key'):
                        bottom_block_titles = item.select('div.detail-house-key')
                        for num, item_title in enumerate(bottom_block_titles):
                            single_entry[item_title.text] = item.select('div.detail-house-value')[num].text
                    else:
                        temp = []
                        for value in item.select('div.detail-house-value'):
                            temp.append(value.text)
                        single_entry[item.select('div.detail-house-name')[0].text] = temp
                        
                
                else :
                    temp = []
                    for value in item.select('div.detail-house-life'):
                        temp.append(value.text)
                    single_entry[item.select('div.detail-house-name')[0].text] = temp
                        
            #屋況特色(格式很亂，不撈)
            # if soup.select('div#detail-feature-text'):
            #     single_entry['屋況特色'] = soup.select('div#detail-feature-text')[0].text
            #     soup.select('div#detail-feature-text')[0].text
        except:
            logger.error(f'url:{url} ;  問題:網頁下方房屋介紹有問題')
    else:
        logger.error(f'url:{url}, res連線失敗')
    
    return single_entry


if __name__ == '__main__':
    url='https://sale.591.com.tw/home/house/detail/2/15652838.html'
    logger = set_logger
    row_data = get_info(url)#回傳一筆raw data













