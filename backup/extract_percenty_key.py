#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 확장 프로그램의 실제 key 값을 추출하고 동일한 ID로 CRX를 생성하는 스크립트

이 스크립트는 다음 작업을 수행합니다:
1. Chrome 프로필 디렉토리에서 퍼센티 확장 프로그램 찾기
2. 설치된 확장 프로그램의 manifest.json에서 key 값 추출
3. 로컬 manifest.json에 key 값 적용
4. 동일한 ID로 CRX 재생성
"""

import os
import json
import shutil
import subprocess
import platform
from pathlib import Path

def get_chrome_profile_path():
    """Chrome 프로필 경로를 반환합니다."""
    system = platform.system()
    
    if system == "Windows":
        base_path = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    elif system == "Darwin":  # macOS
        base_path = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    else:  # Linux
        base_path = Path.home() / ".config" / "google-chrome"
    
    # Default 프로필 경로
    default_profile = base_path / "Default"
    if default_profile.exists():
        return default_profile
    
    # Profile 1, 2 등 다른 프로필 찾기
    for profile_dir in base_path.glob("Profile *"):
        if profile_dir.is_dir():
            return profile_dir
    
    return default_profile

def find_percenty_extension(profile_path):
    """퍼센티 확장 프로그램을 찾습니다."""
    extensions_path = profile_path / "Extensions"
    
    if not extensions_path.exists():
        print(f"❌ Extensions 디렉토리를 찾을 수 없습니다: {extensions_path}")
        return None, None
    
    print(f"🔍 Extensions 디렉토리 검색 중: {extensions_path}")
    
    # 알려진 퍼센티 확장 프로그램 ID
    known_percenty_id = "jlcdjppbpplpdgfeknhioedbhfceaben"
    
    # 먼저 알려진 ID로 찾기
    known_path = extensions_path / known_percenty_id
    if known_path.exists():
        print(f"✅ 알려진 ID로 퍼센티 확장 프로그램 발견: {known_percenty_id}")
        return known_percenty_id, known_path
    
    # 모든 확장 프로그램 검색
    for ext_dir in extensions_path.iterdir():
        if not ext_dir.is_dir():
            continue
            
        # 버전 디렉토리 찾기
        for version_dir in ext_dir.iterdir():
            if not version_dir.is_dir():
                continue
                
            manifest_path = version_dir / "manifest.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    
                    name = manifest.get('name', '').lower()
                    if '퍼센티' in name or 'percenty' in name:
                        print(f"✅ 퍼센티 확장 프로그램 발견: {ext_dir.name}")
                        print(f"   이름: {manifest.get('name')}")
                        print(f"   버전: {manifest.get('version')}")
                        return ext_dir.name, ext_dir
                        
                except Exception as e:
                    continue
    
    print("❌ 퍼센티 확장 프로그램을 찾을 수 없습니다.")
    print("   Chrome 웹스토어에서 퍼센티 확장 프로그램을 먼저 설치해주세요.")
    return None, None

def extract_key_from_manifest(extension_path):
    """확장 프로그램 디렉토리에서 key 값을 추출합니다."""
    # 최신 버전 디렉토리 찾기
    version_dirs = [d for d in extension_path.iterdir() if d.is_dir()]
    if not version_dirs:
        return None
    
    # 버전 번호로 정렬하여 최신 버전 선택
    latest_version = sorted(version_dirs, key=lambda x: x.name)[-1]
    manifest_path = latest_version / "manifest.json"
    
    if not manifest_path.exists():
        return None
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        key = manifest.get('key')
        if key:
            print(f"✅ Key 값 추출 성공")
            print(f"   버전: {latest_version.name}")
            print(f"   Key 길이: {len(key)} 문자")
            return key
        else:
            print("❌ manifest.json에 key 필드가 없습니다.")
            return None
            
    except Exception as e:
        print(f"❌ manifest.json 읽기 실패: {e}")
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

def create_key_info_file(extension_id, key_value):
    """추출된 key 정보를 파일로 저장합니다."""
    info_content = f"""# 퍼센티 확장 프로그램 Key 정보

