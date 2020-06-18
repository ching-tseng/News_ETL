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
query = "search?keyword={keyword}&conditions={condition}&start_time={ST}&end_time={ET}&page={page}"


def start_query(query_list: dict):
    url = domain + query.format(keyword=query_list["keyword"],
                                condition=query_list["condition"],
                                ST=query_list["start_time"],
                                ET=query_list["end_time"],
                                page=query_list["page"])
    print(f"URL: {url}\n")
    # try:
    web_session = requests.session()
    res = web_session.get(url, headers=headers)
    soup = bs4(res.text, "html.parser")
    get_news_list(soup, query_list)
    # except Exception as e:
    #     print("\n------ERROR----->")
    #     print(f"Catch an Exception: {e}\nURL:{url}")
    #     print("<------ERROR-----\n")
    pass


def get_news_list(soup: bs4, query_list: dict):
    news_class = ['business', 'weeklybiz', 'politics']
    news_list = soup.select("ul[class='searchlist boxTitle'] > li")
    for news in news_list:
        pub_time = news.select("span")[0].text
        article = news.select("a")[0]
        print(f"News: {article.text}\n"
              f"Link: {article.attrs['href']}\n"
              f"Class: {article.attrs['href'].split('/')[-3]}")
        if article.attrs['href'].split("/")[-3] in news_class:
            news_id = article.attrs['href'].split("/")[-1]
            if not isNewsExists(news_id, pub_time):
                title = article.text
                link = article.attrs['href']
                get_each_news(news_id, pub_time, title, link)
                time.sleep(random.randint(2, 5))

    next_page_if_exists(soup, query_list)
    pass


def isNewsExists(news_id: int, pub_time: str):
    year = pub_time.split("-")[0]
    file_path = f"./News/{year}/{news_id}.txt"
    try:
        return os.path.exists(file_path)
    except Exception as e:
        print(f"Check News is Exists: {e}")
        return False


def next_page_if_exists(soup: bs4, query_list: dict):
    p_next = soup.select("a[data-desc='下一頁']")
    if len(p_next) > 0:
        query_list["page"] = p_next[0].attrs["href"].split("=")[-1]
        start_query(query_list)
    else:
        query_list["end_time"] = query_list["start_time"]
        query_list["start_time"] = query_list["start_time"] - datetime.timedelta(days=30 * 3)
        query_list["page"] = 1
        if query_list["start_time"] < datetime.datetime(2019, 1, 1).date():
            print(f"Search start time: {query_list['start_time']}")
            print(f"\n-----Finished-----\n\n")
            return
        else:
            start_query(query_list)


def get_each_news(news_id: int, pub_time: str, title: str, link: str):
    # try:
    web_ss = requests.session()
    res = web_ss.get(link, headers=headers)
    soup = bs4(res.text, "html.parser")
    get_each_news_content(news_id, pub_time, title, link, soup)
    # except Exception as e:
    #     print(f"Catch an Exception: \nID: {news_id}\nMSG: {e}\n\n")
    pass


def get_each_news_content(news_id: int, pub_time: str, title: str, link: str, soup: bs4):
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
    # print(f"{all_content}")
    write_to_file(news_id, pub_time, title, link, all_content)
    pass


def write_to_file(news_id: int, pub_time: str, title: str, link: str, content: str):
    current_year = pub_time.split("-")[0]
    file_path = f"./News/{current_year}/"
    file_name = f"{news_id}"
    try:
        os.makedirs(file_path, exist_ok=True)
        file_name = sanitize_filename(file_name)
    except IOError as e:
        print(f"Write Into File Error:\nTitle: {title}\nMSG: {e}")
    finally:
        print(f"\nWrite Into: {file_path + file_name + '.txt'}\n")
        if len(file_name) > 0:
            with open(file_path + file_name + ".txt", "w+", encoding='utf-8') as f:
                f.write(f"標題: {title}\n")
                f.write(f"時間: {pub_time}\n")
                # f.write(f"記者: {reporter}\n")
                f.write(f"內文: {content}\n")
                f.close()
    pass


# Last Disconnect2019-09-22 ~ 2019-12-21
now = datetime.datetime(2019, 12, 21).date()
start_time = time.time()
query_list = {"keyword": "台積電", "condition": "and", "start_time": now - datetime.timedelta(days=30 * 3),
              "end_time": now, "page": 1}
start_query(query_list)

