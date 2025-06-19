#!/bin/bash

# UTF-8 인코딩 설정
export LANG=ko_KR.UTF-8

echo "========================================"
echo "Percenty Project Git 전체 커밋 스크립트"
echo "========================================"
echo

# 현재 Git 상태 확인
echo "[1/5] Git 상태 확인 중..."
git status
echo

# 사용자에게 커밋 메시지 입력 받기
read -p "커밋 메시지를 입력하세요 (예: feat: 새로운 기능 추가): " commit_message

if [ -z "$commit_message" ]; then
    echo "오류: 커밋 메시지가 비어있습니다."
    exit 1
fi

# 모든 변경사항을 스테이징 영역에 추가
echo "[2/5] 모든 변경사항을 스테이징 영역에 추가 중..."
git add .
if [ $? -ne 0 ]; then
    echo "오류: git add 실행 중 문제가 발생했습니다."
    exit 1
fi
echo "완료!"
echo

# 커밋 실행
echo "[3/5] 커밋 실행 중..."
git commit -m "$commit_message"
if [ $? -ne 0 ]; then
    echo "오류: git commit 실행 중 문제가 발생했습니다."
    exit 1
fi
echo "완료!"
echo

# 원격 저장소로 푸시
echo "[4/5] 원격 저장소로 푸시 중..."
git push origin main
if [ $? -ne 0 ]; then
    echo "오류: git push 실행 중 문제가 발생했습니다."
    echo "네트워크 연결이나 인증 정보를 확인해주세요."
    exit 1
fi
echo "완료!"
echo

# 최종 상태 확인
echo "[5/5] 최종 Git 상태 확인..."
git status
echo
echo "========================================"
echo "모든 작업이 성공적으로 완료되었습니다!"
echo "커밋 메시지: $commit_message"
echo "========================================"
echo
read -p "계속하려면 Enter 키를 누르세요..."