## 추출된 정보
- **확장 프로그램 ID**: `{extension_id}`
- **Key 값**: `{key_value}`
- **추출 시간**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 사용 방법
1. 이 key 값이 로컬 `manifest.json`에 추가되었습니다.
2. 이제 CRX를 생성하면 웹스토어와 동일한 ID를 가집니다.
3. Chrome에서 개발자 모드로 로드하면 웹스토어 버전과 충돌하지 않습니다.

## 주의사항
- 이 key 값은 퍼센티 확장 프로그램의 고유 식별자입니다.
- 다른 확장 프로그램에서 사용하지 마세요.
- 웹스토어에 업로드할 때는 key 필드를 제거해야 합니다.

## 다음 단계
1. `python build_crx.py` 실행하여 CRX 생성
2. Chrome 개발자 모드에서 CRX 설치
3. 퍼센티 웹사이트에서 확장 프로그램 인식 확인

## 문제 해결
만약 여전히 퍼센티에서 인식하지 못한다면:
1. Chrome에서 기존 퍼센티 확장 프로그램 완전 제거
2. Chrome 재시작
3. 새로 생성된 CRX 파일 설치
4. 퍼센티 웹사이트 새로고침
"""
    
    with open("PERCENTY_KEY_INFO.md", 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print(f"✅ Key 정보 파일 생성: PERCENTY_KEY_INFO.md")

def main():
    print("🚀 퍼센티 확장 프로그램 Key 추출 시작")
    print("=" * 50)
    
    # 1. Chrome 프로필 경로 찾기
    profile_path = get_chrome_profile_path()
    print(f"📁 Chrome 프로필 경로: {profile_path}")
    
    if not profile_path.exists():
        print(f"❌ Chrome 프로필을 찾을 수 없습니다: {profile_path}")
        print("   Chrome이 설치되어 있고 한 번 이상 실행되었는지 확인해주세요.")
        return
    
    # 2. 퍼센티 확장 프로그램 찾기
    extension_id, extension_path = find_percenty_extension(profile_path)
    
    if not extension_id:
        print("\n💡 해결 방법:")
        print("1. Chrome에서 https://chromewebstore.google.com/detail/퍼센티/jlcdjppbpplpdgfeknhioedbhfceaben 방문")
        print("2. '크롬에 추가' 버튼 클릭하여 확장 프로그램 설치")
        print("3. 설치 후 이 스크립트를 다시 실행")
        return
    
    # 3. Key 값 추출
    print(f"\n🔑 Key 값 추출 중...")
    key_value = extract_key_from_manifest(extension_path)
    
    if not key_value:
        print("❌ Key 값을 추출할 수 없습니다.")
        print("   웹스토어 버전에는 key 필드가 없을 수 있습니다.")
        print("\n💡 대안 방법:")
        print("1. Chrome Extension Source Viewer 사용")
        print("2. CRX Viewer 웹사이트 사용")
        print("3. 개발자 도구에서 확장 프로그램 패키징")
        return
    
    # 4. 로컬 manifest.json 업데이트
    print(f"\n📝 로컬 manifest.json 업데이트 중...")
    if update_local_manifest_with_key(key_value):
        # 5. 정보 파일 생성
        create_key_info_file(extension_id, key_value)
        
        print("\n🎉 Key 추출 및 적용 완료!")
        print("=" * 50)
        print(f"✅ 확장 프로그램 ID: {extension_id}")
        print(f"✅ Key 값이 manifest.json에 추가되었습니다.")
        print(f"✅ 이제 build_crx.py를 실행하여 동일한 ID로 CRX를 생성할 수 있습니다.")
        
        print("\n📋 다음 단계:")
        print("1. python build_crx.py")
        print("2. Chrome 개발자 모드에서 CRX 설치")
        print("3. 퍼센티 웹사이트에서 확장 프로그램 인식 확인")
    else:
        print("❌ 로컬 manifest.json 업데이트 실패")

if __name__ == "__main__":
    main()