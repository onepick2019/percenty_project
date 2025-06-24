#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 확장 프로그램을 Chrome 웹스토어에서 직접 다운로드하여 key 값을 추출하는 스크립트

이 스크립트는 다음 작업을 수행합니다:
1. Chrome 웹스토어에서 퍼센티 확장 프로그램 CRX 파일 다운로드
2. CRX 파일에서 ZIP 아카이브 추출
3. manifest.json에서 key 값 추출
4. 로컬 manifest.json에 key 값 적용
"""

import os
import json
import shutil
import subprocess
import zipfile
import tempfile
from pathlib import Path
import requests

def download_crx_from_webstore(extension_id):
    """Chrome 웹스토어에서 CRX 파일을 다운로드합니다."""
    print(f"🌐 Chrome 웹스토어에서 CRX 다운로드 중: {extension_id}")
    
    # Chrome 웹스토어 CRX 다운로드 URL
    base_url = "https://clients2.google.com/service/update2/crx"
    params = {
        "response": "redirect",
        "os": "win",
        "arch": "x86-64",
        "os_arch": "x86-64",
        "prod": "chromecrx",
        "prodchannel": "stable",
        "prodversion": "120.0.6099.109",
        "lang": "ko",
        "x": f"id={extension_id}&uc"
    }
    
    try:
        # CRX 파일 다운로드
        response = requests.get(base_url, params=params, allow_redirects=True, timeout=30)
        response.raise_for_status()
        
        # CRX 파일 저장
        crx_filename = f"{extension_id}.crx"
        with open(crx_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ CRX 파일 다운로드 완료: {crx_filename}")
        print(f"   파일 크기: {len(response.content):,} bytes")
        return crx_filename
        
    except requests.RequestException as e:
        print(f"❌ CRX 다운로드 실패: {e}")
        return None
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return None

def extract_crx_file(crx_filename):
    """CRX 파일에서 ZIP 아카이브를 추출합니다."""
    print(f"📦 CRX 파일 추출 중: {crx_filename}")
    
    try:
        with open(crx_filename, 'rb') as f:
            # CRX 헤더 읽기
            magic = f.read(4)
            if magic != b'Cr24':
                print(f"❌ 유효하지 않은 CRX 파일: {crx_filename}")
                return None
            
            version = int.from_bytes(f.read(4), 'little')
            print(f"   CRX 버전: {version}")
            
            if version == 2:
                # CRX2 형식
                pub_key_len = int.from_bytes(f.read(4), 'little')
                sig_len = int.from_bytes(f.read(4), 'little')
                
                # 공개키와 서명 건너뛰기
                f.read(pub_key_len + sig_len)
                
            elif version == 3:
                # CRX3 형식
                header_len = int.from_bytes(f.read(4), 'little')
                f.read(header_len)  # 헤더 건너뛰기
            
            else:
                print(f"❌ 지원하지 않는 CRX 버전: {version}")
                return None
            
            # ZIP 데이터 읽기
            zip_data = f.read()
        
        # 임시 디렉토리에 ZIP 파일 저장
        temp_dir = tempfile.mkdtemp()
        zip_filename = os.path.join(temp_dir, 'extension.zip')
        
        with open(zip_filename, 'wb') as f:
            f.write(zip_data)
        
        # ZIP 파일 추출
        extract_dir = os.path.join(temp_dir, 'extracted')
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"✅ CRX 파일 추출 완료: {extract_dir}")
        return extract_dir
        
    except Exception as e:
        print(f"❌ CRX 파일 추출 실패: {e}")
        return None

def extract_key_from_extracted_manifest(extract_dir):
    """추출된 디렉토리에서 manifest.json의 key 값을 추출합니다."""
    manifest_path = os.path.join(extract_dir, 'manifest.json')
    
    if not os.path.exists(manifest_path):
        print(f"❌ manifest.json을 찾을 수 없습니다: {manifest_path}")
        return None
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        key = manifest.get('key')
        if key:
            print(f"✅ Key 값 추출 성공")
            print(f"   Key 길이: {len(key)} 문자")
            print(f"   확장 프로그램 이름: {manifest.get('name', 'Unknown')}")
            print(f"   버전: {manifest.get('version', 'Unknown')}")
            return key
        else:
            print("❌ manifest.json에 key 필드가 없습니다.")
            print("   웹스토어 버전에는 key 필드가 포함되지 않을 수 있습니다.")
            return None
            
    except Exception as e:
        print(f"❌ manifest.json 읽기 실패: {e}")
        return None

def generate_key_from_extension_id(extension_id):
    """확장 프로그램 ID를 기반으로 key 값을 생성합니다."""
    print(f"🔑 확장 프로그램 ID를 기반으로 key 생성 시도: {extension_id}")
    
    # 확장 프로그램 ID는 공개키의 SHA256 해시의 첫 32자를 a-p로 변환한 것
    # 역변환은 불가능하므로 대안 방법 사용
    
    print("❌ 확장 프로그램 ID에서 key 값을 역산하는 것은 불가능합니다.")
    print("   다른 방법을 시도해야 합니다.")
    return None

def update_local_manifest_with_key(key_value):
    """로컬 manifest.json에 key 값을 추가합니다."""
    manifest_path = "manifest.json"
    
    if not os.path.exists(manifest_path):
        print(f"❌ 로컬 manifest.json을 찾을 수 없습니다: {manifest_path}")
        return False
    
    try:
        # 백업 생성
        shutil.copy2(manifest_path, f"{manifest_path}.backup")
        print(f"✅ 백업 생성: {manifest_path}.backup")
        
        # manifest.json 읽기
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # key 값 추가
        manifest['key'] = key_value
        
        # manifest.json 쓰기
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"✅ manifest.json에 key 값 추가 완료")
        return True
        
    except Exception as e:
        print(f"❌ manifest.json 업데이트 실패: {e}")
        return False

def create_alternative_solution_guide():
    """대안 해결책 가이드를 생성합니다."""
    guide_content = """# 퍼센티 확장 프로그램 동일 ID 생성 대안 방법

