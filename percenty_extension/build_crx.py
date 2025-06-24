#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 확장 프로그램 CRX 빌드 스크립트

이 스크립트는 다음 작업을 수행합니다:
1. 기존 manifest.json과 background.js 백업
2. 수정된 파일들로 교체
3. CRX 파일 생성을 위한 준비
4. 검증 및 테스트
"""

import os
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class CRXBuilder:
    def __init__(self, extension_dir):
        self.extension_dir = Path(extension_dir)
        self.backup_dir = self.extension_dir / 'backup'
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def log(self, message):
        """로그 메시지 출력"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def create_backup(self):
        """기존 파일들 백업"""
        self.log("기존 파일 백업 시작...")
        
        # 백업 디렉토리 생성
        backup_timestamp_dir = self.backup_dir / f'backup_{self.timestamp}'
        backup_timestamp_dir.mkdir(parents=True, exist_ok=True)
        
        # 백업할 파일들
        files_to_backup = [
            'manifest.json',
            'static/js/background.js'
        ]
        
        for file_path in files_to_backup:
            source = self.extension_dir / file_path
            if source.exists():
                # 백업 파일의 디렉토리 구조 생성
                backup_file = backup_timestamp_dir / file_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 파일 복사
                shutil.copy2(source, backup_file)
                self.log(f"백업 완료: {file_path}")
            else:
                self.log(f"파일을 찾을 수 없음: {file_path}")
                
        self.log(f"백업 완료: {backup_timestamp_dir}")
        return backup_timestamp_dir
        
    def apply_fixes(self):
        """수정된 파일들 적용"""
        self.log("수정된 파일 적용 시작...")
        
        # manifest_fixed.json을 manifest.json으로 복사
        fixed_manifest = self.extension_dir / 'manifest_fixed.json'
        target_manifest = self.extension_dir / 'manifest.json'
        
        if fixed_manifest.exists():
            shutil.copy2(fixed_manifest, target_manifest)
            self.log("manifest.json 업데이트 완료")
        else:
            self.log("오류: manifest_fixed.json을 찾을 수 없습니다.")
            return False
            
        # background_fixed.js를 static/js/background.js로 복사
        fixed_background = self.extension_dir / 'background_fixed.js'
        target_background = self.extension_dir / 'static' / 'js' / 'background.js'
        
        # static/js 디렉토리 생성 (존재하지 않는 경우)
        target_background.parent.mkdir(parents=True, exist_ok=True)
        
        if fixed_background.exists():
            shutil.copy2(fixed_background, target_background)
            self.log("background.js 업데이트 완료")
        else:
            self.log("오류: background_fixed.js를 찾을 수 없습니다.")
            return False
            
        return True
        
    def validate_manifest(self):
        """manifest.json 유효성 검사"""
        self.log("manifest.json 유효성 검사...")
        
        manifest_path = self.extension_dir / 'manifest.json'
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
                
            # 필수 필드 검사
            required_fields = ['manifest_version', 'name', 'version']
            for field in required_fields:
                if field not in manifest_data:
                    self.log(f"오류: 필수 필드 누락 - {field}")
                    return False
                    
            # Manifest V3 검사
            if manifest_data.get('manifest_version') != 3:
                self.log("오류: Manifest V3가 아닙니다.")
                return False
                
            # URL 패턴 검사
            if 'host_permissions' in manifest_data:
                for pattern in manifest_data['host_permissions']:
                    if pattern == '*://*/*':
                        self.log("경고: '*://*/*' 패턴이 발견되었습니다. 분리된 패턴 사용을 권장합니다.")
                        
            # Background script 경로 검사
            if 'background' in manifest_data:
                service_worker = manifest_data['background'].get('service_worker')
                if service_worker and service_worker.startswith('./'):
                    self.log("경고: Service worker 경로에 './' 접두사가 있습니다.")
                    
            self.log("manifest.json 유효성 검사 통과")
            return True
            
        except json.JSONDecodeError as e:
            self.log(f"오류: manifest.json JSON 파싱 실패 - {e}")
            return False
        except Exception as e:
            self.log(f"오류: manifest.json 검사 중 예외 발생 - {e}")
            return False
            
    def check_files(self):
        """필요한 파일들 존재 확인"""
        self.log("필요한 파일들 존재 확인...")
        
        required_files = [
            'manifest.json',
            'static/js/background.js',
            'index.html',
            'percenty_logo.png'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.extension_dir / file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            self.log(f"오류: 다음 파일들이 누락되었습니다: {missing_files}")
            return False
            
        self.log("모든 필요한 파일이 존재합니다.")
        return True
        
    def create_crx_info(self):
        """CRX 생성 정보 파일 작성"""
        self.log("CRX 생성 정보 파일 작성...")
        
        info_content = f"""
# 퍼센티 확장 프로그램 CRX 생성 가이드

## 생성 일시
{datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}

## 수정 사항
1. manifest.json 업데이트
   - URL 패턴 수정 (*://*/* → https://*/*, http://*/*)
   - Service worker 경로 수정 (./static/js/background.js → static/js/background.js)
   - Web accessible resources 패턴 정규화
   - update_url 제거 (CRX 전용)

2. background.js 재작성
   - Manifest V3 Service Worker 패턴 적용
   - Chrome Runtime API 안전성 체크 추가
   - 오류 처리 강화
   - 메시지 통신 안정성 개선

## CRX 파일 생성 방법

### 방법 1: Chrome 개발자 도구 사용
1. Chrome에서 chrome://extensions/ 접속
2. 개발자 모드 활성화
3. "확장 프로그램 패키징" 클릭
4. 확장 프로그램 루트 디렉터리 선택: {self.extension_dir}
5. 개인 키 파일 선택 (선택사항)
6. "확장 프로그램 패키징" 버튼 클릭

### 방법 2: 명령줄 도구 사용
```bash
# Chrome 설치 경로에서
chrome --pack-extension="{self.extension_dir}" --pack-extension-key="private-key.pem"
```

### 방법 3: Node.js 도구 사용
```bash
npm install -g chrome-extension-tools
chrome-extension-tools pack {self.extension_dir}
```

## 설치 테스트
1. 생성된 .crx 파일을 Chrome으로 드래그 앤 드롭
2. 또는 chrome://extensions/에서 "압축해제된 확장 프로그램 로드" 사용
3. 퍼센티 웹사이트에서 확장 프로그램 인식 확인

## 문제 해결
- 설치 오류 시: Chrome 개발자 콘솔에서 오류 메시지 확인
- 인식 안됨: 퍼센티 웹사이트에서 F12 → Console 탭에서 오류 확인
- 권한 문제: manifest.json의 host_permissions 확인

## 백업 위치
{self.backup_dir / f'backup_{self.timestamp}'}
"""
        
        info_file = self.extension_dir / 'CRX_BUILD_INFO.md'
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(info_content)
            
        self.log(f"CRX 생성 정보 파일 작성 완료: {info_file}")
        
    def build(self):
        """전체 빌드 프로세스 실행"""
        self.log("=== 퍼센티 확장 프로그램 CRX 빌드 시작 ===")
        
        try:
            # 1. 백업 생성
            backup_dir = self.create_backup()
            
            # 2. 수정된 파일 적용
            if not self.apply_fixes():
                self.log("오류: 수정된 파일 적용 실패")
                return False
                
            # 3. 유효성 검사
            if not self.validate_manifest():
                self.log("오류: manifest.json 유효성 검사 실패")
                return False
                
            # 4. 파일 존재 확인
            if not self.check_files():
                self.log("오류: 필요한 파일 누락")
                return False
                
            # 5. CRX 생성 정보 파일 작성
            self.create_crx_info()
            
            self.log("=== CRX 빌드 준비 완료 ===")
            self.log("")
            self.log("다음 단계:")
            self.log("1. Chrome에서 chrome://extensions/ 접속")
            self.log("2. 개발자 모드 활성화")
            self.log("3. '확장 프로그램 패키징' 또는 '압축해제된 확장 프로그램 로드' 사용")
            self.log(f"4. 디렉터리 선택: {self.extension_dir}")
            self.log("")
            self.log("자세한 내용은 CRX_BUILD_INFO.md 파일을 참조하세요.")
            
            return True
            
        except Exception as e:
            self.log(f"빌드 중 예외 발생: {e}")
            return False

def main():
    """메인 함수"""
    # 현재 디렉터리를 확장 프로그램 디렉터리로 사용
    extension_dir = os.getcwd()
    
    # 명령줄 인수로 디렉터리 지정 가능
    if len(sys.argv) > 1:
        extension_dir = sys.argv[1]
        
    # 확장 프로그램 디렉터리 확인
    if not os.path.exists(os.path.join(extension_dir, 'manifest_fixed.json')):
        print("오류: manifest_fixed.json 파일을 찾을 수 없습니다.")
        print("이 스크립트는 퍼센티 확장 프로그램 디렉터리에서 실행해야 합니다.")
        sys.exit(1)
        
    # CRX 빌더 실행
    builder = CRXBuilder(extension_dir)
    success = builder.build()
    
    if success:
        print("\n✅ CRX 빌드 준비가 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ CRX 빌드 준비 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()