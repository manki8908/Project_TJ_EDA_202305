'''
프로그램: 네이버 지도에서 숙박업체 정보 크롤링              작성자: 김만기
출력파일 내용:

'''

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm.notebook import tqdm
import re
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# .. 크롬 드라이버 시작
# 옵션값 사용
chrome_options = webdriver.ChromeOptions()   
# 브라우저 꺼짐 방지           
chrome_options.add_experimental_option("detach",True) 
# 드라이버 자동 최신 설치  
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install(), options = chrome_options))


# 네이버 지도 켜기
def start_navermap_with_chrome():

    # 네이버 지도 켜기
    driver.get("https://map.naver.com/v5")
    driver.implicitly_wait(5)
    #driver.maximize_window()



def search_hotel(hotel_name, hotel_address):
    # 검색 트리
    search_keyword = f'{hotel_name}, {hotel_address}' 
    driver.find_element(By.CLASS_NAME, 'input_search').send_keys(search_keyword)
    driver.find_element(By.CLASS_NAME, 'input_search').send_keys(Keys.ENTER)
    driver.implicitly_wait(7)
    # 새로운 프레임으로 driver 이동
    driver.switch_to.frame("searchIframe")

    #검색 목록중 호텔 url을 가져오기    
    search_result = driver.find_elements(by=By.XPATH, value='//*[@id="_pcmap_list_scroll_container"]/ul/li')
    count_search_result = len(driver.find_elements(by=By.XPATH, value='//*[@id="_pcmap_list_scroll_container"]/ul/li'))
    print(f"주소검색결과 개수: {count_search_result}")
    if count_search_result == 0:   
        return False
    elif count_search_result > 1:
        #식당 정보 클릭        
        driver.execute_script('return document.querySelector("#_pcmap_list_scroll_container > ul > li:nth-child(1) > div.qbGlu > div.ouxiq.icT4K > a:nth-child(1)").click()')
        driver.implicitly_wait(2)
    else:
        print('검색 결과 한개, 새창 없음')


    # 검색후 오른쪽 확장 탭으로 전환
    driver.switch_to.default_content()
    detail_iframe = driver.find_element(By.ID, 'entryIframe')
    driver.switch_to.frame(detail_iframe)
    # driver.switch_to.frame('entryIframe') # 그냥하면 안됨

    return True



def get_attribute():

    line = []

    # 별점
    try:
        star_score = int(driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[2]/div[1]/div[2]/span[1]/em').text)
    except:
        star_score = None
    print("star_score: ", star_score)


    # 블로그 리뷰 수 & 방문자 리뷰 수
    # 방문자
    try:
        visitor_review_count = int(driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[2]/div[1]/div[2]/span[2]/a/em').text)
    except:
        visitor_review_count = None
    print("visitor_review_count: ", visitor_review_count)


    # 블로그
    try:
        blog_review_count = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[2]/div[1]/div[2]/span[3]/a/em').text
    except:
        blog_review_count = None
    print("blog_review_count: ", blog_review_count)


    # 가까운 지하철 역에서 거리 / 도보시간
    # 거리
    try:
        dist_from_stn = driver.find_element(By.CSS_SELECTOR, 'div.O8qbU.tQY7D > div > div > em').text
    except:
        dist_from_stn = None
    print("dist_from_stn: ", dist_from_stn)

    # 시간
    try:
        time_from_stn = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div/div[2]/div/div/div[2]/div/div/div/span').text
        print("time_from_stn: ", time_from_stn)
        if time_from_stn.find("분"):
            time_from_stn = time_from_stn.split('분')[0].split('도보')[1]
    except:
        time_from_stn = None
    print("time_from_stn: ", time_from_stn)


    # 주요시설
    facilitys_list = []
    try:
        facilitys = driver.find_elements(By.CSS_SELECTOR, 'div.place_section_content > div > div.fusPl > ul > li')
        for li in facilitys:
            facilitys_list.append(li.text.strip())
    except:
        facilitys_list = None
    print("facilitys_list: ", facilitys_list)


    # .. 리뷰 클릭
    check_list = driver.find_elements(By.CSS_SELECTOR, 'div.place_fixed_maintab > div > div > div > div.flicking-camera > a > span.veBoZ')
    for i, li in enumerate(check_list):
        #print(i, type(li.text), li.text)
        if "리뷰" in li.text: 
            find_i = i+1  # python index + 1
    driver.find_element(By.CSS_SELECTOR, f'div.place_fixed_maintab > div > div > div > div.flicking-camera > a:nth-child({find_i})').click()


    # 이런점이 좋아요 정보 크롤링
    try:
        these_good_count = int(driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(7) > div:nth-child(3) > div.place_section.no_margin.mdJ86 > div > div > div._Wmab > em').text)
        print('these_good_count: ', these_good_count)
    
    except:
        print("이런점이 좋아요 정보가 없습니다")
        these_good_list = None
        these_good_count = None

    else:
        # "이런점이 좋았어요" 더보기 다 눌러 놓기
        while True:
            try:
                driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(7) > div:nth-child(3) > div.place_section.no_margin.mdJ86 > div > div > div.k2tmh > a.Tvx37').click()
                driver.implicitly_wait(1)
            except:
                break

        # 이런점이 좋아요, 딕셔너리로 {'리뷰':좋아요개수}
        these_good_list = []
        these_good = driver.find_elements(By.CSS_SELECTOR, 'div.place_section.no_margin.mdJ86 > div > div > div.k2tmh > ul > li')
        for i, li in enumerate(these_good):
            these_good_list.append({li.text.split("\n")[0].strip().replace('"',""): int(li.text.split("\n")[2].strip())})
        print("these_good_list: ", these_good_list)


    # combine item
    line.append([star_score, visitor_review_count, blog_review_count, 
                dist_from_stn, time_from_stn, facilitys_list, these_good_count, these_good_list])

    
    # close web
    driver.close

    return line


def main():

    # 서울시 전체 숙소(호텔,모델,게스트하우스, 등등) 리스트 로드
    df = pd.read_csv('../DAIN/crw_list.txt')
    #df.info()

    # 서울시 전체 숙소 네이버 지도에서 검색 및 정보 크롤링
    line = []
    #for i in df.index:
    for i in [0,1,2,3]:

        print(f"----{i} 시작-----------------------------------")
        print(df.사업장명[i], df.지번주소[i])

        # 크롬 드라이버 설정 및 네이버 지도 켜기
        start_navermap_with_chrome()
        print('----지도켜기 완료')

        # 네이버 지도에서 숙소 검색창 띄우기
        answer1 = search_hotel(df.사업장명[i], df.지번주소[i])
        if not(answer1): 
            continue
        else:
            print('----검색창 띄우기 완료')
              
        # 검색숙소 정보 가져오기
        crw_item = get_attribute()
        print('---- 검색숙소 정보 가져오기 완료')

        line.append(crw_item)

    get_list = pd.DataFrame(line, columns=['1', '2', '3', '4', '5', '6', '7', '8'])
    print(get_list)

if __name__ == '__main__':
    main()
