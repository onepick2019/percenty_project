# -*- coding: utf-8 -*-
"""
퍼센티 사이트 계정 정보 검출 개선 스크립트
실제 퍼센티 사이트 구조를 고려한 포괄적 검색
"""

import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enhanced_account_detection():
    """퍼센티 사이트에서 계정 정보 검출 - 개선된 버전"""
    
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.percenty.com")
        
        print("=== 퍼센티 사이트 로드 완료 ===")
        print("수동으로 로그인을 완료한 후 Enter를 눌러주세요...")
        input()
        
        print("\n=== 계정 정보 검출 시작 ===")
        
        # 1. 퍼센티 특화 셀렉터들
        percenty_selectors = [
            # 헤더 영역 사용자 정보
            ".ant-layout-header [class*='user']",
            ".ant-layout-header [class*='account']",
            ".ant-layout-header [class*='profile']",
            ".ant-layout-header .ant-dropdown-trigger",
            ".ant-layout-header .ant-avatar",
            
            # 사이드바 사용자 정보
            ".ant-layout-sider [class*='user']",
            ".ant-layout-sider [class*='account']",
            ".ant-layout-sider [class*='profile']",
            
            # 일반적인 사용자 정보 영역
            "[data-testid*='user']",
            "[data-testid*='account']",
            "[data-testid*='profile']",
            "[aria-label*='user']",
            "[aria-label*='account']",
            "[title*='@']",
            
            # 드롭다운 메뉴 관련
            ".ant-dropdown [class*='user']",
            ".ant-dropdown [class*='account']",
            ".ant-dropdown-menu-item",
            
            # 텍스트 기반 검색
            "*[class*='email']",
            "*[class*='user-info']",
            "*[class*='account-info']",
            "*[class*='profile-info']",
            
            # 메타 정보
            "meta[name*='user']",
            "meta[name*='account']",
            "meta[property*='user']",
            "meta[property*='account']"
        ]
        
        print("\n1. 퍼센티 특화 셀렉터로 검색:")
        found_elements = []
        
        for selector in percenty_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, element in enumerate(elements):
                        try:
                            text = element.text.strip()
                            if text:
                                print(f"  {selector}[{i}]: '{text}'")
                                if '@' in text:
                                    print(f"    ★ 이메일 형식 발견: {text}")
                                    found_elements.append((selector, text, element))
                                    
                            # 속성값도 확인
                            for attr in ['title', 'data-user', 'data-account', 'aria-label', 'placeholder', 'value']:
                                attr_value = element.get_attribute(attr)
                                if attr_value and '@' in attr_value:
                                    print(f"    ★ 속성 {attr}에서 이메일 발견: {attr_value}")
                                    found_elements.append((f"{selector}[{attr}]", attr_value, element))
                        except Exception as e:
                            continue
            except Exception as e:
                continue
        
        # 2. DOM 트리 전체 탐색
        print("\n2. DOM 트리 전체에서 이메일 패턴 검색:")
        try:
            # 모든 요소에서 텍스트 검색
            all_text_elements = driver.find_elements(By.XPATH, "//*[text()]")
            email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
            
            for element in all_text_elements:
                try:
                    text = element.text.strip()
                    if text and email_pattern.search(text):
                        emails = email_pattern.findall(text)
                        for email in emails:
                            tag_name = element.tag_name
                            class_attr = element.get_attribute('class') or ''
                            id_attr = element.get_attribute('id') or ''
                            print(f"    {email} (태그: {tag_name}, 클래스: {class_attr}, ID: {id_attr})")
                            found_elements.append((f"{tag_name}.{class_attr}#{id_attr}", email, element))
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"  DOM 트리 검색 오류: {e}")
        
        # 3. JavaScript 기반 정보 수집
        print("\n3. JavaScript로 사용자 정보 수집:")
        js_queries = [
            # 일반적인 사용자 정보
            "return window.user;",
            "return window.currentUser;",
            "return window.userInfo;",
            "return window.account;",
            "return window.accountInfo;",
            "return window.profile;",
            "return window.userProfile;",
            
            # React/Vue 상태 관리
            "return window.__INITIAL_STATE__;",
            "return window.__REDUX_STATE__;",
            "return window.store?.getState?.();",
            
            # 로컬/세션 스토리지
            "return localStorage.getItem('user');",
            "return localStorage.getItem('userInfo');",
            "return localStorage.getItem('account');",
            "return localStorage.getItem('accountInfo');",
            "return localStorage.getItem('profile');",
            "return localStorage.getItem('email');",
            "return sessionStorage.getItem('user');",
            "return sessionStorage.getItem('userInfo');",
            "return sessionStorage.getItem('account');",
            "return sessionStorage.getItem('email');",
            
            # 쿠키에서 정보 추출
            "return document.cookie;",
            
            # DOM에서 특정 패턴 검색
            "return [...document.querySelectorAll('*')].map(el => el.textContent).filter(text => text && text.includes('@')).slice(0, 10);",
            "return [...document.querySelectorAll('[title]')].map(el => el.title).filter(title => title && title.includes('@'));",
            "return [...document.querySelectorAll('[data-user], [data-account], [data-email]')].map(el => ({tag: el.tagName, attrs: [...el.attributes].map(a => a.name + '=' + a.value)}));"
        ]
        
        for i, script in enumerate(js_queries):
            try:
                result = driver.execute_script(script)
                if result:
                    print(f"  스크립트 {i+1}: {result}")
                    if isinstance(result, str) and '@' in result:
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', result)
                        for email in emails:
                            print(f"    ★ JavaScript에서 이메일 발견: {email}")
                    elif isinstance(result, list):
                        for item in result:
                            if isinstance(item, str) and '@' in item:
                                print(f"    ★ JavaScript 배열에서 이메일 발견: {item}")
            except Exception as e:
                continue
        
        # 4. 네트워크 요청 분석 (페이지 소스)
        print("\n4. 페이지 소스에서 사용자 정보 검색:")
        try:
            page_source = driver.page_source
            
            # 이메일 패턴 검색
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_source)
            if emails:
                unique_emails = list(set(emails))
                print(f"  페이지 소스에서 발견된 이메일들: {unique_emails}")
            
            # JSON 데이터 패턴 검색
            json_patterns = [
                r'"user"\s*:\s*"([^"]*@[^"]*)",',
                r'"email"\s*:\s*"([^"]*@[^"]*)",',
                r'"account"\s*:\s*"([^"]*@[^"]*)",',
                r'userEmail["\']?\s*[:=]\s*["\']([^"\']*)@([^"\']*)["\'\s]',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    print(f"  JSON 패턴에서 발견: {matches}")
                    
        except Exception as e:
            print(f"  페이지 소스 검색 오류: {e}")
        
        # 5. 결과 요약
        print("\n=== 검출 결과 요약 ===")
        if found_elements:
            print("발견된 계정 정보:")
            for selector, text, element in found_elements:
                print(f"  - 셀렉터: {selector}")
                print(f"    텍스트: {text}")
                try:
                    print(f"    위치: {element.location}")
                    print(f"    크기: {element.size}")
                    print(f"    표시여부: {element.is_displayed()}")
                except:
                    pass
                print()
        else:
            print("계정 정보를 찾을 수 없습니다.")
        
        print("\n=== 검출 완료 ===")
        print("결과를 확인한 후 Enter를 눌러 종료하세요...")
        input()
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    enhanced_account_detection()