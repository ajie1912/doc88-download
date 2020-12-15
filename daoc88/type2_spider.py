import time
import requests
import datetime
import re
import doc88

headers = {
    "Referer": "https://m.doc88.com/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36",
}

url1 = "http://www.doc88.com/p-{}.html"  # html，获得imgHostKey
url2 = "https://stat.doc88.com/mc.do?code={}&referer=https%253A%252F%252Fwww.doc88.com%252F&callback=callback&_{}="
url3 = "https://{}.doc88.com/p.do?id={}-{}-600-0-4-11-0-1-{}&callback=callback&_{}="  # 第二个校验链接
url4 = "https://{}.doc88.com/p.do?id={}-{}-600-0-4-{}-2-1-{}"


def spider_part3(info,page_count):
    doc88.check_dir("images2/")
    global url4
    imgHostKey = get_imgHostKey(info)
    hour = datetime.datetime.now().hour
    for i in range(1,page_count+1):
        session = requests.session()
        now = int(round(time.time() * 1000))
        response = session.get(url3.format(imgHostKey, info, i,hour, now), headers=headers)
        print(response.text)
        times = 0
        while "w" not in response.text and times < 5:  # 当请求callback结果为零，刷新十次怎么也够了应该
            session = requests.session()
            response = session.get(url3.format(imgHostKey, info,i, hour, now), headers=headers)
            print(response.text, end=" ")
            print("第{}重新次请求".format(times + 1))
            times += 1
            if times == 5:
                session.close()
                print("第{}组四张图片获取失败了".format(i))
                break
        for j in range(4):
            gif_url = url4.format(imgHostKey, info,i, gif_sort(j), hour)
            response2 = session.get(gif_url, headers=headers)
            if response.status_code == 200:
                print(gif_url, response.status_code)
                doc88.save_content(response2, "images2/{}_{}.gif".format(i, gif_sort(j)))
            else:
                print(gif_url + "访问失败")


def gif_sort(n):
    if n == 0:
        return "00"
    elif n == 1:
        return "01"
    elif n == 2:
        return "10"
    elif n == 3:
        return "11"


def get_imgHostKey(info):
    response = requests.get(url=url1.format(info), headers=headers)
    pattern = r"imgHostKey.*?\"(.*?)\""
    imgHostKey = re.findall(pattern, response.text, re.S)
    if imgHostKey:
        imgHostKey = imgHostKey[0]
    if response.status_code == 200 and imgHostKey:
        return imgHostKey
    else:
        print("获取imageHostKey失败")
        exit(0)
