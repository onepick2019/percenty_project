# 키워드 순환 처리 로직 구현 예시

## Step3_1_1_Core 클래스 수정 예시

### 1. 새로운 메서드 추가

```python
def _process_keywords_with_target_quantity(self, provider_codes: List[str], matching_tasks_dict: Dict, target_quantity: int = 200) -> Tuple[bool, int, List[str]]:
    """
    키워드 순환 처리로 목표 수량 달성
    
    Args:
        provider_codes: 처리할 키워드 목록
        matching_tasks_dict: 키워드별 작업 목록 딕셔너리
        target_quantity: 목표 처리 수량 (기본값: 200)
        
    Returns:
        Tuple[bool, int, List[str]]: (성공 여부, 총 처리된 상품 수, 완료된 키워드 목록)
    """
    total_processed = 0
    completed_keywords = []
    remaining_keywords = provider_codes.copy()
    cycle_count = 0
    MAX_CYCLES = 10  # 무한 루프 방지
    
    logger.info(f"키워드 순환 처리 시작 - 목표 수량: {target_quantity}개, 키워드 수: {len(provider_codes)}개")
    
    while total_processed < target_quantity and remaining_keywords and cycle_count < MAX_CYCLES:
        cycle_count += 1
        cycle_start_processed = total_processed
        keywords_to_remove = []
        
        logger.info(f"===== {cycle_count}차 순환 시작 (목표: {target_quantity}, 현재: {total_processed}, 남은 키워드: {len(remaining_keywords)}개) =====")
        
        for keyword in remaining_keywords:
            if total_processed >= target_quantity:
                logger.info(f"목표 수량 {target_quantity}개 달성으로 순환 중단")
                break
                
            try:
                logger.info(f"키워드 '{keyword}' 처리 시작 ({cycle_count}차 순환)")
                
                # 키워드별 작업 목록 가져오기
                matching_tasks = matching_tasks_dict.get(keyword, [])
                if not matching_tasks:
                    logger.warning(f"키워드 '{keyword}'에 대한 작업이 없습니다")
                    keywords_to_remove.append(keyword)
                    continue
                
                # 기존 키워드 처리 로직 호출
                success, processed_count = self._process_keyword(keyword, matching_tasks)
                
                if success:
                    total_processed += processed_count
                    logger.info(f"키워드 '{keyword}' 처리 완료: {processed_count}개 (총: {total_processed}개)")
                    
                    # 20개 미만 처리된 경우 해당 키워드 완료로 간주
                    if processed_count < 20:
                        keywords_to_remove.append(keyword)
                        completed_keywords.append(keyword)
                        logger.info(f"키워드 '{keyword}' 완료 (처리된 상품이 20개 미만)")
                else:
                    logger.warning(f"키워드 '{keyword}' 처리 실패")
                    # 실패한 키워드도 제거하여 무한 루프 방지
                    keywords_to_remove.append(keyword)
                    
            except Exception as e:
                logger.error(f"키워드 '{keyword}' 처리 중 오류: {e}")
                keywords_to_remove.append(keyword)
        
        # 완료된 키워드 제거
        for keyword in keywords_to_remove:
            if keyword in remaining_keywords:
                remaining_keywords.remove(keyword)
        
        cycle_processed = total_processed - cycle_start_processed
        logger.info(f"{cycle_count}차 순환 완료 - 이번 순환 처리량: {cycle_processed}개, 총 처리량: {total_processed}개, 남은 키워드: {len(remaining_keywords)}개")
        
        # 이번 순환에서 아무것도 처리하지 못한 경우 중단
        if cycle_processed == 0:
            logger.warning("이번 순환에서 처리된 상품이 없어 순환 중단")
            break
            
        # 순환 간 짧은 대기 (브라우저 안정성)
        if remaining_keywords and total_processed < target_quantity:
            time.sleep(2)
    
    # 최종 결과 로깅
    success = total_processed >= target_quantity
    if success:
        logger.info(f"목표 수량 달성! 총 {total_processed}개 처리 완료 ({cycle_count}차 순환)")
    else:
        logger.warning(f"목표 수량 미달성: {total_processed}/{target_quantity}개 처리 ({cycle_count}차 순환)")
    
    return success, total_processed, completed_keywords

def _prepare_matching_tasks_dict(self, provider_codes: List[str], task_list: List[Dict]) -> Dict[str, List[Dict]]:
    """
    키워드별 작업 목록 딕셔너리 생성
    
    Args:
        provider_codes: 처리할 키워드 목록
        task_list: 전체 작업 목록
        
    Returns:
        Dict[str, List[Dict]]: 키워드별 작업 목록 딕셔너리
    """
    matching_tasks_dict = {}
    
    for provider_code in provider_codes:
        matching_tasks = [task for task in task_list if task.get('provider_code') == provider_code]
        matching_tasks_dict[provider_code] = matching_tasks
        logger.debug(f"키워드 '{provider_code}': {len(matching_tasks)}개 작업")
    
    return matching_tasks_dict
```

