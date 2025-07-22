#!/usr/bin/env python3
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 한국 시간대 설정 (GitHub Actions 호환성)
try:
    from zoneinfo import ZoneInfo
    KST = ZoneInfo('Asia/Seoul')
except ImportError:
    KST = None
except:
    KST = None

def get_korea_now():
    """GitHub Actions 환경 호환 한국 시간 가져오기"""
    utc_now = datetime.utcnow()
    
    if KST is None:
        # 직접 UTC+9 계산
        korea_now = utc_now + timedelta(hours=9)
    else:
        # 한국 시간대로 변환
        korea_now = utc_now.replace(tzinfo=timezone.utc).astimezone(KST).replace(tzinfo=None)
    
    return korea_now

def get_korea_today():
    """GitHub Actions 환경 호환 한국 오늘 날짜 가져오기"""
    korea_now = get_korea_now()
    today = korea_now.date()
    return today

def get_korea_today():
    """한국 시간 기준 오늘 날짜 반환"""
    return get_korea_now().date()

def convert_to_korea_time(dt):
    """datetime을 한국 시간으로 변환"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    korea_dt = dt.astimezone(timezone(timedelta(hours=9)))
    return korea_dt.replace(tzinfo=None)

def get_problem_info(problem_dir):
    """문제 디렉토리에서 문제 정보를 추출"""
    readme_path = problem_dir / "README.md"
    if not readme_path.exists():
        return None
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None
    
    # 제목에서 문제 번호와 이름 추출
    title_match = re.search(r'#(\d+)\.\s*(.+?)\]', content)
    if title_match:
        problem_num = title_match.group(1)
        problem_title = title_match.group(2)
    else:
        return None
    
    # 티어 이미지에서 난이도 추출
    tier_match = re.search(r'tier_small/(\d+)\.svg', content)
    if tier_match:
        tier_num = int(tier_match.group(1))
        tier_names = [
            'Unknown', 'Bronze V', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I',
            'Silver V', 'Silver IV', 'Silver III', 'Silver II', 'Silver I',
            'Gold V', 'Gold IV', 'Gold III', 'Gold II', 'Gold I',
            'Platinum V', 'Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I',
            'Diamond V', 'Diamond IV', 'Diamond III', 'Diamond II', 'Diamond I',
            'Ruby V', 'Ruby IV', 'Ruby III', 'Ruby II', 'Ruby I'
        ]
        difficulty = tier_names[tier_num] if tier_num < len(tier_names) else 'Unknown'
    else:
        difficulty = 'Unknown'
    
    return {
        'number': problem_num,
        'title': problem_title,
        'difficulty': difficulty,
        'tier_num': tier_num if tier_match else 0
    }

def scan_users():
    """사용자 디렉토리를 스캔하여 문제 정보를 수집"""
    users_data = {}
    workspace_path = Path('.')
    
    for user_dir in workspace_path.iterdir():
        if not user_dir.is_dir() or user_dir.name.startswith('.') or user_dir.name in ['README.md', 'docs']:
            continue
        
        username = user_dir.name
        users_data[username] = {'problems': []}
        
        for problem_dir in user_dir.iterdir():
            if not problem_dir.is_dir() or not problem_dir.name.isdigit():
                continue
            
            problem_info = get_problem_info(problem_dir)
            if problem_info:
                # Git 커밋 시간 가져오기
                import subprocess
                try:
                    result = subprocess.run(
                        ['git', 'log', '--follow', '--format=%ai', '--', str(problem_dir)],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        first_commit = result.stdout.strip().split('\n')[0]
                        commit_datetime_str = first_commit
                        
                        try:
                            # Git 커밋 시간 형식: '2025-07-22 00:45:46+0900'을 파싱
                            if '+' in commit_datetime_str and commit_datetime_str.count(':') == 2:
                                datetime_part, tz_part = commit_datetime_str.rsplit('+', 1)
                                if len(tz_part) == 4:  # +0900 형식
                                    tz_formatted = f"+{tz_part[:2]}:{tz_part[2:]}"
                                    commit_datetime_str_formatted = f"{datetime_part}{tz_formatted}"
                                else:
                                    commit_datetime_str_formatted = commit_datetime_str
                            else:
                                commit_datetime_str_formatted = commit_datetime_str
                            
                            commit_datetime = datetime.fromisoformat(commit_datetime_str_formatted)
                            
                            # 한국 시간으로 변환
                            if KST is None:
                                commit_datetime_kst = commit_datetime.replace(tzinfo=None) + timedelta(hours=9)
                            else:
                                commit_datetime_kst = commit_datetime.astimezone(KST).replace(tzinfo=None)
                            
                            # 오전 4시 이전이면 전날로 처리
                            if commit_datetime_kst.hour < 4:
                                commit_date = (commit_datetime_kst.date() - timedelta(days=1)).strftime('%Y-%m-%d')
                            else:
                                commit_date = commit_datetime_kst.date().strftime('%Y-%m-%d')
                            
                            problem_info['date'] = commit_date
                        except Exception:
                            problem_info['date'] = get_korea_today().strftime('%Y-%m-%d')
                    else:
                        problem_info['date'] = get_korea_now().strftime('%Y-%m-%d')
                except:
                    problem_info['date'] = get_korea_now().strftime('%Y-%m-%d')
                
                users_data[username]['problems'].append(problem_info)
    
    # 각 사용자의 문제를 날짜순으로 정렬
    for username in users_data:
        users_data[username]['problems'].sort(key=lambda x: x['date'])
        users_data[username]['total_count'] = len(users_data[username]['problems'])
        
        if users_data[username]['problems']:
            users_data[username]['last_update'] = users_data[username]['problems'][-1]['date']
        else:
            users_data[username]['last_update'] = get_korea_now().strftime('%Y-%m-%d')
    
    return users_data

def get_attendance_stats(problems):
    """출석 통계 계산"""
    if not problems:
        return {'success_days': 0, 'fail_days': 0, 'attendance_rate': 0.0}
    
    dates = set(p['date'] for p in problems)
    start_date = datetime.strptime(min(dates), '%Y-%m-%d').date()
    end_date = get_korea_today()
    
    # 평일만 계산 (월-금)
    current_date = start_date
    total_weekdays = 0
    success_days = 0
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 월요일=0, 금요일=4
            total_weekdays += 1
            if current_date.strftime('%Y-%m-%d') in dates:
                success_days += 1
        current_date += timedelta(days=1)
    
    fail_days = total_weekdays - success_days
    attendance_rate = (success_days / total_weekdays * 100) if total_weekdays > 0 else 0
    
    return {
        'success_days': success_days,
        'fail_days': fail_days,
        'attendance_rate': attendance_rate
    }

def update_user_readme(username, user_data):
    """개별 사용자의 README 업데이트"""
    user_dir = Path(username)
    if not user_dir.exists():
        return
    
    readme_path = user_dir / "README.md"
    stats = get_attendance_stats(user_data['problems'])
    today = get_korea_today()
    
    # README 내용 생성
    content = f"""# {username}의 백준 문제 풀이