## 문제 상황
웹스토어에서 다운로드한 CRX 파일에는 key 필드가 없어서 동일한 ID를 생성할 수 없습니다.

## 대안 해결책

### 방법 1: Chrome Extension Source Viewer 사용
1. Chrome 웹스토어에서 "Chrome Extension Source Viewer" 설치
2. 퍼센티 확장 프로그램 페이지에서 Source Viewer 실행
3. 콘솔에서 key 값 확인

### 방법 2: 개발자 도구 사용
1. Chrome에서 퍼센티 확장 프로그램 설치
2. chrome://extensions/ 에서 개발자 모드 활성화
3. "확장 프로그램 패키징" 클릭
4. 설치된 확장 프로그램 디렉토리 선택
5. 생성된 .pem 파일로 key 값 생성

### 방법 3: 수동 key 생성
1. OpenSSL 사용하여 RSA 키 쌍 생성
2. 공개키를 Base64로 인코딩
3. manifest.json에 key 필드 추가

### 방법 4: 웹스토어 ID 무시하고 새 ID 사용
1. 새로운 key 값으로 고유한 ID 생성
2. 퍼센티 웹사이트에서 새 ID 인식하도록 요청
3. 또는 확장 프로그램 코드 수정으로 인식 개선

## 권장 방법
가장 확실한 방법은 **방법 2 (개발자 도구 사용)**입니다:

```bash
# 1. 퍼센티 확장 프로그램을 웹스토어에서 설치
# 2. 다음 스크립트 실행
python extract_percenty_key.py

# 3. 만약 key가 없다면 개발자 도구로 패키징
# chrome://extensions/ -> 개발자 모드 -> 확장 프로그램 패키징
```

## 다음 단계
1. 위 방법 중 하나를 선택하여 key 값 획득
2. manifest.json에 key 값 추가
3. CRX 파일 재생성
4. 테스트 및 검증

## 주의사항
- key 값은 확장 프로그램의 고유 식별자입니다
- 잘못된 key 사용 시 다른 확장 프로그램과 충돌할 수 있습니다
- 웹스토어 업로드 시에는 key 필드를 제거해야 합니다
"""
    
    with open("ALTERNATIVE_SOLUTION_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✅ 대안 해결책 가이드 생성: ALTERNATIVE_SOLUTION_GUIDE.md")

def main():
    print("🚀 퍼센티 확장 프로그램 CRX 다운로드 및 Key 추출 시작")
    print("=" * 60)
    
    # 퍼센티 확장 프로그램 ID
    percenty_extension_id = "jlcdjppbpplpdgfeknhioedbhfceaben"
    
    # 1. CRX 파일 다운로드
    crx_filename = download_crx_from_webstore(percenty_extension_id)
    
    if not crx_filename:
        print("❌ CRX 다운로드 실패")
        create_alternative_solution_guide()
        return
    
    # 2. CRX 파일 추출
    extract_dir = extract_crx_file(crx_filename)
    
    if not extract_dir:
        print("❌ CRX 파일 추출 실패")
        create_alternative_solution_guide()
        return
    
    # 3. Key 값 추출
    key_value = extract_key_from_extracted_manifest(extract_dir)
    
    if key_value:
        # 4. 로컬 manifest.json 업데이트
        print(f"\n📝 로컬 manifest.json 업데이트 중...")
        if update_local_manifest_with_key(key_value):
            print("\n🎉 Key 추출 및 적용 완료!")
            print("=" * 60)
            print(f"✅ 확장 프로그램 ID: {percenty_extension_id}")
            print(f"✅ Key 값이 manifest.json에 추가되었습니다.")
            print(f"✅ 이제 build_crx.py를 실행하여 동일한 ID로 CRX를 생성할 수 있습니다.")
            
            print("\n📋 다음 단계:")
            print("1. python build_crx.py")
            print("2. Chrome 개발자 모드에서 CRX 설치")
            print("3. 퍼센티 웹사이트에서 확장 프로그램 인식 확인")
        else:
            print("❌ 로컬 manifest.json 업데이트 실패")
    else:
        print("\n❌ Key 값을 추출할 수 없습니다.")
        print("   웹스토어 CRX 파일에는 key 필드가 포함되지 않습니다.")
        create_alternative_solution_guide()
        
        print("\n💡 대안 방법:")
        print("1. ALTERNATIVE_SOLUTION_GUIDE.md 파일을 참조하세요")
        print("2. Chrome Extension Source Viewer 사용")
        print("3. 개발자 도구로 확장 프로그램 패키징")
        print("4. 새로운 key 생성 후 사용")
    
    # 5. 임시 파일 정리
    try:
        if extract_dir and os.path.exists(extract_dir):
            shutil.rmtree(os.path.dirname(extract_dir))
        if crx_filename and os.path.exists(crx_filename):
            os.remove(crx_filename)
        print("\n🧹 임시 파일 정리 완료")
    except Exception as e:
        print(f"⚠️ 임시 파일 정리 중 오류: {e}")

if __name__ == "__main__":
    main()