import os
import json5
import re
import time
import datetime
import requests
import gif_to_pdf
import base64_decode
import type2_spider
import four_to_one
import asy

headers = {
    "Referer": "https://m.doc88.com/",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36",
}


def get_base_str(id):
    """访问得到一串加密内容，里面信息为gif信息"""
    base_str_url = "https://m.doc88.com/doc.php?act=info&p_code={}&key=3854933de90d1dbb321d8ca29eac130a&v=1".format(id)
    response = requests.get(base_str_url)
    print("正在获取加密内容...")
    if response.status_code == 200:
        print("获取加密内容成功!")
        return response.text
    else:
        print("获取加密内容失败...请重试")
        exit(0)


def decode(str):
    """交给js解密，得到结果用json解析，并提取有用信息，回传一个列表"""
    print("正在解密...")
    result = json5.loads(base64_decode.ctx.call("all", str))
    if result:
        print("解密成功!")
        # print(result)
        try:
            page_count = result["pagecount"]
            docformat = result["docformat"]
            name = result["name"]
        except Exception as e:
            print("解析密文的json出错了...")
            exit(0)
        result_list = [page_count, name, [], docformat, True]
        if "gif_host" in result:
            gif_host = result["gif_host"]
            gif_struct = result["gif_struct"]
            result_list.append(gif_host)
            result_list[2] = gif_struct
            result_list[4] = True
        else:
            struct = result["struct"]
            result_list[2] = struct
            result_list[4] = False
        return result_list


def get_gif_urls(gif_urls, gif_host, gif_struct):
    """从gif_struct得到url部分，并组成真的url"""
    pattern = r"\"u\".*?\"(.*?)\"}"
    urls = re.findall(pattern, gif_struct, re.S)
    for url in urls:
        gif_urls.append(gif_host + "/get-" + url + ".gif")


def start_spider(gif_urls):
    """根据url开始下载gif，如果超过十张则只能下载10张"""
    for i in range(len(gif_urls)):
        response = requests.get(headers=headers, url=gif_urls[i])
        print(gif_urls[i], response.status_code)
        with open("images/" + str(i + 1) + ".gif", "wb")as file:
            file.write(response.content)


def spider_part2(page_count, page, id):
    """开始下载超过十张的部分
    必须先访问一个接口从接口携带session去callback真的gif链接
    如果从接口得到的信息是e=0需要重新访问接口"""
    hour = datetime.datetime.now().hour
    for i in range(page, page_count + 1):
        url1 = "https://mu3.doc88.com/p.do?id=" + str(id) + '-' + str(i) + '-' + "1024" + '-0-1-00-2-1-' + str(hour)
        url2 = "https://mu3.doc88.com/p.do?id=" + str(id) + '-' + str(i) + '-' + "1024" + '-0-1-00-0-1-' + str(hour)
        session = requests.session()
        now = int(round(time.time() * 1000))
        response = session.get(headers=headers, url=url2 + "&callback=callback_" + str(now) + "=")
        print(response.text)
        times = 0
        while "w" not in response.text and times < 5:  # 当请求callback结果为零，刷新十次怎么也够了应该
            session = requests.session()
            response = session.get(headers=headers, url=url2 + "&callback=callback_" + str(now) + "=")
            print(response.text, end=" ")
            print("第{}重新次请求".format(times + 1))
            times += 1
            if times == 5:
                session.close()
                print("第{}张图片获取失败了".format(i))
                break
        response2 = session.get(headers=headers, url=url1)
        print(url1, response.status_code)
        save_content(response2, "images/" + str(i) + ".gif")


def check_dir(path='images/'):
    """检测文件夹有没有别的内容"""
    if os.path.exists(path):
        file_list = os.listdir(path)
        for file in file_list:
            os.remove(path + file)
    else:
        os.mkdir(path)


def save_content(response, file):
    with open(file, "wb")as file_obj:
        file_obj.write(response.content)


def main():
    id = input("请输入id (链接中的一串数字)")
    base_str = (get_base_str(id))
    if base_str:
        result = decode(base_str)  # 得到列表
        check_dir()
        if result:
            print("name: " + result[1])
            print("总页数:" + result[0])
            print("文档类型： " + result[3])
            # print(result)
            gif_urls = []
            if result[4]:
                get_gif_urls(gif_urls, result[5], result[2])
                start_spider(gif_urls)
                if int(result[0]) > len(gif_urls):
                    spider_part2(int(result[0]), len(gif_urls), id)
                gif_to_pdf.save_to_pdf(result[1])
            else:
                # print(result)
                if int(result[0]) < 600:
                    type2_spider.spider_part3(id, int(result[0]))
                else:
                    asy.scheduler(int(result[0]), info=id)
                four_to_one.join(int(result[0]))
                gif_to_pdf.save_to_pdf(result[1])

            input("程序结束！")


"""result是一个回传列表，【page_count,name,struct,docuformat,type,gif_host】
struct是存放pic信息的，若type为True,存放含有url加密片段内容，若False,存放无用信息
type把加载方式分为两类，True为直接获得gif类，False为加载PPT片段类
"""
if __name__ == "__main__":
    main()
