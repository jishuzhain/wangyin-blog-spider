# -*- coding:utf-8 -*-
import os
import re
import time
import logging
import pdfkit
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>

"""

def parse_url_to_html(url, name):
    """
    解析URL，返回HTML内容
    :param url:解析的url
    :param name: 保存的html文件名
    :return: html
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # 正文
    body = soup.find_all(class_="inner")[0]
    print body
    print "----------------------------------------------------------------------"
    # 标题
    title = soup.find('h2').get_text()
    print title

    # 标题加入到正文的最前面，居中显示
    center_tag = soup.new_tag("center")
    title_tag = soup.new_tag('h1')
    title_tag.string = title
    center_tag.insert(1, title_tag)
    body.insert(1, center_tag)
    html = str(body)
    # body中的img标签的src相对路径的改成绝对路径
    pattern = "(<img .*?src=\")(.*?)(\")"

    def func(m):
        if not m.group(3).startswith("http"):
            rtn = m.group(1) + "http://www.yinwang.org" + m.group(2) + m.group(3)
            return rtn
        else:
            return m.group(1) + m.group(2) + m.group(3)

    html = re.compile(pattern).sub(func, html)
    html = html_template.format(content=html)
    #html = html.encode("utf-8")  # 这里存在问题，解析错误
    with open(name, 'wb') as f:
        f.write(html)
    return name


def get_url_list():
    """
    获取所有URL目录列表
    :return:
    """
    response = requests.get("http://www.yinwang.org/")
    soup = BeautifulSoup(response.content, "html.parser")
    menu_tag = soup.find_all(class_="list-group")[0]
    urls = []
    for li in menu_tag.find_all("li"):
        url = "http://www.yinwang.org" + li.a.get('href')
        urls.append(url)
    print len(urls)  #134
    return urls


urls = get_url_list()
parse_url_to_html("http://www.yinwang.org/blog-cn/2018/03/01/truth",
                  "http://www.yinwang.org/blog-cn/2018/03/01/truth" + ".html")
