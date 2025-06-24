#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 웹스토어 확장 프로그램 Key 추출 및 CRX 수정 스크립트

이 스크립트는 다음 작업을 수행합니다:
1. 퍼센티 웹스토어 확장 프로그램 CRX 다운로드
2. CRX 파일에서 key 값 추출
3. 로컬 manifest.json에 key 값 적용
4. 동일한 ID로 CRX 재생성
"""

import os
import json
import requests
import zipfile
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# 퍼센티 확장 프로그램 정보
PERCENTY_EXTENSION_ID = "jlcdjppbpplpdgfeknhioedbhfceaben"
PERCENTY_WEBSTORE_URL = f"https://chromewebstore.google.com/detail/%ED%8D%BC%EC%84%BC%ED%8B%B0/{PERCENTY_EXTENSION_ID}"
CRX_DOWNLOAD_URL = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=91.0.4472.124&acceptformat=crx2,crx3&x=id%3D{PERCENTY_EXTENSION_ID}%26uc"

def log_message(message):
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def download_webstore_crx():
    """웹스토어에서 퍼센티 CRX 파일 다운로드"""
    log_message("퍼센티 웹스토어 CRX 파일 다운로드 중...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(CRX_DOWNLOAD_URL, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        crx_path = "percenty_webstore.crx"
        with open(crx_path, 'wb') as f:
            f.write(response.content)
        
        log_message(f"CRX 파일 다운로드 완료: {crx_path}")
        return crx_path
        
    except Exception as e:
        log_message(f"CRX 다운로드 실패: {e}")
        return None

def extract_key_from_crx(crx_path):
    """CRX 파일에서 key 값 추출"""
    log_message("CRX 파일에서 key 값 추출 중...")
    
    try:
        # CRX 파일을 임시 디렉터리에 압축 해제
        with tempfile.TemporaryDirectory() as temp_dir:
            # CRX 파일은 헤더를 제거하고 ZIP으로 처리해야 함
            with open(crx_path, 'rb') as f:
                crx_data = f.read()
            
            # CRX3 헤더 건너뛰기 (일반적으로 처음 몇 바이트)
            # CRX 파일 구조: magic number (4) + version (4) + header length (4) + header + zip data
            if crx_data[:4] == b'Cr24':
                # CRX3 형식
                header_length = int.from_bytes(crx_data[8:12], 'little')
                zip_start = 12 + header_length
            else:
                # 다른 형식 시도
                zip_start = 16  # 기본값
            
            zip_data = crx_data[zip_start:]
            
            # ZIP 데이터를 임시 파일로 저장
            temp_zip = os.path.join(temp_dir, 'extension.zip')
            with open(temp_zip, 'wb') as f:
                f.write(zip_data)
            
            # ZIP 파일 압축 해제
            extract_dir = os.path.join(temp_dir, 'extracted')
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # manifest.json에서 key 값 읽기
            manifest_path = os.path.join(extract_dir, 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                
                key_value = manifest_data.get('key')
                if key_value:
                    log_message("웹스토어 key 값 추출 성공")
                    return key_value
                else:
                    log_message("manifest.json에 key 필드가 없습니다")
            else:
                log_message("manifest.json 파일을 찾을 수 없습니다")
                
    except Exception as e:
        log_message(f"Key 추출 실패: {e}")
    
    return None

def update_local_manifest_with_key(key_value):
    """로컬 manifest.json에 key 값 적용"""
    log_message("로컬 manifest.json에 key 값 적용 중...")
    
    try:
        # 기존 manifest.json 백업
        manifest_path = "manifest.json"
        backup_path = f"manifest_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if os.path.exists(manifest_path):
            shutil.copy2(manifest_path, backup_path)
            log_message(f"기존 manifest.json 백업: {backup_path}")
        
        # manifest.json 읽기
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        # key 값 추가
        manifest_data['key'] = key_value
        
        # update_url 제거 (CRX 전용)
        if 'update_url' in manifest_data:
            del manifest_data['update_url']
        
        # manifest.json 저장
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
        log_message("로컬 manifest.json 업데이트 완료")
        return True
        
    except Exception as e:
        log_message(f"Manifest 업데이트 실패: {e}")
        return False

def create_key_extraction_report(key_value):
    """Key 추출 보고서 생성"""
    report_content = f"""# 퍼센티 확장 프로그램 Key 추출 보고서

## 추출 일시
{datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}

## 확장 프로그램 정보
- **확장 프로그램 ID**: {PERCENTY_EXTENSION_ID}
- **웹스토어 URL**: {PERCENTY_WEBSTORE_URL}

## 추출된 Key 값
```
{key_value}
```

## 적용 결과
- 로컬 manifest.json에 key 값이 적용되었습니다
- 이제 CRX 설치 시 웹스토어 확장 프로그램과 동일한 ID를 가집니다
- 웹스토어에서 "Chrome에 추가" 버튼이 비활성화됩니다

## 다음 단계
1. Chrome에서 기존 퍼센티 확장 프로그램 제거
2. 수정된 CRX 파일로 재설치
3. 퍼센티 웹사이트에서 확장 프로그램 인식 확인
4. 웹스토어 페이지에서 중복 설치 방지 확인

## 주의사항
- key 값이 적용된 manifest.json은 웹스토어 업로드 시 제거해야 합니다
- 개발 중에는 key 값을 유지하여 일관된 확장 프로그램 ID를 보장합니다
"""
    
    with open("KEY_EXTRACTION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    log_message("Key 추출 보고서 생성 완료: KEY_EXTRACTION_REPORT.md")

def main():
    """메인 실행 함수"""
    log_message("=== 퍼센티 웹스토어 Key 추출 시작 ===")
    
    # 1. 웹스토어 CRX 다운로드
    crx_path = download_webstore_crx()
    if not crx_path:
        log_message("CRX 다운로드 실패로 종료")
        return False
    
    # 2. Key 값 추출
    key_value = extract_key_from_crx(crx_path)
    if not key_value:
        log_message("Key 추출 실패로 종료")
        return False
    
    # 3. 로컬 manifest.json 업데이트
    if not update_local_manifest_with_key(key_value):
        log_message("Manifest 업데이트 실패로 종료")
        return False
    
    # 4. 보고서 생성
    create_key_extraction_report(key_value)
    
    # 5. 임시 파일 정리
    if os.path.exists(crx_path):
        os.remove(crx_path)
        log_message("임시 CRX 파일 삭제")
    
    log_message("=== Key 추출 및 적용 완료 ===")
    log_message("")
    log_message("다음 단계:")
    log_message("1. Chrome에서 기존 퍼센티 확장 프로그램 제거")
    log_message("2. chrome://extensions/에서 개발자 모드 활성화")
    log_message("3. '확장 프로그램 패키징'으로 새 CRX 생성")
    log_message("4. 새 CRX 파일 설치 및 테스트")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 퍼센티 웹스토어 Key 추출 및 적용이 성공적으로 완료되었습니다!")
        else:
            print("\n❌ 작업 중 오류가 발생했습니다.")
    except KeyboardInterrupt:
        print("\n\n작업이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n예상치 못한 오류가 발생했습니다: {e}")