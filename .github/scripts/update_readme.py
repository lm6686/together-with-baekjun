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

def calculate_missing_weekdays(problems):
    """첫 번째 문제부터 현재까지 빼먹은 평일 계산"""
    if not problems:
        return 0, 0, []
    
    from datetime import date, timedelta
    
    # 문제 날짜들을 date 객체로 변환
    problem_dates = set()
    for problem in problems:
        try:
            problem_date = datetime.strptime(problem['date'], '%Y-%m-%d').date()
            problem_dates.add(problem_date)
        except:
            continue
    
    if not problem_dates:
        return 0, 0, []
    
    # 첫 번째 문제 날짜부터 오늘까지 (오늘 한 건 성공에 포함!)
    start_date = min(problem_dates)
    end_date = date.today()
    
    # 시작일이 오늘 이후면 아직 계산할 게 없음
    if start_date > date.today():
        return 0, 0, []
    
    # 평일 날짜들 생성 (월~금)
    weekdays = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 0=월요일, 4=금요일
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    
    # 빼먹은 평일들 (오늘은 아직 할 수 있으니 제외)
    today = date.today()
    missing_weekdays = []
    for day in weekdays:
        if day not in problem_dates and day != today:  # 오늘은 빼먹은 날에서 제외
            missing_weekdays.append(day)
    
    return len(weekdays), len(missing_weekdays), missing_weekdays

