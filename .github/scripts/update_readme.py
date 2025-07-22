#!/usr/bin/env python3
import re
from datetime import datetime, timedelta
from pathlib import Path

def get_problem_info_from_readme(readme_path):
    """개별 문제 README에서 정보 추출"""
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 문제 번호와 제목 추출
        title_match = re.search(r'\[#(\d+)\.\s*(.+?)\]', content)
        if title_match:
            problem_num = title_match.group(1)
            problem_title = title_match.group(2)
        else:
            return None
        
        # 티어 이미지에서 난이도 추출
        tier_match = re.search(r'tier_small/(\d+)\.svg', content)
        if tier_match:
            tier_num = int(tier_match.group(1))
            # 티어 번호를 난이도로 변환
            tier_names = [
                'Unknown',          # 0
                'Bronze V',         # 1
                'Bronze IV',        # 2
                'Bronze III',       # 3
                'Bronze II',        # 4
                'Bronze I',         # 5
                'Silver V',         # 6
                'Silver IV',        # 7
                'Silver III',       # 8
                'Silver II',        # 9
                'Silver I',         # 10
                'Gold V',           # 11
                'Gold IV',          # 12
                'Gold III',         # 13
                'Gold II',          # 14
                'Gold I',           # 15
                'Platinum V',       # 16
                'Platinum IV',      # 17
                'Platinum III',     # 18
                'Platinum II',      # 19
                'Platinum I',       # 20
                'Diamond V',        # 21
                'Diamond IV',       # 22
                'Diamond III',      # 23
                'Diamond II',       # 24
                'Diamond I',        # 25
                'Ruby V',           # 26
                'Ruby IV',          # 27
                'Ruby III',         # 28
                'Ruby II',          # 29
                'Ruby I'            # 30
            ]
            
            if 1 <= tier_num <= 30:
                difficulty = tier_names[tier_num]
            else:
                difficulty = "Unknown"
        else:
            difficulty = "Unknown"
        
        return {
            'number': problem_num,
            'title': problem_title,
            'difficulty': difficulty
        }
    except:
        return None

def scan_user_folders():
    """사용자 폴더들을 스캔하여 문제 정보 수집"""
    base_path = Path('.')
    users_data = {}
    
    for user_folder in base_path.iterdir():
        if user_folder.is_dir() and not user_folder.name.startswith('.') and user_folder.name != 'README.md':
            username = user_folder.name
            users_data[username] = {
                'problems': [],
                'total_count': 0,
                'last_update': None
            }
            
            # 각 문제 폴더 스캔
            for problem_folder in user_folder.iterdir():
                if problem_folder.is_dir() and problem_folder.name.isdigit():
                    problem_readme = problem_folder / 'README.md'
                    if problem_readme.exists():
                        problem_info = get_problem_info_from_readme(problem_readme)
                        if problem_info:
                            # Git에서 첫 번째 커밋 시간 가져오기 (파일 생성 시점)
                            try:
                                import subprocess
                                result = subprocess.run(
                                    ['git', 'log', '--follow', '--format=%ai', '--reverse', str(problem_readme)],
                                    capture_output=True, text=True
                                )
                                if result.returncode == 0 and result.stdout.strip():
                                    # 첫 번째 라인이 가장 오래된 커밋
                                    first_commit = result.stdout.strip().split('\n')[0]
                                    commit_datetime_str = first_commit
                                    # 커밋 시간을 파싱
                                    commit_datetime = datetime.fromisoformat(commit_datetime_str.replace(' +', '+'))
                                    
                                    # 오전 4시 이전이면 전날로 처리
                                    if commit_datetime.hour < 4:
                                        commit_date = (commit_datetime.date() - timedelta(days=1)).strftime('%Y-%m-%d')
                                    else:
                                        commit_date = commit_datetime.date().strftime('%Y-%m-%d')
                                    
                                    problem_info['date'] = commit_date
                                else:
                                    problem_info['date'] = datetime.now().strftime('%Y-%m-%d')
                            except:
                                problem_info['date'] = datetime.now().strftime('%Y-%m-%d')
                            
                            users_data[username]['problems'].append(problem_info)
            
            # 문제들을 날짜순으로 정렬
            users_data[username]['problems'].sort(key=lambda x: x['date'])
            users_data[username]['total_count'] = len(users_data[username]['problems'])
            
            if users_data[username]['problems']:
                users_data[username]['last_update'] = users_data[username]['problems'][-1]['date']
    
    return users_data