### 2. 기존 execute_step3_1_1 메서드 수정

```python
def execute_step3_1_1(self, provider_codes: List[str], account_info: Dict = None, target_quantity: int = 200) -> Dict:
    """
    3단계_1_1 작업 실행 (순환 처리 방식)
    
    Args:
        provider_codes: 처리할 키워드(provider_code) 목록
        account_info: 계정 정보 (엑셀 파일에서 읽은 계정 정보)
        target_quantity: 목표 처리 수량 (기본값: 200)
        
    Returns:
        Dict: 실행 결과
    """
    result = {
        'success': False,
        'processed_keywords': 0,
        'failed_keywords': 0,
        'total_products_processed': 0,
        'target_quantity': target_quantity,
        'target_achieved': False,
        'cycles_completed': 0,
        'errors': [],
        'completed_keywords': [],
        'failed_keywords_list': []
    }
    
    try:
        logger.info(f"3단계_1_1 작업 시작 (서버: {self.server_name}) - 처리 예정 키워드: {len(provider_codes)}개, 목표 수량: {target_quantity}개")
        
        # 1. 로그인 후 모달 처리
        if not self._handle_post_login_modals():
            logger.warning("로그인 후 모달 처리 실패 - 하지만 작업을 계속 진행합니다")
        
        # 2. 채널톡 숨기기
        if not self._hide_channel_talk():
            logger.warning("채널톡 숨기기 실패 - 계속 진행")
        
        # 3. 계정 일치 확인 (선택적)
        if account_info:
            try:
                logger.info(f"계정 매핑 확인 시작 - 가상ID: {account_info.get('id', 'Unknown')}")
                if not self._verify_account_match(account_info):
                    logger.warning("계정 일치 확인 실패 - 하지만 작업을 계속 진행합니다")
            except Exception as e:
                logger.warning(f"계정 일치 확인 중 오류 발생 - 계속 진행합니다: {e}")
        
        # 4. 등록상품 메뉴로 이동
        if not self._navigate_to_registered_products():
            raise Exception("등록상품 메뉴 이동 실패")
        
        # 5. UI 초기 설정
        if not self._setup_initial_ui():
            logger.warning("UI 초기 설정 실패 - 하지만 작업을 계속 진행합니다")
        
        # 6. 엑셀에서 작업 목록 로드 (서버 필터링 포함)
        if not account_info:
            raise Exception("계정 정보가 필요합니다")
        
        account_id = account_info.get('id')
        if not account_id:
            raise Exception("계정 ID가 없습니다")
        
        # 가상 ID를 실제 이메일로 변환
        from batch.batch_manager import get_real_account_id
        real_account_id = get_real_account_id(account_id)
        logger.info(f"작업 목록 로드를 위한 계정 ID 변환: {account_id} -> {real_account_id}")
        
        task_list = self.product_editor.load_task_list_from_excel_with_server_filter(
            account_id=real_account_id,
            step="step3",
            server_name=self.server_name
        )
        
        if not task_list:
            logger.warning(f"서버 {self.server_name}에 대한 작업 목록이 없습니다")
            result['success'] = True  # 작업할 것이 없는 것은 성공으로 간주
            return result
        
        logger.info(f"로드된 작업 목록: {len(task_list)}개")
        
        # 7. 키워드별 작업 목록 딕셔너리 생성
        matching_tasks_dict = self._prepare_matching_tasks_dict(provider_codes, task_list)
        
        # 8. 순환 처리로 목표 수량 달성
        target_achieved, total_processed, completed_keywords = self._process_keywords_with_target_quantity(
            provider_codes, matching_tasks_dict, target_quantity
        )
        
        # 9. 결과 업데이트
        result['total_products_processed'] = total_processed
        result['target_achieved'] = target_achieved
        result['completed_keywords'] = completed_keywords
        result['processed_keywords'] = len(completed_keywords)
        result['failed_keywords'] = len(provider_codes) - len(completed_keywords)
        result['success'] = target_achieved and len(completed_keywords) > 0
        
        logger.info(f"3단계_1_1 작업 완료 (서버: {self.server_name}) - 처리된 키워드: {result['processed_keywords']}, 실패: {result['failed_keywords']}, 총 처리된 상품: {result['total_products_processed']}, 목표 달성: {target_achieved}")
        
    except Exception as e:
        error_msg = f"3단계_1_1 작업 중 치명적 오류: {str(e)}"
        logger.error(error_msg)
        logger.error(f"오류 상세: {traceback.format_exc()}")
        result['errors'].append(error_msg)
        result['success'] = False
    
    return result
```

