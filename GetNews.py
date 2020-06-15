# libraries
import os
import time
import random
import datetime
import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup as bs4

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/83.0.4103.97 Safari/537.36"
}
domain = "https://news.ltn.com.tw/"
query = "search?keyword={keyword}&conditions={condition}&start_time={ST}&end_time={ET}"


def start_query(keyword: str, condition: str, start_time: datetime.date, end_time: datetime.date):
    url = domain + query.format(keyword=keyword, condition=condition, ST=start_time, ET=end_time)
    print(f"URL: {url}\n")
    try:
        web_session = requests.session()
        res = web_session.get(url, headers=headers)

        soup = bs4(res.text, "html.parser")
        get_news_list(soup)
    except Exception as e:
        print("\n------ERROR----->")
        print(f"Catch an Exception: {e}")
        print("<------ERROR-----\n")
    pass


def get_news_list(soup: bs4):
    # print(f"{soup}")
    news_list = soup.select("a[class='tit']")
    for news in news_list:
        print(f"News: {news.text}\nLink: {news.attrs['href']}\n\n")
        print(f"{news.attrs['href'].split('/')[-3]}")
        if news.attrs['href'].split("/")[-3] == 'business':
            get_each_news(news.text, news.attrs['href'])
            time.sleep(random.randint(3, 7))
    pass


def get_each_news(news_title: str, news_link: str):
    try:
        web_ss = requests.session()
        res = web_ss.get(news_link, headers=headers)
        soup = bs4(res.text, "html.parser")
        # print(f"{soup}")
        get_each_news_content(news_title, soup)
    except Exception as e:
        print(f"Catch an Exception: \nTitle: {news_title}\nMSG: {e}\n\n")
    pass


def get_each_news_content(title:str, soup: bs4):
    all_content = ''
    content_list = soup.findAll("p", attrs={'class': None})
    for content in content_list:
        # print(f"{content.text}")
        if '一手掌握經濟脈動' in content.text:
            break
        elif '示意圖' in content.text or len(content.text) <= 1:
            continue
        else:
            all_content += content.text
    print(f"{all_content}")
    write_to_file(title, all_content)
    pass


def write_to_file(title: str, content: str):
    file_path = "./News/"
    file_name = ''
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path, exist_ok=True)
            
        file_name = sanitize_filename(title.replace(" ", ""))
    except IOError as e:
        print(f"Write Into File Error:\nTitle: {title}\nMSG: {e}")
    finally:
        print(f"\nWrite Into: {file_path+file_name+'.txt'}")
        if len(file_name) > 0:
            with open(file_path+file_name+".txt", "w+", encoding='utf-8') as f:
                f.write(content)
                f.close()
            print(f"\n-----Finished-----\n\n")
    pass


now = datetime.datetime.now()
start_query(keyword="台積電",
            condition="and",
            start_time=now.date() - datetime.timedelta(days=30 * 3),
            end_time=now.date())
