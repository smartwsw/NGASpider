# -*- coding:utf-8 -*-
from urllib import request
from urllib import error
from bs4 import BeautifulSoup
import http.cookiejar as cookiejar
import re
import time
import sys
import os

base_url = "https://bbs.nga.cn/"


def cookie_to_dict(cookie):
    cookie_dict = {}
    items = cookie.split(';')
    for item in items:
        key = item.split('=')[0].replace(' ', '')
        value = item.split('=')[1]
        cookie_dict[key] = value
    return cookie_dict


def make_page(url):
    try:
        cookie = cookiejar.MozillaCookieJar()
        cookie.load("cookie.txt", ignore_discard=True, ignore_expires=True)
        handler = request.HTTPCookieProcessor(cookie)
        opener = request.build_opener(handler)
        response = opener.open(url)
        page = response.read()
        soup = BeautifulSoup(page, "html.parser", from_encoding='gb18030')
        return soup
    except error.HTTPError as e:
        print(e.reason)
        return None

def print_reply(reply):
    sz = os.get_terminal_size()
    n = 75
    buffer = [ reply[i:i+n] for i in range(0, len(reply), n) ]
    first_line = True
    for buf in buffer:
        if first_line:
            print("|- {}".format(buf))
            first_line = False
        else:
            print("|  {}".format(buf))


class LowGA:
    threads = []

    def __init__(self, url, fid):
        self.base_Url = url
        self.fid = fid

    def get_list(self):
        threads = []
        url = self.base_Url + "thread.php?fid=" + self.fid
        soup = make_page(url)
        for thread in soup.find_all('tbody'):
            ele = thread.find_all('td')
            threads.append({"title": ele[1].text.strip("\n"), "link": ele[1].a['href']})
        self.threads = threads
        return threads

    def get_reply(self, url):
        replies = []
        _len = 20
        page_num = 1
        while True:
            thread_url = self.base_Url + url + "&page=" + str(page_num)
            soup = make_page(thread_url)
            raw_replies = soup.find_all(id=re.compile(r"post1strow\d+"))
            _len = len(raw_replies)
            for reply in raw_replies:
                user = reply.find(id=re.compile(r"postauthor\d+"))['href']
                content = reply.find(id=re.compile(r"postcontent\d+")).text
                if page_num > 1:
                    if content == replies[-20]['content']:
                        return replies
                replies.append({"content": content, "user": user})
            if _len < 20:
                break
            page_num += 1
        return replies


def main():
    if len(sys.argv) == 2:
        for reply in LowGA(base_url, "549").get_reply(sys.argv[1]):
            print_reply(reply['content'])
        exit()
    bbs = LowGA(base_url, "549")
    thds = bbs.get_list()
    for thread in thds:
        print("+-{}\t\t{}".format(thread['title'], base_url + thread['link']))
        for reply in bbs.get_reply(thread['link']):
            print_reply(reply['content'])
        print("\_____________________________________________________________________________")
        input("Press Enter to continue...")

if __name__ == "__main__":
    main()
