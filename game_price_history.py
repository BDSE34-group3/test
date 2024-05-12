import requests
from bs4 import BeautifulSoup as bs


def request_url(url):
    #首頁網址
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
    cookie = {
        "cf_clearance":"Rwwn4ULzOFnumFngY_fyl6OyXa950UG5NqPxrO6XSjg-1715530138-1.0.1.1-UVgt1FhAPuK.5C7FzbWfWwo5bcBqGkalA80vj7y9nprXxkJiweA1lDelKxB3l3ks_pTa2H_v4FqFFSW_SH6BUg",
        
        "__cf_bm":"k2UYsNakpy2MNJlStGgl8f_3OgRJf9IH499sZg9zZqE-1715530148-1.0.1.1-vVRw3EGB3ItXvJO6SHM0HL68qsR18mV3PoNFpBuBsN_QgBI1EOd.he2ctOOZMGeXy3gDq.bMvye17AxzBtrpBA"
    }
    req = requests.get(url, headers=headers, cookies=cookie)
    print(req.json())

        
    return req.text

# def soup(html_text):
#     soup = bs(html_text, features="html.parser")
#     for a in soup.select('a'):
#         if a.has_attr('href'):
#             print(a['href'])


  
if __name__ == '__main__':
    request_url('https://steamdb.info/api/GetGraphMax/?appid=730')

    
    
    






