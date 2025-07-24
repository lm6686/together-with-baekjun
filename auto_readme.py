#!/usr/bin/env python3
"""
백준 문제 README 자동 생성 스크립트

사용법:
1. 문제 폴더에서 README.md 파일을 생성하고 [#문제번호] 형태로 작성
2. 이 스크립트를 실행하면 자동으로 문제 정보를 채워줍니다

예시:
- README.md에 "[#2156]" 입력
- python3 auto_readme.py 실행
- 자동으로 문제 정보가 채워진 README.md 생성
"""

import requests
import re
import os
import sys
from pathlib import Path

def get_problem_info_from_solved_ac(problem_id):
    """solved.ac API에서 문제 정보 가져오기"""
    try:
        url = f"https://solved.ac/api/v3/problem/lookup?problemIds={problem_id}"
        response = requests.get(url)
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
        print(f"solved.ac API 요청 실패: {e}")
    return None

def get_problem_info_from_baekjoon(problem_id):
    """백준 사이트에서 문제 정보 가져오기"""
    try:
        url = f"https://www.acmicpc.net/problem/{problem_id}"
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            
            # 문제 설명 추출
            problem_match = re.search(r'<div id="problem_description"[^>]*>(.*?)</div>', content, re.DOTALL)
            problem_desc = ""
            if problem_match:
                desc_html = problem_match.group(1)
                # HTML 태그 제거 및 정리
                desc_text = re.sub(r'<[^>]+>', '', desc_html)
                desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                problem_desc = desc_text
            
            # 입력 조건 추출
            input_match = re.search(r'<div id="problem_input"[^>]*>(.*?)</div>', content, re.DOTALL)
            input_desc = ""
            if input_match:
                input_html = input_match.group(1)
                input_text = re.sub(r'<[^>]+>', '', input_html)
                input_text = re.sub(r'\s+', ' ', input_text).strip()
                input_desc = input_text
            
            # 출력 조건 추출
            output_match = re.search(r'<div id="problem_output"[^>]*>(.*?)</div>', content, re.DOTALL)
            output_desc = ""
            if output_match:
                output_html = output_match.group(1)
                output_text = re.sub(r'<[^>]+>', '', output_html)
                output_text = re.sub(r'\s+', ' ', output_text).strip()
                output_desc = output_text
            
            # 예제 입력 추출
            sample_input_match = re.search(r'<pre class="sampledata" id="sample-input-1"[^>]*>(.*?)</pre>', content, re.DOTALL)
            sample_input = ""
            if sample_input_match:
                sample_input = sample_input_match.group(1).strip()
            
            # 예제 출력 추출
            sample_output_match = re.search(r'<pre class="sampledata" id="sample-output-1"[^>]*>(.*?)</pre>', content, re.DOTALL)
            sample_output = ""
            if sample_output_match:
                sample_output = sample_output_match.group(1).strip()
            
            return {
                'problem_desc': problem_desc,
                'input_desc': input_desc,
                'output_desc': output_desc,
                'sample_input': sample_input,
                'sample_output': sample_output
            }
    except Exception as e:
        print(f"백준 사이트 요청 실패: {e}")
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
        solve_match = re.search(r'## 📊 풀이 정보(.*?)(?=##|$)', existing_content, re.DOTALL)
        if solve_match:
            existing_solve_info = solve_match.group(1).strip()
        
        process_match = re.search(r'## 💭 풀이 과정 \(ETC\)(.*?)(?=##|$)', existing_content, re.DOTALL)
        if process_match:
            existing_process = process_match.group(1).strip()
    
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

## 💭 풀이 과정 (ETC)

{existing_process if existing_process else '> '}
"""
    
    return readme_content

def find_readme_files_with_problem_numbers():
    """현재 디렉토리에서 [#숫자] 패턴이 있는 README.md 파일들 찾기"""
    readme_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'README.md':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # [#숫자] 패턴 찾기
                        match = re.search(r'\[#(\d+)\]', content)
                        if match:
                            problem_id = match.group(1)
                            readme_files.append((file_path, problem_id, content))
                except Exception as e:
                    print(f"파일 읽기 실패 {file_path}: {e}")
    
    return readme_files

def main():
    print("🔍 [#문제번호] 패턴이 있는 README.md 파일들을 찾는 중...")
    
    readme_files = find_readme_files_with_problem_numbers()
    
    if not readme_files:
        print("❌ [#문제번호] 패턴이 있는 README.md 파일을 찾을 수 없습니다.")
        print("💡 사용법: README.md 파일에 [#2156] 같은 형태로 문제 번호를 입력해주세요.")
        return
    
    print(f"📝 {len(readme_files)}개의 README.md 파일을 발견했습니다.")
    
    for file_path, problem_id, existing_content in readme_files:
        print(f"\n🔄 처리 중: {file_path} (문제 #{problem_id})")
        
        # solved.ac에서 문제 정보 가져오기
        print("  📡 solved.ac에서 정보 가져오는 중...")
        problem_info = get_problem_info_from_solved_ac(problem_id)
        
        if not problem_info:
            print(f"  ❌ 문제 #{problem_id} 정보를 가져올 수 없습니다.")
            continue
        
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
        except Exception as e:
            print(f"  ❌ 파일 저장 실패: {e}")
    
    print(f"\n🎉 작업 완료! {len(readme_files)}개의 파일을 처리했습니다.")

if __name__ == "__main__":
    main()
