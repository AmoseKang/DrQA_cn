import json
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import bs4
import re
import uuid
import os

def get_hrefs(soup,doc_num):
    count = 0;
    href = []
    for tr in soup.find_all('h3'):
        if isinstance(tr, bs4.element.Tag):
            tar = tr.a
            href.append( tar.attrs['href'])
            count += 1
        if count >= doc_num:
            break
    return href

def get_html(url):
    res=requests.get(url)
    res.encoding='utf-8'
    return res.text

def get_content_by_vsb(soup):
    content = []
    for tr in soup.find_all('div', id=re.compile('vsb_')):
        if isinstance(tr, bs4.element.Tag):
            for p in tr.find_all('p'):
                content.append(p.text)
    return content

def get_jsnr_content(soup):
    # 先把名字找出来，这个就很恶心
    name = ''
    for tr in soup.find_all('td', width=re.compile('21%')):
        if isinstance(tr, bs4.element.Tag):
            name = tr.text
    if name == '' or name is None:
        return ''
    title = []
    text = []
    content = []
    # 开头处一个title对应一个text
    for tr in soup.find_all('div', class_=re.compile('jiaoshi_title')):
        if isinstance(tr, bs4.element.Tag):
            title.append(tr.text)
    for tr in soup.find_all('div', class_=re.compile('jstext')):
        if isinstance(tr, bs4.element.Tag):
            temp = ''.join(tr.text)
            temp = temp.replace('&nbsp;', ' ')
            if 'function' not in temp:
                text.append(temp)
    for i in range(len(text)):
        if i >= len(title):
            content[len(title)] += name + text[i]
        else:
            content.append( name + title[i] + text[i])
    return content

def get_content_by_p(soup):
    content = []
    for tr in soup.find_all('p'):
        if isinstance(tr, bs4.element.Tag):
            content.append(''.join(tr.text.split()))

    return content

def get_content_by_indent(soup):
    content = []
    try:
        for tr in soup.find_all('p', class_=re.compile('indent')):
            if isinstance(tr, bs4.element.Tag):
                content.append( tr.text)
        return content
    except:
        return []

def get_content(link):
    html = get_html(link)
    soup = BeautifulSoup(html, 'html.parser')
    real_url = requests.get(link).url
    if 'jsnr.jsp' in real_url:
        content = get_jsnr_content(soup)
        return content.replace('&nbsp;','')

    content = get_content_by_vsb(soup)
    if content == [] or content == '':
        content = get_content_by_indent(soup)
    if content == [] or content == '':
        content = get_content_by_p(soup)
    for i in range(len(content)):
        content[i] = content[i].replace('&nbsp;', ' ')
    return content

def save_content_to_files(content):
    if os.path.isdir('data') is False:
        os.mkdir('data')
    for w in content:
        if len(w) < 30:
            continue
        id = str(uuid.uuid1())
        with open('data/'+id+'.txt','w',encoding='utf-8') as f:
            f.write(json.dumps({'id':id,'text':w},ensure_ascii=False))

def retriver(question,doc_num):
    if question == '':
        return False

    if doc_num == '' or doc_num is None:
        doc_num = 5
    elif type(doc_num) == str:
        doc_num = eval(doc_num)

    url = 'http://www.baidu.com/s?wd=' + quote(question + ' site:xjtu.edu.cn')
    html = get_html(url)
    soup = BeautifulSoup(html,'html.parser')
    hrefs = get_hrefs(soup,doc_num)
    content = []
    for link in hrefs:
        content.extend(get_content(link))

    save_content_to_files(content)
    return content
    # print(content)




if __name__ == '__main__':
    retriver('交大哪年办学',5)