import asyncio
import datetime
import time
import aiohttp
import aiofiles
import doc88
import re
import requests

headers = {
    "Referer": "https://m.doc88.com/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36",
}
url1 = "http://www.doc88.com/p-{}.html"
url2 = "https://stat.doc88.com/mc.do?code={}&referer=https%253A%252F%252Fwww.doc88.com%252F&callback=callback&_{}="
url3 = "https://{}.doc88.com/p.do?id={}-{}-600-0-4-11-0-1-{}&callback=callback&_{}="  # 第二个校验链接
url4 = "https://{}.doc88.com/p.do?id={}-{}-600-0-4-{}-2-1-{}"
index = ["00", "01", "10", "11"]


async def build_requests(session, url, i):
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            infos = await response.text()
            print(infos, i)
            if "w" not in infos:
                # print(infos, end=" ")
                return False
        else:
            print(await response.text(), "wrong")
            return False
        return True


async def get_pic(url, session, i, j):
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            await save_gif(await response.read(), i, j)
            print(url, 200)


async def save_gif(content, i, j):
    if not content:
        print(str(i) + "_" + index[j])
    async with aiofiles.open(r"images2/{}_{}.gif".format(i, index[j]), "wb")as file:
        await file.write(content)


async def save(i, imgHostKey, info, hour, sem):
    async with sem:
        async with asyncio.Semaphore(30):
            session = aiohttp.ClientSession()
            now = int(round(time.time() * 1000))
            url_3 = url3.format(imgHostKey, info, i, hour, now)
            times = 0
            flag = await build_requests(session, url_3, i)
            while (not flag) and times < 5:
                print("第{}次重新尝试".format(times))
                await session.close()
                session = aiohttp.ClientSession()
                await check_test(info, session, now)
                flag = await build_requests(session, url_3, i)
                times = times + 1
                if times == 5:
                    print("获取第{}组四张图片失败".format(i))
                    await session.close()
                    return
            for j in range(4):
                gif_url = url4.format(imgHostKey, info, i, index[j], hour)
                await get_pic(gif_url, session=session, i=i, j=j)
            await session.close()


def scheduler(page_count, info):
    imgHostKey = get_imgHostKey(info)
    doc88.check_dir("images2/")
    hour = datetime.datetime.now().hour
    loop = asyncio.get_event_loop()
    sem = asyncio.Semaphore(50)
    task = [save(i, imgHostKey=imgHostKey, info=info, hour=hour, sem=sem) for i in range(1, page_count + 1)]
    loop.run_until_complete(asyncio.wait(task))
    loop.run_until_complete(asyncio.sleep(1))
    loop.close()


def get_imgHostKey(info):
    response = requests.get(url=url1.format(info), headers=headers)
    pattern = r"imgHostKey.*?\"(.*?)\""
    imgHostKey = re.findall(pattern, response.text, re.S)
    if imgHostKey:
        imgHostKey = imgHostKey[0]
    if response.status_code == 200 and imgHostKey:
        return imgHostKey
    else:
        print("获取imageHostKey失败", response.status_code, response.text)
        exit(0)


async def check_test(info, session, now):
    await session.get(url=url2.format(info, now), headers=headers)


if __name__ == "__main__":
    scheduler(int(input("输入页码数")), input("输入链接中的数字"))
