#!/bin/bash

# 사용법: ./create_readme.sh 사용자명 문제번호
# 예시: ./create_readme.sh junho 1000

if [ $# -ne 2 ]; then
    echo "사용법: ./create_readme.sh 사용자명 문제번호"
    echo "예시: ./create_readme.sh junho 1000"
    exit 1
fi

USER=$1
PROBLEM=$2

# 사용자 폴더 존재 검사
if [ ! -d "$USER" ]; then
    echo "❌ 사용자 폴더가 존재하지 않습니다: $USER"
    echo "기존 사용자 폴더: $(ls -d */ 2>/dev/null | tr -d '/' | tr '\n' ', ' | sed 's/,$//')"
    exit 1
fi

# 문제번호 숫자 검사
if ! [[ "$PROBLEM" =~ ^[0-9]+$ ]]; then
    echo "❌ 문제번호는 숫자여야 합니다: $PROBLEM"
    exit 1
fi

# 사용자 폴더로 이동
cd "$USER"

# 문제 폴더 생성 및 이동
mkdir -p "$PROBLEM"
cd "$PROBLEM"

# README.md 생성
cat > README.md << EOF
# [#$PROBLEM]

---

## 📊 풀이 정보

- **⏱️ 소요 시간**: 0분
- **🔄 시도 횟수**: 0회
- **📅 풀이 날짜**: $(date +%Y-%m-%d)

---

## 💭 풀이 과정

> 여기에 풀이 과정을 작성하세요.

## 🔥 풀이 핵심

> 여기에 풀이 핵심을 작성하세요.

EOF

echo "✅ $USER/$PROBLEM 생성 완료!"
