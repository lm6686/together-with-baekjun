#!/usr/bin/env python3
"""
GitHub Actions용 백준 문제 README 자동 완성 스크립트
푸시할 때마다 [#문제번호] 형태의 README 파일을 찾아서 자동으로 문제 정보를 채워줍니다.
"""

import requests
import re
import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import time

def get_problem_info_from_solved_ac(problem_id):
    """solved.ac API에서 문제 정보 가져오기"""
    try:
        url = f"https://solved.ac/api/v3/problem/lookup?problemIds={problem_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                problem = data[0]
                return {
                    'id': problem['problemId'],
                    'title': problem['titleKo'],
                    'level': problem['level'],
                    'tags': [tag['displayNames'][0]['name'] for tag in problem['tags']]
                }
    except Exception as e:
        print(f"❌ solved.ac API 요청 실패 (문제 {problem_id}): {e}")
    return None

def get_problem_info_from_baekjoon(problem_id):
    """백준 사이트에서 문제 정보 가져오기"""
    try:
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 문제 설명 추출
            problem_desc = ""
            problem_div = soup.find('div', {'id': 'problem_description'})
            if problem_div:
                problem_desc = problem_div.get_text(strip=True)
            
            # 입력 조건 추출
            input_desc = ""
            input_div = soup.find('div', {'id': 'problem_input'})
            if input_div:
                input_desc = input_div.get_text(strip=True)
            
            # 출력 조건 추출
            output_desc = ""
            output_div = soup.find('div', {'id': 'problem_output'})
            if output_div:
                output_desc = output_div.get_text(strip=True)
            
            # 예제 입력 추출
            sample_input = ""
            sample_input_pre = soup.find('pre', {'id': 'sample-input-1'})
            if sample_input_pre:
                sample_input = sample_input_pre.get_text(strip=True)
            
            # 예제 출력 추출
            sample_output = ""
            sample_output_pre = soup.find('pre', {'id': 'sample-output-1'})
            if sample_output_pre:
                sample_output = sample_output_pre.get_text(strip=True)
            
            return {
                'problem_desc': problem_desc,
                'input_desc': input_desc,
                'output_desc': output_desc,
                'sample_input': sample_input,
                'sample_output': sample_output
            }
    except Exception as e:
        print(f"❌ 백준 사이트 요청 실패 (문제 {problem_id}): {e}")
    return None

def generate_readme_content(problem_info, baekjoon_info, existing_content=""):
    """README 내용 생성"""
    problem_id = problem_info['id']
    title = problem_info['title']
    level = problem_info['level']
    tags = ', '.join(problem_info['tags'])
    
    # 기존 풀이 정보 추출
    existing_solve_info = ""
    existing_process = ""
    
    if existing_content:
        solve_match = re.search(r'## 📊 풀이 정보(.*?)(?=##|---|\Z)', existing_content, re.DOTALL)
        if solve_match:
            existing_solve_info = solve_match.group(1).strip()
        
        process_match = re.search(r'## 💭 풀이 과정(.*?)(?=##|---|\Z)', existing_content, re.DOTALL)
        if process_match:
            existing_process = process_match.group(1).strip()
        
        # 풀이 핵심도 추가로 추출
        core_match = re.search(r'## 🔥 풀이 핵심(.*?)(?=##|---|\Z)', existing_content, re.DOTALL)
        existing_core = ""
        if core_match:
            existing_core = core_match.group(1).strip()
    
    readme_content = f"""[#{problem_id}. {title}](https://www.acmicpc.net/problem/{problem_id})
<img src="https://static.solved.ac/tier_small/{level}.svg" width="16" height="16">

---

## 📍 문제 정보

- **문제 번호**: {problem_id}
- **🏷️ 문제 유형**: {tags}

---

## 문제

> {baekjoon_info['problem_desc']}

## 입력

> {baekjoon_info['input_desc']}

## 출력

> {baekjoon_info['output_desc']}

## 예제 입력

> {baekjoon_info['sample_input']}

## 예제 출력

> {baekjoon_info['sample_output']}

---

## 📊 풀이 정보

{existing_solve_info if existing_solve_info else '''- **⏱️ 소요 시간**: 
- **🔄 시도 횟수**: 
- **📅 풀이 날짜**: '''}

---

## 💭 풀이 과정

{existing_process if existing_process else '> 여기에 풀이 과정을 작성하세요.'}

## 🔥 풀이 핵심

{existing_core if existing_core else '> 여기에 풀이 핵심을 작성하세요.'}
"""
    
    return readme_content