def update_user_readme(username, user_data):
    """개별 사용자의 README 업데이트"""
    readme_path = Path(username) / 'README.md'
    
    # README 내용 생성
    content = f"""# 📚 {username}의 백준 스터디 기록

> 🎯 **매일 꾸준히, 함께 성장하기!**

---

## 📅 풀이 기록

"""
    
    # 문제 목록 추가
    for problem in user_data['problems']:
        difficulty_display = problem.get('difficulty', 'Unknown')
        
        content += f"- {problem['date']}: {problem['number']}번 ({problem['title']})"
        if difficulty_display != "Unknown":
            content += f" {difficulty_display}"
        content += "\n"
    
    content += f"""
---

**총 풀이 문제: {user_data['total_count']}개**
"""
    
    if user_data['last_update']:
        content += f"**마지막 업데이트: {user_data['last_update']}**\n"
    
    # 파일 쓰기
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_main_readme(users_data):
    """메인 README의 참여자 테이블 업데이트"""
    readme_path = Path('README.md')
    
    if not readme_path.exists():
        return
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 참여자 테이블 생성
    table_content = """| 이름 | 백준 ID | 풀이 문제 수 | 최근 활동 |
|------|---------|-------------|-----------|
"""
    
    for username, data in users_data.items():
        last_activity = data['last_update'] if data['last_update'] else "-"
        status = "🟢 활발" if data['total_count'] > 0 else "⚪ 준비중"
        
        table_content += f"| {username} | - | {data['total_count']}문제 | {last_activity} |\n"
    
    # 기존 테이블 교체 (정규식으로 찾아서 교체)
    pattern = r'\| 이름 \| 백준 ID \| 진행률 \|.*?\n(?:\|.*?\n)*'
    if re.search(pattern, content, re.MULTILINE):
        content = re.sub(pattern, table_content, content, flags=re.MULTILINE)
    else:
        # 테이블이 없으면 참여자 섹션에 추가
        participants_pattern = r'## 👥 참여자.*?(?=\n##|\n---|\Z)'
        if re.search(participants_pattern, content, re.DOTALL):
            replacement = f"## 👥 참여자\n\n{table_content}\n"
            content = re.sub(participants_pattern, replacement, content, flags=re.DOTALL)
    
    # 진행 현황 업데이트
    total_problems = sum(data['total_count'] for data in users_data.values())
    today = datetime.now().strftime('%Y년 %m월 %d일')
    
    # 현재 진행 부분 업데이트
    progress_pattern = r'📈 \*\*현재 진행\*\*:.*'
    new_progress = f"📈 **현재 진행**: 총 {total_problems}문제 완료 ({today} 기준)"
    content = re.sub(progress_pattern, new_progress, content)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("🔍 폴더 구조 스캔 중...")
    users_data = scan_user_folders()
    
    print(f"📊 발견된 사용자: {list(users_data.keys())}")
    
    # 각 사용자의 README 업데이트
    for username, user_data in users_data.items():
        print(f"📝 {username}의 README 업데이트 중...")
        update_user_readme(username, user_data)
    
    # 메인 README 업데이트
    print("📋 메인 README 업데이트 중...")
    update_main_readme(users_data)
    
    print("✅ README 업데이트 완료!")

if __name__ == "__main__":
    main()
