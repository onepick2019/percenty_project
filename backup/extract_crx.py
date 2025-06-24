#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRX 파일을 압축해제하여 Chrome 확장프로그램 설치용 폴더를 생성하는 스크립트

Chrome의 보안 정책으로 인해 CRX 파일을 직접 설치할 수 없으므로,
CRX 파일을 압축해제하여 개발자 모드에서 로드할 수 있는 폴더를 생성합니다.
"""

import os
import zipfile
import shutil
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_crx_file(crx_path, output_dir):
    """
    CRX 파일을 압축해제하여 확장프로그램 폴더를 생성합니다.
    
    Args:
        crx_path (str): CRX 파일 경로
        output_dir (str): 출력 디렉토리 경로
    
    Returns:
        bool: 성공 여부
    """
    try:
        logger.info(f"CRX 파일 압축해제 시작: {crx_path}")
        
        # CRX 파일 존재 확인
        if not os.path.exists(crx_path):
            logger.error(f"CRX 파일을 찾을 수 없습니다: {crx_path}")
            return False
        
        # 출력 디렉토리가 이미 존재하는 경우 삭제
        if os.path.exists(output_dir):
            logger.info(f"기존 출력 디렉토리 삭제: {output_dir}")
            shutil.rmtree(output_dir)
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"출력 디렉토리 생성: {output_dir}")
        
        # CRX 파일을 ZIP 파일로 복사 (CRX는 ZIP 형식과 유사)
        temp_zip_path = crx_path + ".zip"
        shutil.copy2(crx_path, temp_zip_path)
        
        try:
            # ZIP 파일로 압축해제 시도
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            logger.info("ZIP 형식으로 압축해제 성공")
            
        except zipfile.BadZipFile:
            # CRX 헤더 제거 후 다시 시도
            logger.info("CRX 헤더 제거 후 압축해제 시도")
            
            with open(crx_path, 'rb') as crx_file:
                # CRX 헤더 건너뛰기 (일반적으로 처음 몇 바이트)
                crx_data = crx_file.read()
                
                # 'PK' 시그니처 찾기 (ZIP 파일의 시작)
                pk_index = crx_data.find(b'PK')
                if pk_index != -1:
                    zip_data = crx_data[pk_index:]
                    
                    # 임시 ZIP 파일 생성
                    with open(temp_zip_path, 'wb') as temp_zip:
                        temp_zip.write(zip_data)
                    
                    # 압축해제
                    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                        zip_ref.extractall(output_dir)
                    
                    logger.info("CRX 헤더 제거 후 압축해제 성공")
                else:
                    logger.error("ZIP 시그니처를 찾을 수 없습니다")
                    return False
        
        finally:
            # 임시 ZIP 파일 삭제
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
        
        # manifest.json 파일 확인
        manifest_path = os.path.join(output_dir, "manifest.json")
        if os.path.exists(manifest_path):
            logger.info(f"manifest.json 파일 확인됨: {manifest_path}")
            
            # manifest.json 내용 로그 출력
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_content = f.read()
                    logger.info(f"Manifest 내용 (처음 200자): {manifest_content[:200]}...")
            except Exception as e:
                logger.warning(f"Manifest 파일 읽기 실패: {e}")
        else:
            logger.warning("manifest.json 파일을 찾을 수 없습니다")
        
        # 압축해제된 파일 목록 출력
        extracted_files = os.listdir(output_dir)
        logger.info(f"압축해제된 파일 목록: {extracted_files}")
        
        logger.info(f"CRX 파일 압축해제 완료: {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"CRX 파일 압축해제 중 오류 발생: {e}")
        return False

def main():
    """
    메인 함수
    """
    # 파일 경로 설정
    project_root = "c:\\Projects\\percenty_project"
    crx_file_path = os.path.join(project_root, "percenty_extension.crx")
    output_directory = os.path.join(project_root, "percenty_extension")
    
    print("=== CRX 파일 압축해제 도구 ===")
    print(f"CRX 파일: {crx_file_path}")
    print(f"출력 디렉토리: {output_directory}")
    print()
    
    # CRX 파일 압축해제
    if extract_crx_file(crx_file_path, output_directory):
        print("✅ CRX 파일 압축해제 성공!")
        print()
        print("=== Chrome 확장프로그램 설치 방법 ===")
        print("1. Chrome 브라우저에서 chrome://extensions/ 페이지를 엽니다")
        print("2. 우측 상단의 '개발자 모드' 토글을 활성화합니다")
        print("3. '압축해제된 확장 프로그램을 로드합니다' 버튼을 클릭합니다")
        print(f"4. 파일 탐색기에서 다음 폴더를 선택합니다: {output_directory}")
        print("5. '폴더 선택' 버튼을 클릭합니다")
        print("6. 확장프로그램이 설치됩니다")
        print()
        print("설치 후 자동화 스크립트를 다시 실행하세요.")
    else:
        print("❌ CRX 파일 압축해제 실패")
        print("CRX 파일이 존재하는지 확인하고 다시 시도하세요.")

if __name__ == "__main__":
    main()