## 📊 통계

- **시작일**: {user_data['problems'][0]['date'] if user_data['problems'] else today.strftime('%Y-%m-%d')}
- **풀이 문제 수**: {user_data['total_count']}문제
- **성공한 날**: {stats['success_days']}일
- **실패한 날**: {stats['fail_days']}일
- **출석률**: {stats['attendance_rate']:.1f}%
- **최근 활동**: {user_data['last_update']}

## 📚 풀이 기록

"""
    
    # 날짜별로 그룹화
    problems_by_date = {}
    for problem in user_data['problems']:
        date = problem['date']
        if date not in problems_by_date:
            problems_by_date[date] = []
        problems_by_date[date].append(problem)
    
    # 날짜 역순으로 정렬하여 출력
    for date in sorted(problems_by_date.keys(), reverse=True):
        content += f"### {date}\n\n"
        for problem in problems_by_date[date]:
            content += f"- [{problem['number']}번 {problem['title']}]({username}/{problem['number']}) - {problem['difficulty']}\n"
        content += "\n"
    
    # 파일에 쓰기
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_main_readme(users_data):
    """메인 README 업데이트"""
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        return
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 전체 통계 계산
    all_problems = []
    for user_data in users_data.values():
        all_problems.extend(user_data['problems'])
    
    total_problems = len(all_problems)
    total_users = len(users_data)
    
    # 시작일 계산 (가장 이른 날짜)
    start_dates = []
    for user_data in users_data.values():
        if user_data['problems']:
            start_dates.append(user_data['problems'][0]['date'])
    
    if start_dates:
        study_start_date = min(start_dates)
        start_date_obj = datetime.strptime(study_start_date, '%Y-%m-%d').date()
        today = get_korea_today()
        study_days = (today - start_date_obj).days + 1
    else:
        study_start_date = get_korea_today().strftime('%Y-%m-%d')
        study_days = 1
    
    # 참여자 테이블 생성
    participant_table = "| 이름 | 시작일 | 풀이 문제 수 | 성공한 날 | 실패한 날 | 출석률 | 최근 활동 |\n"
    participant_table += "|------|--------|-------------|----------|----------|--------|-----------|\n"
    
    for username, user_data in users_data.items():
        stats = get_attendance_stats(user_data['problems'])
        start_date = user_data['problems'][0]['date'] if user_data['problems'] else get_korea_today().strftime('%Y-%m-%d')
        participant_table += f"| {username} | {start_date} | {user_data['total_count']}문제 | {stats['success_days']}일 | {stats['fail_days']}일 | {stats['attendance_rate']:.1f}% | {user_data['last_update']} |\n"
    
    # 통계 섹션
    stats_section = f"""## 📊 전체 스터디 통계

- **📅 스터디 시작일**: {study_start_date}
- **📈 총 풀이 문제**: {total_problems}개
- **⏱️ 도전 기간**: {study_days}일째 도전 중!
- **👥 참여자 수**: {total_users}명"""
    
    # 진행 현황 섹션
    progress_section = f"""## 📈 진행 현황

- **현재 진행**: 총 {total_problems}문제 완료 ({get_korea_today().strftime('%Y년 %m월 %d일')} 기준)"""
    
    # 기존 섹션들을 찾아서 교체
    # 참여자 섹션 교체
    participant_pattern = r'## 👥 참여자.*?(?=##|\Z)'
    new_participant_section = f"## 👥 참여자\n\n{participant_table}\n"
    content = re.sub(participant_pattern, new_participant_section, content, flags=re.DOTALL)
    
    # 통계 섹션 교체
    stats_pattern = r'## 📊 전체 스터디 통계.*?(?=##|\Z)'
    content = re.sub(stats_pattern, f"{stats_section}\n\n---\n\n", content, flags=re.DOTALL)
    
    # 진행 현황 섹션 교체
    progress_pattern = r'## 📈 진행 현황.*?(?=##|\Z)'
    content = re.sub(progress_pattern, progress_section, content, flags=re.DOTALL)
    
    # 파일에 쓰기
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    try:
        # 사용자 데이터 수집
        users_data = scan_users()
        
        # 개인 README 업데이트
        for username, user_data in users_data.items():
            update_user_readme(username, user_data)
        
        # 메인 README 업데이트
        update_main_readme(users_data)
        
        print("✅ README 업데이트 완료!")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