def find_readme_files_with_problem_numbers():
    """현재 디렉토리에서 [#숫자] 패턴이 있는 README.md 파일들 찾기"""
    readme_files = []
    for root, dirs, files in os.walk('.'):
        # .git, .github, .venv 폴더 제외
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file == 'README.md':
                file_path = os.path.join(root, file)
                print(f"📂 검사 중: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # [#숫자] 패턴 찾기 (단독으로 있는 경우만)
                        lines = content.split('\n')
                        first_few_lines = '\n'.join(lines[:5])  # 처음 5줄만 확인
                        print(f"   처음 5줄:\n{first_few_lines}")
                        match = re.search(r'^#\s*\[#(\d+)\]$', first_few_lines, re.MULTILINE)
                        print(f"   정규식 매치 결과: {match}")
                        if match:
                            problem_id = match.group(1)
                            print(f"🔍 [#문제번호] 패턴 발견: {file_path} (문제 #{problem_id})")
                            # 이미 완성된 README인지 확인 (문제 정보가 있는지)
                            has_problem_info = re.search(r'## 📍 문제 정보', content)
                            print(f"   📍 문제 정보 섹션 존재: {'Yes' if has_problem_info else 'No'}")
                            if not has_problem_info:
                                readme_files.append((file_path, problem_id, content))
                                print(f"✅ 처리 대상에 추가: {file_path} (문제 #{problem_id})")
                except Exception as e:
                    print(f"⚠️ 파일 읽기 실패 {file_path}: {e}")
    
    return readme_files

def main():
    print("🤖 GitHub Actions - 백준 문제 README 자동 완성 시작!")
    print("=" * 50)
    
    readme_files = find_readme_files_with_problem_numbers()
    
    if not readme_files:
        print("✅ 완성되지 않은 [#문제번호] 패턴의 README.md 파일이 없습니다.")
        return
    
    print(f"📝 {len(readme_files)}개의 README.md 파일을 처리합니다.")
    
    success_count = 0
    
    for file_path, problem_id, existing_content in readme_files:
        print(f"\n🔄 처리 중: {file_path} (문제 #{problem_id})")
        
        # solved.ac에서 문제 정보 가져오기
        print("  📡 solved.ac에서 정보 가져오는 중...")
        problem_info = get_problem_info_from_solved_ac(problem_id)
        
        if not problem_info:
            print(f"  ❌ 문제 #{problem_id} 정보를 가져올 수 없습니다.")
            continue
        
        # 요청 사이에 딜레이 추가 (너무 빠른 요청 방지)
        time.sleep(1)
        
        # 백준에서 문제 내용 가져오기
        print("  📡 백준에서 문제 내용 가져오는 중...")
        baekjoon_info = get_problem_info_from_baekjoon(problem_id)
        
        if not baekjoon_info:
            print(f"  ❌ 문제 #{problem_id} 내용을 가져올 수 없습니다.")
            continue
        
        # README 내용 생성
        print("  📝 README 내용 생성 중...")
        readme_content = generate_readme_content(problem_info, baekjoon_info, existing_content)
        
        # 파일 저장
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"  ✅ {file_path} 업데이트 완료!")
            success_count += 1
        except Exception as e:
            print(f"  ❌ 파일 저장 실패: {e}")
        
        # 요청 사이에 딜레이 추가
        time.sleep(2)
    
    print("=" * 50)
    print(f"🎉 작업 완료! {success_count}/{len(readme_files)}개의 파일을 성공적으로 처리했습니다.")
    
    if success_count > 0:
        print("📝 변경된 파일들이 자동으로 커밋됩니다.")

if __name__ == "__main__":
    main()
