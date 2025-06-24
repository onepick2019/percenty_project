#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
퍼센티 확장 프로그램용 새로운 키 생성 및 CRX 빌드 스크립트

이 스크립트는:
1. OpenSSL을 사용하여 새로운 RSA 키 쌍 생성
2. 공개키를 Base64로 인코딩하여 manifest.json에 추가
3. 동일한 ID로 CRX 파일 생성
4. 퍼센티 웹사이트에서 인식 가능한 확장 프로그램 생성
"""

import os
import json
import base64
import subprocess
import shutil
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_rsa_key_pair():
    """RSA 키 쌍 생성"""
    print("🔑 RSA 키 쌍 생성 중...")
    
    # RSA 키 쌍 생성 (2048 비트)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # 공개키 추출
    public_key = private_key.public_key()
    
    return private_key, public_key

def save_private_key(private_key, filename="extension.pem"):
    """개인키를 PEM 파일로 저장"""
    print(f"💾 개인키 저장 중: {filename}")
    
    pem_data = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open(filename, 'wb') as f:
        f.write(pem_data)
    
    return filename

def public_key_to_base64(public_key):
    """공개키를 Base64로 인코딩"""
    print("🔐 공개키를 Base64로 인코딩 중...")
    
    # DER 형식으로 공개키 직렬화
    der_data = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Base64 인코딩
    base64_key = base64.b64encode(der_data).decode('utf-8')
    
    return base64_key

def update_manifest_with_key(manifest_path, base64_key):
    """manifest.json에 key 필드 추가"""
    print(f"📝 manifest.json 업데이트 중: {manifest_path}")
    
    # 기존 manifest.json 읽기
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # key 필드 추가
    manifest['key'] = base64_key
    
    # 업데이트된 manifest.json 저장
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✅ manifest.json에 key 필드 추가 완료")
    return manifest

def calculate_extension_id(base64_key):
    """Base64 키로부터 확장 프로그램 ID 계산"""
    import hashlib
    
    # Base64 디코딩
    key_bytes = base64.b64decode(base64_key)
    
    # SHA256 해시 계산
    sha256_hash = hashlib.sha256(key_bytes).hexdigest()
    
    # 처음 32자를 16진수에서 알파벳으로 변환 (a-p)
    extension_id = ''
    for i in range(0, 32, 2):
        hex_pair = sha256_hash[i:i+2]
        decimal_value = int(hex_pair, 16)
        letter = chr(ord('a') + (decimal_value % 16))
        extension_id += letter
    
    return extension_id

def build_crx_with_key(manifest_dir, pem_file, output_crx):
    """키 파일을 사용하여 CRX 빌드"""
    print(f"🏗️ CRX 파일 빌드 중: {output_crx}")
    
    # Chrome 경로 찾기
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME'))
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        print("❌ Chrome 실행 파일을 찾을 수 없습니다.")
        return False
    
    # CRX 빌드 명령어
    cmd = [
        chrome_exe,
        "--pack-extension=" + os.path.abspath(manifest_dir),
        "--pack-extension-key=" + os.path.abspath(pem_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # 생성된 CRX 파일 확인
        generated_crx = manifest_dir + ".crx"
        if os.path.exists(generated_crx):
            if output_crx != generated_crx:
                shutil.move(generated_crx, output_crx)
            print(f"✅ CRX 파일 생성 완료: {output_crx}")
            return True
        else:
            print(f"❌ CRX 파일 생성 실패")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CRX 빌드 시간 초과")
        return False
    except Exception as e:
        print(f"❌ CRX 빌드 중 오류: {e}")
        return False

def main():
    print("="*60)
    print("퍼센티 확장 프로그램 키 생성 및 CRX 빌드")
    print("="*60)
    
    # 현재 디렉토리 확인
    current_dir = os.getcwd()
    manifest_path = os.path.join(current_dir, "manifest.json")
    
    if not os.path.exists(manifest_path):
        print(f"❌ manifest.json을 찾을 수 없습니다: {manifest_path}")
        return
    
    try:
        # 1. RSA 키 쌍 생성
        private_key, public_key = generate_rsa_key_pair()
        
        # 2. 개인키를 PEM 파일로 저장
        pem_file = save_private_key(private_key, "percenty_extension.pem")
        
        # 3. 공개키를 Base64로 인코딩
        base64_key = public_key_to_base64(public_key)
        
        # 4. 확장 프로그램 ID 계산
        extension_id = calculate_extension_id(base64_key)
        print(f"🆔 생성된 확장 프로그램 ID: {extension_id}")
        
        # 5. manifest.json에 key 필드 추가
        manifest = update_manifest_with_key(manifest_path, base64_key)
        
        # 6. CRX 파일 빌드
        output_crx = "percenty_extension_with_key.crx"
        success = build_crx_with_key(current_dir, pem_file, output_crx)
        
        if success:
            print("\n" + "="*60)
            print("✅ 성공적으로 완료되었습니다!")
            print("="*60)
            print(f"📁 생성된 파일들:")
            print(f"   - {pem_file} (개인키)")
            print(f"   - {output_crx} (CRX 파일)")
            print(f"   - manifest.json (key 필드 추가됨)")
            print(f"\n🆔 확장 프로그램 ID: {extension_id}")
            print(f"\n📋 설치 방법:")
            print(f"   1. Chrome에서 chrome://extensions/ 열기")
            print(f"   2. 개발자 모드 활성화")
            print(f"   3. '{output_crx}' 파일을 드래그 앤 드롭")
            print(f"\n🎯 이제 퍼센티 웹사이트에서 이 확장 프로그램을 인식할 수 있습니다.")
        else:
            print("❌ CRX 빌드에 실패했습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()