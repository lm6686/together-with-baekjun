#!/bin/bash

# 백준 문제 README 템플릿 생성 스크립트
# 사용법: ./create_readme.sh 문제번호

if [ $# -eq 0 ]; then
    echo "❌ 문제 번호를 입력해주세요!"
    echo "사용법: ./create_readme.sh 1000"
    exit 1
fi

PROBLEM_NUM=$1

# 현재 사용자 폴더 확인
CURRENT_USER=$(basename $(pwd))

# 사용자 폴더가 아닌 경우 안내
if [ ! -d "../$CURRENT_USER" ] && [ "$CURRENT_USER" != "hyosang" ] && [ "$CURRENT_USER" != "junho" ] && [ "$CURRENT_USER" != "jungyu" ] && [ "$CURRENT_USER" != "nayeon" ] && [ "$CURRENT_USER" != "yeyoung" ]; then
    echo "⚠️  사용자 폴더(hyosang, junho, jungyu, nayeon, yeyoung) 안에서 실행해주세요!"
    echo "현재 위치: $(pwd)"
    exit 1
fi

# 숫자인지 확인
if ! [[ "$PROBLEM_NUM" =~ ^[0-9]+$ ]]; then
    echo "❌ 오류: 문제번호는 숫자여야 합니다."
    exit 1
fi

# 문제 폴더 생성
if [ -d "$PROBLEM_NUM" ]; then
    echo "⚠️  문제 폴더 '$PROBLEM_NUM'가 이미 존재합니다."
    read -p "덮어쓰시겠습니까? (y/N): " answer
    if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
        echo "취소되었습니다."
        exit 1
    fi
fi

mkdir -p $PROBLEM_NUM
cd $PROBLEM_NUM

CURRENT_DATE=$(date +%Y-%m-%d)

# README.md 템플릿 생성

cat > README.md << EOF
# [#$PROBLEM_NUM]

---

## 📊 풀이 정보

- **⏱️ 소요 시간**: 0분
- **🔄 시도 횟수**: 0회
- **📅 풀이 날짜**: $CURRENT_DATE

---

## 💭 풀이 과정

> 여기에 풀이 과정을 작성하세요. 문제를 어떻게 접근했는지, 어떤 알고리즘을 사용했는지 등을 상세히 설명합니다.

## 🔥 풀이 핵심:

> 여기에 풀이 핵심을 작성하세요. 문제를 해결하기 위한 핵심 아이디어나 알고리즘을 간단히 정리합니다.

EOF

echo "✅ 문제 $PROBLEM_NUM 폴더와 README.md 템플릿이 생성되었습니다!"
echo ""
echo "📋 다음 단계:"
echo "1. 솔루션 파일을 작성하세요 (solution.py, main.cpp 등)"
echo "2. README.md의 풀이 정보를 채워주세요"  
echo "3. git add . && git commit -m \"solve: 백준 ${PROBLEM_NUM}번\" && git push"
echo "4. 🤖 GitHub Actions가 자동으로 문제 정보를 추가합니다!"
echo ""
echo "📂 생성된 파일 위치: $(pwd)/README.md"