def update_user_readme(username, user_data):
    """개별 사용자의 README 업데이트"""
    readme_path = Path(username) / 'README.md'
    
    # 빼먹은 평일 계산
    total_weekdays, missing_count, missing_dates = calculate_missing_weekdays(user_data['problems'])
    
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
    
    # 통계 섹션 추가
    if user_data['problems']:
        first_date = user_data['problems'][0]['date']
        
        # 실제로 문제를 푼 평일 계산
        problem_dates = set()
        for problem in user_data['problems']:
            try:
                problem_date = datetime.strptime(problem['date'], '%Y-%m-%d').date()
                if problem_date.weekday() < 5:  # 평일만
                    problem_dates.add(problem_date)
            except:
                continue
        
        actual_success_days = len(problem_dates)  # 실제로 문제를 푼 평일 수
        total_evaluated_days = actual_success_days + missing_count  # 성공 + 실패 = 평가된 총 일수
        success_rate = ((actual_success_days) / total_evaluated_days * 100) if total_evaluated_days > 0 else 0
        
        # 계산된 통계를 user_data에 저장 (전체 README에서 재사용)
        user_data['stats'] = {
            'first_date': first_date,
            'total_weekdays': total_weekdays,
            'success_days': actual_success_days,
            'failure_days': missing_count,
            'success_rate': success_rate
        }
        
        content += f"""
---

## 📊 스터디 통계

- **📅 시작일**: {first_date}
- **📈 총 풀이 문제**: {user_data['total_count']}개
- **⏱️ 도전 기간**: {total_weekdays}일째 도전 중!
- **✅ 성공한 날**: {actual_success_days}일
- **❌ 실패한 날**: {missing_count}일
- **🎯 출석률**: {success_rate:.1f}%"""

        if missing_dates and len(missing_dates) <= 10:  # 너무 많으면 표시하지 않음
            missing_str = ", ".join([d.strftime('%m-%d') for d in missing_dates[-5:]])  # 최근 5개만
            if len(missing_dates) > 5:
                missing_str += f" (외 {len(missing_dates)-5}일)"
            content += f"\n- **📝 최근 빼먹은 날**: {missing_str}"
        
        content += "\n"
    else:
        # 문제를 풀지 않은 경우 기본값 저장
        user_data['stats'] = {
            'first_date': None,
            'total_weekdays': 0,
            'success_days': 0,
            'failure_days': 0,
            'success_rate': 0
        }
        
        content += f"""
---

**📊 아직 문제를 풀지 않았습니다. 첫 문제를 풀어보세요!**
"""
    
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
    
    # 전체 스터디 통계 계산 (개별 사용자 통계 사용)
    if users_data:
        # 모든 사용자의 첫 문제 날짜 중 가장 빠른 날
        all_first_dates = []
        total_problems_all = 0
        total_success_days_all = 0
        total_missing_days_all = 0
        
        for username, data in users_data.items():
            if data['problems'] and 'stats' in data:
                first_date = data['stats']['first_date']
                if first_date:
                    all_first_dates.append(datetime.strptime(first_date, '%Y-%m-%d').date())
                
                total_problems_all += data['total_count']
                total_success_days_all += data['stats']['success_days']
                total_missing_days_all += data['stats']['failure_days']
        
        if all_first_dates:
            study_start_date = min(all_first_dates).strftime('%Y-%m-%d')
            
            # 전체 도전 기간 계산
            from datetime import date
            start_date = min(all_first_dates)
            end_date = date.today()
            
            total_weekdays_all = 0
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() < 5:  # 평일만
                    total_weekdays_all += 1
                current_date += timedelta(days=1)
        else:
            study_start_date = "아직 시작 안함"
            total_weekdays_all = 0
    
    # 참여자 테이블 생성 (개인별 상세 통계 포함)
    table_content = """| 이름 | 풀이 문제 수 | 성공한 날 | 실패한 날 | 출석률 | 최근 활동 |
|------|-------------|----------|----------|--------|-----------|
"""
    
    for username, data in users_data.items():
        last_activity = data['last_update'] if data['last_update'] else "-"
        
        if data['problems'] and 'stats' in data:
            # 저장된 통계 사용
            stats = data['stats']
            success_days = stats['success_days']
            failure_days = stats['failure_days']
            attendance_rate = stats['success_rate']
            
            table_content += f"| {username} | {data['total_count']}문제 | {success_days}일 | {failure_days}일 | {attendance_rate:.1f}% | {last_activity} |\n"
        else:
            table_content += f"| {username} | 0문제 | 0일 | 0일 | - | {last_activity} |\n"
    
    # 기존 테이블 교체 (정규식으로 찾아서 교체)
    pattern = r'\| 이름 \|.*?\|.*?\n(?:\|.*?\n)*'
    if re.search(pattern, content, re.MULTILINE):
        content = re.sub(pattern, table_content, content, flags=re.MULTILINE)
    else:
        # 테이블이 없으면 참여자 섹션에 추가
        participants_pattern = r'## 👥 참여자.*?(?=\n##|\n---|\Z)'
        if re.search(participants_pattern, content, re.DOTALL):
            replacement = f"## 👥 참여자\n\n{table_content}\n"
            content = re.sub(participants_pattern, replacement, content, flags=re.DOTALL)
    
    # 진행 현황 업데이트
    today = datetime.now().strftime('%Y년 %m월 %d일')
    
    # 기존 진행 현황 부분을 전체 통계로 교체
    if users_data and all_first_dates:
        stats_content = f"""## 📊 전체 스터디 통계

- **📅 스터디 시작일**: {study_start_date}
- **📈 총 풀이 문제**: {total_problems_all}개
- **⏱️ 도전 기간**: {total_weekdays_all}일째 도전 중!
- **👥 참여자 수**: {len(users_data)}명

---

## 📈 진행 현황

- **현재 진행**: 총 {total_problems_all}문제 완료 ({today} 기준)"""
    else:
        stats_content = f"""## 📊 전체 스터디 통계

- **📊 아직 문제를 푼 참여자가 없습니다.**

---

## 📈 진행 현황

- **현재 진행**: 스터디 준비 중 ({today} 기준)"""
    
    # 진행 현황 섹션 교체
    progress_pattern = r'## 📊 진행 현황.*?(?=\n##|\n---|\Z)'
    if re.search(progress_pattern, content, re.DOTALL):
        content = re.sub(progress_pattern, stats_content, content, flags=re.DOTALL)
    else:
        # 진행 현황이 없으면 참여자 섹션 뒤에 추가
        participants_end_pattern = r'(## 👥 참여자.*?\n(?:\|.*?\n)*)'
        if re.search(participants_end_pattern, content, re.DOTALL):
            content = re.sub(participants_end_pattern, f'\\1\n{stats_content}\n', content, flags=re.DOTALL)
    
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
