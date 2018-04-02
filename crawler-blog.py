# -*- coding:utf-8 -*-
#在合并pdf文件时出现问题，这里的话请参考https://github.com/mstamy2/PyPDF2/issues/193
#参考了https://blog.csdn.net/hubaoquanu/article/details/66973149  对此表示感谢
#2018-4-1 by jishuzhain

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


def get_url_list():
    """
    获取所有URL目录列表
    :return:
    """
    response = requests.get("http://www.yinwang.org/")
    soup = BeautifulSoup(response.content, "html.parser")
    menu_tag = soup.find_all(class_="list-group")[0]  # 这里根据实际网页的布局寻找对应的元素进行修改
    urls = []
    for li in menu_tag.find_all("li"):
        url = "http://www.yinwang.org" + li.a.get('href')
        urls.append(url)
    return urls


def parse_url_to_html(url, name):
    """
    解析URL，返回HTML内容
    :param url:解析的url
    :param name: 保存的html文件名
    :return: html
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 正文
        body = soup.find_all(class_="inner")[0]
        # 标题
        title = soup.find('h2').get_text()

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
                rtn = m.group(1) + m.group(2) + m.group(3)
                return rtn
            else:
                return m.group(1) + m.group(2) + m.group(3)

        html = re.compile(pattern).sub(func, html)
        html = html_template.format(content=html)
        # html = html.encode("utf-8")   #这里存在问题，进行编码后解析错误我就直接注释掉了，也许是本人的IDE环境所致
        with open(name, 'wb') as f:
            f.write(html)
        return name

    except Exception as e:

        logging.error("解析错误", exc_info=True)


def save_pdf(htmls, file_name):
    """
    把所有html文件保存到pdf文件
    :param htmls:  html文件列表
    :param file_name: pdf文件名
    :return:
    """
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'outline-depth': 10,
    }
    pdfkit.from_file(htmls, file_name, options=options)


def main():
    start = time.time()
    file_name = u"wang-yin-blog"
    urls = get_url_list()
    for index, url in enumerate(urls):
        parse_url_to_html(url, str(index) + ".html")
    htmls = []
    pdfs = []
    for i in range(0, 134):
        htmls.append(str(i) + '.html')
        pdfs.append(file_name + str(i) + '.pdf')

        save_pdf(str(i) + '.html', file_name + str(i) + '.pdf')
        print str(i) + " is ok"
        #print u"转换完成第" + str(i) + '个html'
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))
        print str(i) + ' pdf' + pdf
        # print u"合并完成第" + str(i) + '个pdf' + pdf

    output = open(u"wang-yin.pdf", "wb")
    merger.write(output)

    print "OK is done!"
    # print u"输出PDF成功！"

    for html in htmls:
        os.remove(html)
        print u"删除临时文件" + html

    for pdf in pdfs:
        os.remove(pdf)
        print u"删除临时文件" + pdf

    total_time = time.time() - start
    print(u"总共耗时：%f 秒" % total_time)


if __name__ == '__main__':
    main()
