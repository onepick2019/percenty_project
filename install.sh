#!/bin/bash

# Percenty 자동화 프로젝트 설치 스크립트 (Linux/macOS)

set -e  # 오류 발생 시 스크립트 중단

echo "========================================"
echo "Percenty 자동화 프로젝트 설치 스크립트"
echo "========================================"
echo

echo "[1/5] Python 버전 확인 중..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    python3 --version
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    python --version
else
    echo "오류: Python이 설치되어 있지 않습니다."
    echo "Python 3.9 이상을 설치해주세요."
    exit 1
fi
echo

echo "[2/5] 가상환경 생성 중..."
if [ -d "venv" ]; then
    echo "가상환경이 이미 존재합니다."
else
    $PYTHON_CMD -m venv venv
    echo "가상환경이 성공적으로 생성되었습니다."
fi
echo

echo "[3/5] 가상환경 활성화 중..."
source venv/bin/activate
echo "가상환경이 활성화되었습니다."
echo

echo "[4/5] 의존성 설치 중..."
echo "이 과정은 몇 분이 소요될 수 있습니다..."
pip install --upgrade pip
pip install -r requirements.txt
echo

echo "[5/5] 설치 완료 확인 중..."
echo "주요 라이브러리 설치 상태 확인:"
python -c "import selenium; print('✓ Selenium:', selenium.__version__)" 2>/dev/null || echo "✗ Selenium 설치 실패"
python -c "import pandas; print('✓ Pandas:', pandas.__version__)" 2>/dev/null || echo "✗ Pandas 설치 실패"
python -c "import numpy; print('✓ Numpy:', numpy.__version__)" 2>/dev/null || echo "✗ Numpy 설치 실패"
python -c "import PIL; print('✓ Pillow:', PIL.__version__)" 2>/dev/null || echo "✗ Pillow 설치 실패"
python -c "import easyocr; print('✓ EasyOCR: 설치됨')" 2>/dev/null || echo "✗ EasyOCR 설치 실패"
python -c "import cv2; print('✓ OpenCV:', cv2.__version__)" 2>/dev/null || echo "✗ OpenCV 설치 실패"
echo

echo "========================================"
echo "설치가 완료되었습니다!"
echo "========================================"
echo
echo "다음 단계:"
echo "1. percenty_id.xlsx 파일에 계정 정보를 입력하세요"
echo "2. 다음 명령어로 프로그램을 실행하세요:"
echo "   python percenty_gui_advanced.py"
echo
echo "가상환경을 활성화하려면:"
echo "   source venv/bin/activate"
echo
echo "문제가 발생하면 README.md 파일을 참조하세요."
echo

echo "설치 스크립트가 완료되었습니다. 터미널을 닫지 마세요."
echo "가상환경이 현재 활성화되어 있습니다."