### 3. 설정 파일 수정 (periodic_config.json)

```json
{
  "step3_target_quantity": 200,
  "step3_max_cycles": 10,
  "step3_cycle_delay": 2,
  "step3_keyword_limit_per_cycle": 20
}
```

### 4. 호출부 수정 예시

```python
# 기존 호출 방식
result = step3_core.execute_step3_1_1(provider_codes, account_info)

# 새로운 호출 방식 (목표 수량 지정)
result = step3_core.execute_step3_1_1(provider_codes, account_info, target_quantity=200)

# 결과 확인
if result['target_achieved']:
    print(f"목표 달성! {result['total_products_processed']}개 처리 완료")
else:
    print(f"목표 미달성: {result['total_products_processed']}/{result['target_quantity']}개 처리")
```

## 구현 시 주의사항

### 1. 브라우저 안정성
```python
# 순환 간 브라우저 상태 확인
def _verify_browser_stability_between_cycles(self):
    try:
        self.driver.current_url
        return True
    except Exception as e:
        logger.error(f"브라우저 연결 오류: {e}")
        return False
```

### 2. 메모리 관리
```python
# 3순환마다 메모리 정리
if cycle_count % 3 == 0:
    logger.info("순환 처리 중 메모리 정리 수행")
    self.driver.execute_script("window.gc && window.gc();")
    time.sleep(1)
```

### 3. 진행률 모니터링
```python
# 진행률 계산 및 로깅
progress_percentage = (total_processed / target_quantity) * 100
logger.info(f"진행률: {progress_percentage:.1f}% ({total_processed}/{target_quantity})")
```

## 테스트 시나리오

### 1. 정상 케이스
- 키워드 10개, 각각 20개 이상 상품 보유
- 예상 결과: 1차 순환에서 200개 달성

### 2. 불균등 케이스
- 키워드 10개, 상품 수 불균등 (0~50개)
- 예상 결과: 2-3차 순환으로 200개 달성

### 3. 부족 케이스
- 키워드 10개, 총 상품 수 150개
- 예상 결과: 모든 상품 처리 후 150개로 종료

## 기대 효과

1. **처리량 향상**: 평균 140개 → 200개 (43% 향상)
2. **예측 가능성**: 목표 수량 달성으로 배치 시간 예측 가능
3. **효율성**: 키워드별 상품 불균등 문제 해결
4. **안정성**: 기존 로직 재사용으로 안정성 보장