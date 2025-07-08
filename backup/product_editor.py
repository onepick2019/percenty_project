# -*- coding: utf-8 -*-
"""
퍼센티 상품 수정 관련 모듈
"""

import sys
import os
import io
import time
import random
import logging
import pyperclip
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 설정 가져오기
try:
    from config import (
        MIN_DELAY, MAX_DELAY, 
        PAGE_LOAD_MIN, PAGE_LOAD_MAX
    )
except ImportError:
    # 기본 설정 정의
    MIN_DELAY = 1
    MAX_DELAY = 3
    PAGE_LOAD_MIN = 2
    PAGE_LOAD_MAX = 5

class ProductEditor:
    """퍼센티 상품 편집 클래스"""
    
    def __init__(self, driver=None):
        """초기화"""
        self.driver = driver
        
    def random_delay(self, min_seconds=None, max_seconds=None):
        """랜덤 지연"""
        min_seconds = min_seconds or MIN_DELAY
        max_seconds = max_seconds or MAX_DELAY
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
        
    def navigate_to_product_tab(self, tab_name):
        """상품 수정 모달창에서 탭 이동
        
        Args:
            tab_name (str): 탭 이름 (예: '상품명 / 카테고리', '옵션', '가격', '키워드', '썸네일', '상세페이지', '업로드', '메모')
            
        Returns:
            bool: 탭 이동 성공 여부
        """
        try:
            logging.info(f"{tab_name} 탭으로 이동 시도...")
            
            # 스크린샷 찍기 - 디버깅용
            try:
                self.driver.save_screenshot(f"tab_{tab_name}_before.png")
                logging.info(f"{tab_name} 탭 이동 전 화면 스크린샷 저장: tab_{tab_name}_before.png")
            except Exception as e:
                logging.warning(f"스크린샷 저장 실패: {e}")
            
            # 모달창이 있는지 확인
            try:
                modal = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-content, .ant-drawer-content"))
                )
                logging.info("모달창 확인 성공")
            except Exception as e:
                logging.warning(f"모달창을 찾을 수 없습니다: {e}")
                return False
            
            # 모달창 내부로 포커스 이동
            try:
                self.driver.execute_script("""
                    var modal = document.querySelector('.ant-modal-content, .ant-drawer-content');
                    if (modal) modal.focus();
                """)
                time.sleep(1)
            except Exception as e:
                logging.warning(f"모달창 포커스 실패: {e}")
            
            # 탭 이름 매핑 - 탭 이름을 실제 HTML에 맞게 변환
            tab_mapping = {
                '기본정보': '상품명 / 카테고리',
                '상품명': '상품명 / 카테고리',
                '카테고리': '상품명 / 카테고리',
                '상세정보': '상세페이지',
                '상세': '상세페이지',
                '업로드정보': '업로드'
            }
            
            # 탭 이름 변환
            actual_tab_name = tab_mapping.get(tab_name, tab_name)
            logging.info(f"실제 탭 이름 변환: {tab_name} -> {actual_tab_name}")
            
            # 탭 선택자 목록 - mdfiles/percenty_project_move_tab.md 파일의 HTML 구조에 맞게 수정
            tab_selectors = [
                # 가장 정확한 탭 선택자 - ant-tabs-tab 클래스와 텍스트 매칭
                f"//div[contains(@class, 'ant-tabs-tab')]//div[contains(@class, 'ant-tabs-tab-btn') and contains(text(), '{actual_tab_name}')]",
                f"//div[contains(@class, 'ant-tabs-tab')]//div[contains(@class, 'ant-tabs-tab-btn')]/span[text()='{actual_tab_name}']",
                f"//div[contains(@class, 'ant-tabs-tab')]//div[contains(@class, 'ant-tabs-tab-btn')]/span[contains(text(), '{actual_tab_name}')]",
                
                # 역할 기반 선택자
                f"//div[@role='tab']//div[contains(text(), '{actual_tab_name}')]",
                f"//div[@role='tab' and contains(@aria-selected, 'false')]//div[contains(text(), '{actual_tab_name}')]",
                
                # 탭 버튼 선택자
                f"//div[contains(@class, 'ant-tabs-tab-btn') and contains(text(), '{actual_tab_name}')]",
                
                # 탭 리스트 내부 선택자
                f"//div[contains(@class, 'ant-tabs-nav-list')]//div[contains(@class, 'ant-tabs-tab')]//span[text()='{actual_tab_name}']",
                f"//div[contains(@class, 'ant-tabs-nav-list')]//div[contains(@class, 'ant-tabs-tab')]//span[contains(text(), '{actual_tab_name}')]",
                
                # 단순 텍스트 매칭
                f"//span[text()='{actual_tab_name}']",
                
                # 특정 탭에 대한 선택자
                "//div[contains(@class, 'ant-tabs-tab')]//span[text()='상품명 / 카테고리']",
                "//div[contains(@class, 'ant-tabs-tab')]//span[text()='옵션']",
                "//div[contains(@class, 'ant-tabs-tab')]//span[text()='가격']",
                "//div[contains(@class, 'ant-tabs-tab')]//span[text()='키워드']",
                "//div[contains(@class, 'ant-tabs-tab')]//span[text()='썸네일']",
                "//div[contains(@class, 'ant-tabs-tab')]//span[text()='상세페이지']",
                "//div[contains(@class, 'ant-tabs-tab')]//span[text()='업로드']",
                
                # CSS 선택자
                ".ant-tabs-tab"
            ]
            
            # 탭 찾기 시도
            tab_found = False
            for selector in tab_selectors:
                try:
                    # 명시적 대기 사용
                    wait = WebDriverWait(self.driver, 3)
                    if selector.startswith("//"):
                        tabs = wait.until(EC.presence_of_all_elements_located((By.XPATH, selector)))
                    else:
                        tabs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                except Exception as e:
                    logging.warning(f"{tab_name} 탭 요소 찾기 실패 ({selector}): {e}")
                    continue
                    
                try:
                    if not tabs:
                        continue
                    
                    logging.info(f"탭 선택자 {selector}로 {len(tabs)}개의 요소 발견")
                except Exception as e:
                    logging.warning(f"탭 요소 처리 중 오류: {e}")
                    continue
                    
                try:
                    for tab in tabs:
                        try:
                            # 탭이 보이는지 확인
                            if not tab.is_displayed():
                                continue
                            
                            # 탭 텍스트 확인
                            tab_text = tab.text.strip()
                            logging.info(f"발견한 탭 텍스트: '{tab_text}'")
                            
                            # 탭 텍스트가 비어있으면 하위 요소 확인
                            if not tab_text:
                                try:
                                    # span 하위 요소 확인
                                    spans = tab.find_elements(By.TAG_NAME, "span")
                                    for span in spans:
                                        if span.is_displayed() and span.text.strip():
                                            tab_text = span.text.strip()
                                            logging.info(f"span 요소에서 탭 텍스트 발견: '{tab_text}'")
                                            break
                                except:
                                    pass
                                
                                # div 하위 요소 확인
                                if not tab_text:
                                    try:
                                        divs = tab.find_elements(By.TAG_NAME, "div")
                                        for div in divs:
                                            if div.is_displayed() and div.text.strip():
                                                tab_text = div.text.strip()
                                                logging.info(f"div 요소에서 탭 텍스트 발견: '{tab_text}'")
                                                break
                                    except:
                                        pass
                            
                            # 탭 매칭 확인
                            if actual_tab_name in tab_text or \
                               (actual_tab_name == '상품명 / 카테고리' and ('상품명' in tab_text or '카테고리' in tab_text)) or \
                               (actual_tab_name == '상세페이지' and '상세' in tab_text) or \
                               (actual_tab_name == '업로드' and '업로드' in tab_text):
                                
                                # 탭이 보이도록 스크롤
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
                                self.random_delay(0.5, 1)
                                
                                # 탭 클릭 시도 (여러 방법 시도)
                                try:
                                    # 1. 일반 클릭
                                    tab.click()
                                    logging.info(f"{actual_tab_name} 탭 클릭 성공 (일반 클릭)")
                                    tab_found = True
                                except Exception as e:
                                    logging.warning(f"일반 클릭 실패: {e}")
                                    
                                    try:
                                        # 2. JavaScript로 클릭
                                        self.driver.execute_script("arguments[0].click();", tab)
                                        logging.info(f"{actual_tab_name} 탭 클릭 성공 (JavaScript 클릭)")
                                        tab_found = True
                                    except Exception as e:
                                        logging.warning(f"JavaScript 클릭 실패: {e}")
                                        
                                        try:
                                            # 3. 하위 요소 클릭 시도
                                            child_elements = tab.find_elements(By.XPATH, ".//*")
                                            for child in child_elements:
                                                if child.is_displayed():
                                                    try:
                                                        child.click()
                                                        logging.info(f"{actual_tab_name} 탭 하위 요소 클릭 성공")
                                                        tab_found = True
                                                        break
                                                    except:
                                                        continue
                                        except Exception as e:
                                            logging.warning(f"하위 요소 클릭 실패: {e}")
                                    except Exception as e2:
                                        logging.warning(f"JavaScript 클릭 실패: {e2}")
                                        continue
                                
                                # 클릭 후 대기
                                time.sleep(2)
                                
                                # 스크린샷 찍기 - 디버깅용
                                try:
                                    self.driver.save_screenshot(f"tab_{tab_name}_after.png")
                                    logging.info(f"{tab_name} 탭 클릭 후 화면 스크린샷 저장: tab_{tab_name}_after.png")
                                except Exception as e:
                                    logging.warning(f"스크린샷 저장 실패: {e}")
                                tab_found = True
                                return True
                        except Exception as e:
                            logging.warning(f"탭 처리 중 오류: {e}")
                            continue
                except Exception as e:
                    logging.warning(f"{tab_name} 탭 찾기 실패 ({selector}): {e}")
            
            # 모든 선택자로 찾지 못한 경우 JavaScript로 시도
            if not tab_found:
                try:
                    # 모든 탭 가져오기
                    tabs_info = self.driver.execute_script("""
                        var tabs = document.querySelectorAll('.ant-tabs-tab, [role="tab"]');
                        var tabsInfo = [];
                        for (var i = 0; i < tabs.length; i++) {
                            tabsInfo.push({
                                index: i,
                                text: tabs[i].textContent.trim()
                            });
                        }
                        return tabsInfo;
                    """)
                    
                    if tabs_info:
                        logging.info(f"발견된 탭 목록: {tabs_info}")
                        
                        # 탭 인덱스 찾기
                        tab_index = -1
                        for i, tab_info in enumerate(tabs_info):
                            if tab_name in tab_info['text'] or \
                               ("기본" in tab_info['text'] and tab_name == "기본정보") or \
                               ("상세" in tab_info['text'] and tab_name == "상세정보") or \
                               ("메모" in tab_info['text'] and tab_name == "메모") or \
                               ("업로드" in tab_info['text'] and tab_name == "업로드정보"):
                                tab_index = tab_info['index']
                                break
                        
                        if tab_index >= 0:
                            # 탭 클릭
                            click_result = self.driver.execute_script(f"""
                                var tabs = document.querySelectorAll('.ant-tabs-tab, [role="tab"]');
                                if (tabs.length > {tab_index}) {{
                                    tabs[{tab_index}].scrollIntoView({{block: 'center'}});
                                    tabs[{tab_index}].click();
                                    return true;
                                }}
                                return false;
                            """)
                            
                            if click_result:
                                logging.info(f"{tab_name} 탭 JavaScript 클릭 성공 (인덱스: {tab_index})")
                                time.sleep(2)  # 탭 전환 대기
                                return True
                except Exception as e:
                    logging.warning(f"JavaScript로 탭 찾기 실패: {e}")
            
            # 실패 시 스크린샷 찍기
            try:
                self.driver.save_screenshot(f"tab_{tab_name}_not_found.png")
                logging.info(f"{tab_name} 탭을 찾지 못한 화면 스크린샷 저장: tab_{tab_name}_not_found.png")
            except Exception as e:
                logging.warning(f"스크린샷 저장 실패: {e}")
            
            logging.error(f"{tab_name} 탭을 찾을 수 없습니다.")
            return False
        except Exception as e:
            logging.error(f"{tab_name} 탭 이동 중 오류 발생: {e}")
            return False
        
    def random_delay(self, min_seconds=None, max_seconds=None):
        """랜덤 지연"""
        min_seconds = min_seconds or MIN_DELAY
        max_seconds = max_seconds or MAX_DELAY
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def get_product_list(self):
        """상품 목록 가져오기"""
        try:
            # 상품 행 목록 가져오기
            self.random_delay(2, 3)  # 페이지 로딩 대기 시간 추가
            
            # 총상품수 확인
            try:
                total_products_elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '총') and contains(text(), '개 상품')]")),
                )
                total_text = total_products_elem.text
                match = re.search(r'총\s*(\d+)\s*개', total_text)
                if match:
                    total_count = int(match.group(1))
                    logging.info(f"현재 총상품수: {total_count}개")
            except Exception as e:
                logging.debug(f"총상품수 확인 실패: {e}")
            
            # 상품 행 목록 가져오기
            product_rows = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//tbody/tr"))
            )
            
            # 빈 행이나 유효하지 않은 행 필터링
            valid_rows = []
            for row in product_rows:
                try:
                    # 상품명 셀이 있고 내용이 비어있지 않은지 확인
                    name_cells = row.find_elements(By.XPATH, ".//td[2]")
                    if name_cells and name_cells[0].text.strip():
                        valid_rows.append(row)
                except:
                    continue
            
            logging.info(f"상품 목록 {len(valid_rows)}개 가져옴")
            return valid_rows
        except Exception as e:
            logging.error(f"상품 목록 가져오기 실패: {e}")
            return []
    
    def select_product(self, product_row):
        """상품 선택 및 수정화면 모달창 열기"""
        try:
            logging.info("상품 선택 및 수정화면 모달창 열기 중...")
            
            # 상품명 추출 시도
            product_name = None
            try:
                # 행에서 상품명 추출 - 일반적으로 2번째 열
                cells = product_row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    product_name = cells[1].text.strip()
                    if product_name:
                        # 상품명이 여러 줄일 경우 첫 줄만 추출
                        product_name = product_name.split('\n')[0].strip()
                        logging.info(f"행에서 추출한 상품명: {product_name}")
            except Exception as e:
                logging.warning(f"행에서 상품명 추출 실패: {e}")
            
            # 스크린샷 찍기 - 디버깅용
            try:
                self.driver.save_screenshot("before_select.png")
                logging.info("상품 선택 전 화면 스크린샷 저장: before_select.png")
            except Exception as e:
                logging.warning(f"스크린샷 저장 실패: {e}")
            
            # 요소가 보이도록 스크롤
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product_row)
                logging.info("상품 행으로 스크롤")
                self.random_delay(1, 2)
            except Exception as e:
                logging.warning(f"스크롤 실패: {e}")
            
            # 상품 행 단일 클릭 시도
            try:
                # 일반 단일 클릭 시도
                logging.info("일반 단일 클릭 시도")
                product_row.click()
                self.random_delay(2, 3)
                
                # 모달창 열렸는지 확인
                try:
                    logging.info("모달창 열림 확인 시도 중...")
                    modal = WebDriverWait(self.driver, 8).until(  # 대기 시간 증가
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-content, .ant-drawer-content"))
                    )
                    if modal.is_displayed():
                        logging.info("모달창 열림 확인 - 일반 클릭 방법")
                        
                        # 스크린샷 찍기 - 디버깅용
                        try:
                            self.driver.save_screenshot("modal_opened.png")
                            logging.info("모달창 열린 후 화면 스크린샷 저장: modal_opened.png")
                        except Exception as e:
                            logging.warning(f"스크린샷 저장 실패: {e}")
                        
                        return product_name
                    else:
                        logging.warning("모달창이 발견되었지만 표시되지 않음")
                except TimeoutException:
                    logging.warning("일반 클릭 후 모달창이 열리지 않음")
            except Exception as e:
                logging.warning(f"상품 행 클릭 시도 실패: {e}")
            
            # 더블 클릭 시도
            try:
                logging.info("더블 클릭 시도")
                actions = ActionChains(self.driver)
                actions.double_click(product_row).perform()
                self.random_delay(2, 3)
                
                # 모달창 열렸는지 확인
                try:
                    modal = WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-content, .ant-drawer-content"))
                    )
                    if modal.is_displayed():
                        logging.info("모달창 열림 확인 - 더블 클릭 방법")
                        return product_name
                except TimeoutException:
                    logging.warning("더블 클릭 후 모달창이 열리지 않음")
            except Exception as e:
                logging.warning(f"더블 클릭 시도 실패: {e}")
                
                # 스크린샷 찍기 - 디버깅용
                try:
                    self.driver.save_screenshot("click_failed.png")
                    logging.info("클릭 실패 후 화면 스크린샷 저장: click_failed.png")
                except Exception as e:
                    logging.warning(f"스크린샷 저장 실패: {e}")
                    
            # 행 내부의 편집 버튼 찾기 시도
            try:
                # 더 넓은 선택자로 편집 버튼 찾기
                edit_buttons = product_row.find_elements(By.XPATH, 
                    ".//button[contains(@class, 'edit') or contains(text(), '편집')] | .//span[contains(@class, 'edit')] | .//i[contains(@class, 'edit')]")
                
                if edit_buttons:
                    for button in edit_buttons:
                        if button.is_displayed():
                            # 버튼으로 스크롤
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            self.random_delay(1, 1)
                            
                            # JavaScript로 클릭 실행
                            self.driver.execute_script("arguments[0].click();", button)
                            logging.info("편집 버튼 JavaScript 클릭")
                            self.random_delay(2, 3)
                            
                            # 모달창 열렸는지 확인
                            try:
                                modal = WebDriverWait(self.driver, 8).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-content, .ant-drawer-content"))
                                )
                                if modal.is_displayed():
                                    logging.info("모달창 열림 확인 - 편집 버튼 방법")
                                    return product_name
                            except TimeoutException:
                                logging.warning("편집 버튼 클릭 후 모달창이 열리지 않음")
            except Exception as e:
                logging.warning(f"편집 버튼 클릭 시도 실패: {e}")
            
            # 오른쪽 클릭 메뉴 시도
            try:
                # JavaScript로 오른쪽 클릭 실행
                self.driver.execute_script("""
                    function simulateRightClick(element) {
                        var evt = element.ownerDocument.createEvent('MouseEvents');
                        evt.initMouseEvent('contextmenu', true, true, element.ownerDocument.defaultView, 1, 0, 0, 0, 0, false, false, false, false, 2, null);
                        element.dispatchEvent(evt);
                    }
                    simulateRightClick(arguments[0]);
                """, product_row)
                
                logging.info("상품 행 JavaScript 오른쪽 클릭 시도")
                self.random_delay(1, 2)
                
                # 컨텍스트 메뉴에서 편집 옵션 찾기
                menu_items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-dropdown') or contains(@class, 'context-menu')]//li")
                for item in menu_items:
                    if '편집' in item.text or 'edit' in item.text.lower():
                        self.driver.execute_script("arguments[0].click();", item)
                        logging.info("컨텍스트 메뉴에서 편집 옵션 JavaScript 클릭")
                        self.random_delay(2, 3)
                        
                        # 모달창 열렸는지 확인
                        try:
                            modal = WebDriverWait(self.driver, 8).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-content, .ant-drawer-content"))
                            )
                            if modal.is_displayed():
                                logging.info("모달창 열림 확인 - 컨텍스트 메뉴 방법")
                                return product_name
                        except TimeoutException:
                            logging.warning("컨텍스트 메뉴 클릭 후 모달창이 열리지 않음")
            except Exception as e:
                logging.warning(f"컨텍스트 메뉴 시도 실패: {e}")
                
            # 상품명 클릭 후 편집 아이콘 찾기 시도
            if product_name:
                try:
                    # 페이지에서 상품명 텍스트 찾기
                    product_text = product_name.split(' ')[0]  # 첫 단어만 사용하여 검색
                    if len(product_text) > 3:  # 충분히 길면 사용
                        xpath = f"//span[contains(text(), '{product_text}')] | //div[contains(text(), '{product_text}')]"  
                        product_elements = self.driver.find_elements(By.XPATH, xpath)
                        
                        for element in product_elements:
                            if element.is_displayed():
                                # 요소로 스크롤
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                self.random_delay(1, 1)
                                
                                self.driver.execute_script("arguments[0].click();", element)
                                logging.info(f"상품 텍스트 '{product_text}' 클릭")
                                self.random_delay(1, 2)
                                
                                # 편집 아이콘 찾기
                                edit_icons = self.driver.find_elements(By.XPATH, 
                                    "//span[contains(@class, 'edit')] | //button[contains(@class, 'edit')] | //i[contains(@class, 'edit')]")
                                
                                for icon in edit_icons:
                                    if icon.is_displayed():
                                        self.driver.execute_script("arguments[0].click();", icon)
                                        logging.info("편집 아이콘 JavaScript 클릭")
                                        self.random_delay(2, 3)
                                        
                                        # 모달창 확인
                                        try:
                                            modal = WebDriverWait(self.driver, 8).until(
                                                EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-modal-content, .ant-drawer-content"))
                                            )
                                            if modal.is_displayed():
                                                logging.info("모달창 열림 확인 - 편집 아이콘 방법")
                                                return product_name
                                        except TimeoutException:
                                            logging.warning("편집 아이콘 클릭 후 모달창이 열리지 않음")
                except Exception as e:
                    logging.warning(f"상품명 클릭 후 편집 아이콘 찾기 실패: {e}")
            
            # 모달창이 이미 열려있는지 확인
            try:
                modals = self.driver.find_elements(By.CSS_SELECTOR, ".ant-modal-content, .ant-drawer-content")
                if any(modal.is_displayed() for modal in modals):
                    logging.info("모달창이 이미 열려있음을 감지")
                    return product_name
            except Exception as e:
                logging.warning(f"모달창 확인 실패: {e}")
                
            # 모든 시도 실패 시
            logging.error("모든 상품 선택 방법 실패")
            return None
        except Exception as e:
            logging.error(f"상품 선택 시 오류 발생: {e}")
            return None
    
    def select_tab(self, tab_name):
        """상품 수정 모달창에서 탭 선택"""
        try:
            logging.info(f"'{tab_name}' 탭으로 이동 시도")
            
            # 탭 선택자 정의 (여러 가능한 선택자)
            tab_selectors = {
                "기본정보": [
                    "//div[contains(@class, 'ant-tabs-tab')]//span[contains(text(), '기본정보')]",
                    "//div[contains(@class, 'ant-tabs-tab') and contains(., '기본정보')]",
                    "//div[contains(@class, 'ant-tabs-tab')][1]",  # 첫 번째 탭
                ],
                "상세정보": [
                    "//div[contains(@class, 'ant-tabs-tab')]//span[contains(text(), '상세정보')]",
                    "//div[contains(@class, 'ant-tabs-tab') and contains(., '상세정보')]",
                    "//div[contains(@class, 'ant-tabs-tab')][2]",  # 두 번째 탭
                ],
                "메모": [
                    "//div[contains(@class, 'ant-tabs-tab')]//span[contains(text(), '메모')]",
                    "//div[contains(@class, 'ant-tabs-tab') and contains(., '메모')]",
                    "//div[contains(@class, 'ant-tabs-tab')][3]",  # 세 번째 탭
                ],
                "업로드정보": [
                    "//div[contains(@class, 'ant-tabs-tab')]//span[contains(text(), '업로드정보')]",
                    "//div[contains(@class, 'ant-tabs-tab') and contains(., '업로드정보')]",
                    "//div[contains(@class, 'ant-tabs-tab')][4]",  # 네 번째 탭
                ]
            }
            
            if tab_name not in tab_selectors:
                logging.error(f"알 수 없는 탭 이름: {tab_name}")
                return False
            
            # 스크린샷 찍기 (디버깅용)
            try:
                self.driver.save_screenshot(f"before_{tab_name}_tab.png")
                logging.info(f"{tab_name} 탭 클릭 전 화면 스크린샷 저장: before_{tab_name}_tab.png")
            except:
                pass
                
            # 여러 선택자 시도
            for selector in tab_selectors[tab_name]:
                try:
                    tab_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # JavaScript로 클릭 시도
                    self.driver.execute_script("arguments[0].click();", tab_element)
                    logging.info(f"'{tab_name}' 탭 JavaScript 클릭 성공: {selector}")
                    self.random_delay(1, 2)
                    
                    # 스크린샷 찍기 (디버깅용)
                    try:
                        self.driver.save_screenshot(f"after_{tab_name}_tab.png")
                        logging.info(f"{tab_name} 탭 클릭 후 화면 스크린샷 저장: after_{tab_name}_tab.png")
                    except:
                        pass
                    
                    return True
                except Exception as e:
                    logging.warning(f"'{tab_name}' 탭 클릭 실패 ({selector}): {e}")
                    continue
            
            # 모든 선택자 실패 시
            logging.error(f"'{tab_name}' 탭 클릭 실패 (모든 방법)")
            return False
        except Exception as e:
            logging.error(f"'{tab_name}' 탭 이동 중 오류 발생: {e}")
            return False
    
    def _try_click_edit_button(self, product_row, product_name):
        """편집 버튼 찾아서 클릭 시도"""
        try:
            edit_buttons = product_row.find_elements(By.XPATH, ".//button[contains(@class, 'edit') or contains(@class, 'modify')]")
            if edit_buttons:
                edit_buttons[0].click()
                return True
            return False
        except Exception as e:
            logging.warning(f"편집 버튼 클릭 실패: {e}")
            return False
    
    def _try_context_menu(self, product_row, product_name):
        """오른쪽 클릭으로 컨텍스트 메뉴 열기 시도"""
        try:
            # 상품명 셀 찾기
            name_cells = product_row.find_elements(By.XPATH, ".//td[2]")
            if not name_cells:
                return False
                
            # 컨텍스트 메뉴 열기
            actions = ActionChains(self.driver)
            actions.context_click(name_cells[0]).perform()
            self.random_delay(0.5, 1)
            
            # 수정 메뉴 항목 클릭
            edit_menu_items = self.driver.find_elements(By.XPATH, "//li[contains(text(), '수정') or contains(text(), '편집')]")
            if edit_menu_items:
                edit_menu_items[0].click()
                return True
            
            # 메뉴 닫기 (ESC 키)
            actions.send_keys(Keys.ESCAPE).perform()
            return False
        except Exception as e:
            logging.warning(f"컨텍스트 메뉴 사용 실패: {e}")
            return False
    
    def _try_find_edit_icon(self, product_row, product_name):
        """페이지 전체에서 편집 아이콘 찾기 시도"""
        try:
            # 행 클릭하여 활성화
            try:
                product_row.click()
                self.random_delay(0.5, 1)
            except:
                pass
                
            # 편집 아이콘 찾기 (다양한 선택자 시도)
            icon_selectors = [
                "//button[contains(@class, 'edit-icon')]",
                "//span[contains(@class, 'edit-icon')]",
                "//i[contains(@class, 'edit-icon')]",
                "//i[contains(@class, 'anticon-edit')]",
                "//button//i[contains(@class, 'anticon-edit')]",
                "//button[contains(@title, '수정') or contains(@title, '편집')]",
                "//button[contains(@aria-label, '수정') or contains(@aria-label, '편집')]"
            ]
            
            for selector in icon_selectors:
                icons = self.driver.find_elements(By.XPATH, selector)
                for icon in icons:
                    if icon.is_displayed():
                        icon.click()
                        return True
            
            return False
        except Exception as e:
            logging.warning(f"편집 아이콘 찾기 실패: {e}")
            return False
    
    def _try_click_product_name(self, product_row, product_name):
        """상품명 요소 클릭 시도"""
        try:
            name_cells = product_row.find_elements(By.XPATH, ".//td[2]")
            if name_cells:
                name_cells[0].click()
                self.random_delay(0.5, 1)
                return True
            return False
        except Exception as e:
            logging.warning(f"상품명 클릭 실패: {e}")
            return False
    
    def _try_double_click_row(self, product_row, product_name):
        """상품 행 더블 클릭 시도"""
        try:
            actions = ActionChains(self.driver)
            actions.double_click(product_row).perform()
            self.random_delay(0.5, 1)
            return True
        except Exception as e:
            logging.warning(f"행 더블 클릭 실패: {e}")
            return False
