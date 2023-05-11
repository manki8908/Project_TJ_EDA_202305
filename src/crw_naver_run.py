'''
작성자: 김만기
프로그램: 네이버 지도에서 숙박업체 정보 크롤링              
출력파일 내용:
 #   Column                  Non-Null Count  Dtype  
---  ------                  --------------  -----  
 0   사업장명                    34 non-null     object 
 1   업소유형                    34 non-null     object 
 2   지번주소                    34 non-null     object 
 3   도로명주소                   34 non-null     object 
 4   위도                      34 non-null     float64
 5   경도                      34 non-null     float64
 6   별점                      21 non-null     float64
 7   방문자 리뷰수                 28 non-null     float64
 8   블로그 리뷰수                 21 non-null     object 
 9   지하철역과의 거리               32 non-null     object 
 10  도보시간                    12 non-null     object 
 11  구비시설                    22 non-null     object 
 12  네이버 이런점이 좋아요 총합         23 non-null     float64
 13  네이버 이런점이 좋아요 {항목:좋아요수}  23 non-null     object 
 14  인허가일자                   34 non-null     object 
 15  인허가취소일자                 0 non-null      float64
 16  영업상태코드                  34 non-null     int64  
 17  폐업일자                    2 non-null      object 
 18  휴업시작일자                  2 non-null      object 
 19  휴업종료일자                  2 non-null      object 
 20  재개업일자                   0 non-null      float64
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
    driver.implicitly_wait(10)
    #driver.maximize_window()



def search_hotel(hotel_name, hotel_address):
    # 검색 트리
    search_keyword = f'{hotel_name}, {hotel_address}' 
    driver.find_element(By.CLASS_NAME, 'input_search').send_keys(search_keyword)
    driver.find_element(By.CLASS_NAME, 'input_search').send_keys(Keys.ENTER)
    driver.implicitly_wait(3)
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
        driver.execute_script('return document.querySelector("#_pcmap_list_scroll_container > ul > li:nth-child(1) > div.qbGlu > div> a:nth-child(1)").click()')
        driver.implicitly_wait(3)
    else:
        print('검색 결과 한개, 새창 없음')


    # 검색후 오른쪽 확장 탭으로 전환
    driver.switch_to.default_content()
    detail_iframe = driver.find_element(By.ID, 'entryIframe')
    driver.switch_to.frame(detail_iframe)
    # driver.switch_to.frame('entryIframe') # 그냥하면 안됨

    return True



def get_attribute():

    star_score = None
    stn_type = None
    visitor_review_count = None
    blog_review_count = None
    dist_from_stn = None
    time_from_stn = None
    facilitys_list_join = None
    these_good_count = None
    these_good_list_join = None

    # 별점
    try:
        star_score = float(driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div.place_section.OP4V8 > div.zD5Nm.f7aZ0 > div.dAsGb > span.PXMot.LXIwF > em').text)
    except:
        pass
    print("star_score: ", star_score)


    # 업소유형
    try:
        stn_type = driver.find_element(By.CSS_SELECTOR, '#_title > span.DJJvD').text
    except:
        pass
    print("stn_type: ", stn_type)


    # 블로그 리뷰 수 & 방문자 리뷰 수
    try:
        review_count_tag_list = driver.find_elements(By.CSS_SELECTOR, 'div.zD5Nm.f7aZ0 > div.dAsGb > span.PXMot')
    except:
        pass
    else:
        for li in review_count_tag_list:
            if "방문자리뷰" in li.text:
                visitor_review_count = li.text.split(" ")[1]
                print("visitor_review_count: ", visitor_review_count)
            if "블로그리뷰" in li.text:
                blog_review_count = li.text.split(" ")[1]
                print("blog_review_count: ", blog_review_count)


    # 가까운 지하철 역에서 거리 / 도보시간
    # 거리
    try:
        dist_from_stn = driver.find_element(By.CSS_SELECTOR, 'div.O8qbU.tQY7D > div > div > em').text
    except:
        pass
    print("dist_from_stn: ", dist_from_stn)
    # 도보시간
    try:
        #time_text = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div/div[2]/div/div/div[2]/div/div/div/span').text
        time_text = driver.find_element(By.CSS_SELECTOR, 'div.place_section.no_margin.vKA6F > div > div > div.O8qbU > div.vV_z_ > div > a > span.zPfVt').text
        #print("time_text: ", time_text)
        p = re.compile('[0-9]+분')
        time_from_stn = p.findall(time_text)            
    except:
        pass
    print("time_from_stn: ", time_from_stn)


    # 주요시설
    facilitys_list = []
    try:
        facilitys = driver.find_elements(By.CSS_SELECTOR, 'div.place_section_content > div > div.fusPl > ul > li')
        for li in facilitys:
            facilitys_list.append(li.text.strip())
    except:
        facilitys_list = None
    #facilitys_list_join = "\n".join(facilitys_list)
    facilitys_list_join = ",".join(facilitys_list)
    print("facilitys_list: ", facilitys_list)

    # .. 리뷰 클릭
    try:    # 홈, 리뷰 탭이 있는지 없는지 확인
        check_list = driver.find_elements(By.CSS_SELECTOR, 'div.place_fixed_maintab > div > div > div > div.flicking-camera > a.tpj9w._tab-menu > span.veBoZ')
        for i, li in enumerate(check_list):
            print(f"print check_list {i}: ", li.text)
    except:
        pass
    else:
        # 리뷰 버튼이 있으면 클릭
        if check_list:
            for i, li in enumerate(check_list):
                #print(i, type(li.text), li.text)
                if "리뷰" in li.text: 
                    find_i = i+1  # python index + 1
                    driver.find_element(By.CSS_SELECTOR, f'div.place_fixed_maintab > div > div > div > div.flicking-camera > a:nth-child({find_i})').click()
                    check_list = driver.find_elements(By.CSS_SELECTOR, 'div.place_fixed_maintab > div > div > div > div.flicking-camera > a > span.veBoZ')

                    # 이런점이 좋아요 정보 크롤링
                    these_good_list = []
                    try:
                        these_good_count = int(driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(7) > div:nth-child(3) > div.place_section.no_margin.mdJ86 > div > div > div._Wmab > em').text)
                        print('these_good_count: ', these_good_count)
                    except:
                        print("이런점이 좋아요 정보가 없습니다")
                        these_good_list = None                
                    else:
                        # "이런점이 좋았어요" 더보기 다 눌러 놓기
                        while True:
                            try:
                                driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(7) > div:nth-child(3) > div.place_section.no_margin.mdJ86 > div > div > div.k2tmh > a.Tvx37').click()
                                driver.implicitly_wait(1)
                            except:
                                break
                            
                        # 이런점이 좋아요, 딕셔너리로 {'리뷰':좋아요개수}
                        these_good = driver.find_elements(By.CSS_SELECTOR, 'div.place_section.no_margin.mdJ86 > div > div > div.k2tmh > ul > li')
                        for i, li in enumerate(these_good):
                            these_good_list.append({li.text.split("\n")[0].strip().replace('"',""): int(li.text.split("\n")[2].strip())})
                        print("these_good_list: ", these_good_list)
                        these_good_list_join=''
                        for i, item in enumerate(these_good_list):
                            #print(str(item))
                            if i == len(these_good_list)-1:
                                these_good_list_join += str(item)
                            else:
                                #these_good_list_join += str(item) + '\n'
                                these_good_list_join += str(item) + ','

    


    # combine item
    line = [stn_type, star_score, visitor_review_count, blog_review_count, 
            dist_from_stn, time_from_stn, facilitys_list_join, 
            these_good_count, these_good_list_join]

    return line


def main():

    # 서울시 전체 숙소(호텔,모델,게스트하우스, 등등) 리스트 로드
    df = pd.read_csv('../DAIN/crw_list.txt', index_col=0)
    #df.info()

    # 서울시 전체 숙소 네이버 지도에서 검색 및 정보 크롤링
    result = []

    for i in df.index:
    #for i in range(0,100,1):
    #for i in [0,1]:

        print(f"----{i} 시작-----------------------------------")
        print(df.사업장명[i], df.지번주소[i])

        # 크롬 드라이버 설정 및 네이버 지도 켜기
        start_navermap_with_chrome()
        print('----지도켜기 완료')

        # 네이버 지도에서 숙소 검색창 띄우기
        answer1 = search_hotel(df.사업장명[i], df.지번주소[i])
        if not(answer1): 
            print('----숙소가 없습니다, 검색창 띄우기 건너띔')
            continue
        else:
            print('----검색창 띄우기 완료')
              
        # 검색숙소 정보 가져오기
        crw_item = get_attribute()
        print('---- 검색숙소 정보 가져오기 완료')

        # close web
        driver.close

        # result save
        print("crw_item print: ")
        print(crw_item)

        result1 = df.iloc[i].tolist()
        result1.extend(crw_item)
        result.append(result1)

    print("print result: ", result)

    colum_names = ['사업장명','지번주소','도로명주소','위도','경도',
                '인허가일자','인허가취소일자','영업상태코드','폐업일자','휴업시작일자','휴업종료일자','재개업일자',
                '업소유형','별점', '방문자 리뷰수', '블로그 리뷰수', '지하철역과의 거리', '도보시간', '구비시설',
                '네이버 이런점이 좋아요 총합', '네이버 이런점이 좋아요 {항목:좋아요수}']  # 21
    
    get_list = pd.DataFrame(result, columns=colum_names)
    print(get_list.info())

    # 컬럼 순서 변경
    colum_names2 = ['사업장명','업소유형','지번주소','도로명주소','위도','경도',
                    '별점','방문자 리뷰수', '블로그 리뷰수', '지하철역과의 거리', '도보시간', '구비시설',
                    '네이버 이런점이 좋아요 총합', '네이버 이런점이 좋아요 {항목:좋아요수}',
                    '인허가일자','인허가취소일자','영업상태코드','폐업일자','휴업시작일자','휴업종료일자','재개업일자']  # 21
    get_df = get_list[colum_names2]
    get_df.to_csv("../DAOU/test_out_0_100.csv", encoding='euc-kr')

if __name__ == '__main__':
    main()