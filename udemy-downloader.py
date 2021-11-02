import os
import json
import sys
import time
import ctypes
import requests
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from colorama import init, Fore, Style
from selenium.webdriver import ActionChains

os.environ['ADAL_PYTHON_SSL_NO_VERIFY'] = "1"

potada = r"""
                         __     __
                        / /__  / /_  _  __
                   __  / / _ \/ __ \| |/_/
                  / /_/ /  __/ /_/ />  <
TOOL MADE BY:     \____/\___/_.___/_/|_|
    """

header = {
    "Host":"www.udemy.com",
    "Connection":"keep-alive",
    "Accept":"*/*",
    "Sec-Fetch-Dest":"empty",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    "Origin":"https://www.udemy.com",
    "Sec-Fetch-Site":"same-origin",
    "Sec-Fetch-Mode":"cors",
    "Referer":"https://www.udemy.com/mobile/ipad",
    "Accept-Encoding":"deflate, br",
    "Accept-Language": "es-ES,es;q=0.9",
    "sec-fetch-dest": "document",
"sec-fetch-mode": "navigate",
"sec-fetch-site": "same-origin",
"sec-fetch-user": "?1",
"upgrade-insecure-requests": "1",
} #default headers request 
csrfmiddlewaretoken = ''
objWithVideosURL = []
idCourse = ''
courses = []
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option("excludeSwitches", ['enable-logging'])
options.add_argument("--disable-blink-features=AutomationControlled")
webD = '' #webdriver
req = requests.Session()

def getTokens():
    try:
        webD.get("https://www.udemy.com/join/login-popup/") #request to login page
        while "Access to this page" in webD.title: #await to user to resolve captcha
            print('Resolve the captcha...')
            print('Waiting 20 seconds...')
            time.sleep(20)
            pass
        csrfmiddlewaretoken = webD.find_element_by_name("csrfmiddlewaretoken").get_attribute("value")#get csrfmiddlewaretoken
        #get cookies
        cookies = str(webD.execute_script("return document.cookie"))
        index = cookies.index('csrftoken=')
        csrftoken=cookies[index:]
        index = csrftoken.index(';')
        csrftoken = csrftoken[:index]
        header['Cookie'] = csrftoken
        inputElement = webD.find_element_by_id("email--1")
        inputElement.send_keys(USER)
        inputElement = webD.find_element_by_id("id_password")
        inputElement.send_keys(PASS)
        inputElement = webD.find_element_by_id("submit-id-submit")
        ActionChains(webD).click(inputElement).perform()

        #wait until the page is loaded
        print('Wait 6 seconds...')
        time.sleep(6)
        while "Cloudflare" in webD.title: #await to user to resolve captcha
            print('Resolve the captcha...')
            print('Waiting 30 seconds...')
            time.sleep(30)
            pass

        #get cookies
        cookies = str(webD.execute_script("return document.cookie"))
        webD.quit()
        index = cookies.index('access_token=')+13
        authorization = cookies[index:]
        index = authorization.index(';')
        authorization = authorization[:index]
        header['x-udemy-authorization'] = 'Bearer '+authorization
        header['Accept'] = '*/*'
        header['cookie'] = cookies
        return True
    except Exception as e:
        print(f'error getPreToken: {e}')

def getIdCourses():
    global courses
    try:
        #get IDs and titles of the courses
        count = 0
        r=req.get(f"https://www.udemy.com/api-2.0/users/me/subscribed-courses", headers=header)
        ss = json.loads(r.text)
        for value in ss['results']:
            courses.append({"index":count,"id":value['id'],"title":value['title']})
            print(str(count) +' - '+ value['title'])
            count+=1
    except Exception as e:
        print(f'error getIdCourses: {e}')

def getIds():
    global objWithVideosURL
    try:
        #get IDs and titles of the videos
        count = 1
        r=req.get(f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{idCourse}/lectures/?page={count}", headers=header)
        while(r.status_code == 200):
            ss = json.loads(r.text)
            for value in ss['results']:
                info = {"id":value['id'],"title":value['title'],"asset_type":value['asset']['asset_type']}
                if "Article" == value['asset']['asset_type']:
                    info["id"] = value['asset']['id']
                objWithVideosURL.append(info)
            count+=1
            r=req.get(f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{idCourse}/lectures/?page={count}", headers=header)
    except Exception as e:
        print(f'error getIds: {e}')

def getVideos():
    try:
        #Download videos
        count = 0
        l = len(objWithVideosURL)
        printProgressBar(count, l, prefix = count, suffix = len(objWithVideosURL), length = 50)
        for value in objWithVideosURL:
            if value['asset_type'] == "Article":
                f = open(f"{count} - Articulo.html", "w")
                r=req.get(f"https://www.udemy.com/api-2.0/assets/{value['id']}/?fields[asset]=@min,body", headers=header)
                ss = json.loads(r.text)
                f.write(ss['body'])
                f.close()
            elif value['asset_type'] == "Video":
                if not os.path.isfile(f"{count} - {especialCharacteres(value['title'])}.mp4"):
                    r=req.get(f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{idCourse}/lectures/{value['id']}/?fields[lecture]=asset,supplementary_assets&fields[asset]=asset_type,stream_urls,filename", headers=header)
                    ss = json.loads(r.text)
                    urllib.request.urlretrieve(ss['asset']['stream_urls']['Video'][0]['file'], f"{count} - {especialCharacteres(value['title'])}.mp4")
                    if len(ss['supplementary_assets']) != 0:
                        for x in ss['supplementary_assets']:
                            if "File" == x["asset_type"]:
                                r=req.get(f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{idCourse}/lectures/{value['id']}/supplementary-assets/{x['id']}/?fields[asset]=download_urls", headers=header)
                                sa = json.loads(r.text)
                                r=req.get(f"{sa['download_urls']['File'][0]['file']}", stream=True)
                                chunk_size=128
                                with open(f"{count} - {x['filename']}", "wb") as fd:
                                    for chunk in r.iter_content(chunk_size=chunk_size):
                                        fd.write(chunk)
                            else:
                                f = open(f"{count} - Download link .txt", "w")
                                r=req.get(f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{idCourse}/lectures/{value['id']}/supplementary-assets/{x['id']}/?fields[asset]=external_url", headers=header)
                                sa = json.loads(r.text)
                                f.write(f"{x['filename']} : {sa['external_url']}")
                                f.close()
            else:
                open(f"{count} - Maybe here there is an exam.txt", "w")
            count+=1
            printProgressBar(count, l, prefix = count, suffix = len(objWithVideosURL), length = 50)
    except Exception as e:
        print(f'error getVideos: {e}')

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

def especialCharacteres(text):#replace special characters
    chars = '<>:"/\\|?*'
    for c in chars:
        if c in text:
            text = text.replace(c, "")
    return text

if __name__ == '__main__':
    try:
        init()
        ctypes.windll.kernel32.SetConsoleTitleW(os.path.basename(__file__).replace('.py','') + f' | by Jebx')
        print(f"{Fore.YELLOW}{potada}{Style.RESET_ALL}")
        USER = input("Email:")
        PASS = input("Pass:")
        print("Don't close the browser!!!!")
        time.sleep(2)
        webD = webdriver.Chrome(options=options, executable_path='chromedriver.exe')
        if getTokens():
            getIdCourses()
            print()
            print()
            idCourse = input('ID course:')
            for course in courses:
                if str(course['index']) == idCourse:
                    idCourse = course['id']
            print('Loading...')
            getIds()
            getVideos()
            input('Press ENTER to EXIT')
            sys.exit()
    except:
        print("\nGoodbye!!")
