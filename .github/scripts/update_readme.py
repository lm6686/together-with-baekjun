#!/usr/bin/env python3
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 한국 시간대 설정 (GitHub Actions 호환성)
try:
    from zoneinfo import ZoneInfo
    KST = ZoneInfo('Asia/Seoul')
    print("✅ zoneinfo 사용")
except ImportError:
    # zoneinfo 없는 경우 fallback
    print("⚠️ zoneinfo 없음, UTC+9 직접 계산 사용")
    KST = None
except:
    # 완전 fallback - UTC+9 시간 직접 계산
    print("⚠️ 시간대 라이브러리 없음, UTC+9 직접 계산 사용")
    KST = None

def get_korea_now():
    """GitHub Actions 환경 호환 한국 시간 가져오기"""
    utc_now = datetime.utcnow()
    print(f"🕐 UTC 시간: {utc_now}")
    
    if KST is None:
        # 직접 UTC+9 계산
        korea_now = utc_now + timedelta(hours=9)
        print(f"🇰🇷 한국 시간 (UTC+9): {korea_now}")
    else:
        # 한국 시간대로 변환
        korea_now = utc_now.replace(tzinfo=timezone.utc).astimezone(KST).replace(tzinfo=None)
        print(f"🇰🇷 한국 시간 (시간대): {korea_now}")
    
    return korea_now

def get_korea_today():
    """GitHub Actions 환경 호환 한국 오늘 날짜 가져오기"""
    korea_now = get_korea_now()
    today = korea_now.date()
    print(f"📅 한국 오늘: {today}")
    return today

def get_korea_today():
    """한국 시간 기준 오늘 날짜 반환"""
    return get_korea_now().date()

def convert_to_korea_time(dt):
    """datetime을 한국 시간으로 변환"""
    if KST:
        return dt.astimezone(KST)
    else:
        # UTC+9 직접 계산
        if dt.tzinfo is None:
            # naive datetime은 UTC로 가정
            return dt + timedelta(hours=9)
        else:
            # timezone 정보가 있는 경우 UTC로 변환 후 +9
            utc_dt = dt.astimezone(datetime.timezone.utc)
            return utc_dt.replace(tzinfo=None) + timedelta(hours=9)

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
                                    
                                    # 오전 4시 이전이면 전날로 처리 (한국 시간 기준)
                                    commit_datetime_kst = commit_datetime.astimezone(KST)
                                    if commit_datetime_kst.hour < 4:
                                        commit_date = (commit_datetime_kst.date() - timedelta(days=1)).strftime('%Y-%m-%d')
                                    else:
                                        commit_date = commit_datetime_kst.date().strftime('%Y-%m-%d')
                                    
                                    # 디버깅 정보 출력
                                    print(f"🔍 {problem_info['number']}번: 커밋시간 {first_commit} -> 한국시간 {commit_datetime_kst} -> 날짜 {commit_date}")
                                    
                                    problem_info['date'] = commit_date
                                else:
                                    problem_info['date'] = get_korea_now().strftime('%Y-%m-%d')
                                    print(f"⚠️ {problem_info['number']}번: Git 로그 없음, 현재 날짜 사용 {problem_info['date']}")
                            except Exception as e:
                                problem_info['date'] = get_korea_now().strftime('%Y-%m-%d')
                                print(f"❌ {problem_info['number']}번: Git 오류 {e}, 현재 날짜 사용 {problem_info['date']}")
                            
                            users_data[username]['problems'].append(problem_info)
            
        # 문제들을 날짜순으로 정렬
        users_data[username]['problems'].sort(key=lambda x: x['date'])
        users_data[username]['total_count'] = len(users_data[username]['problems'])
        
        # 디버깅 정보
        if users_data[username]['problems']:
            print(f"📊 {username}: {len(users_data[username]['problems'])}문제, 시작일 {users_data[username]['problems'][0]['date']}")
            for p in users_data[username]['problems']:
                print(f"  - {p['date']}: {p['number']}번 {p['title']}")
        
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
    
    # 첫 번째 문제 날짜부터 오늘까지 (한국 시간 기준)
    start_date = min(problem_dates)
    end_date = get_korea_today()
    
    # 시작일이 오늘 이후면 아직 계산할 게 없음
    if start_date > get_korea_today():
        return 0, 0, []
    
    # 평일 날짜들 생성 (월~금)
    weekdays = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 0=월요일, 4=금요일
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    
    # 빼먹은 평일들 (오늘은 아직 할 수 있으니 제외)
    today = get_korea_today()
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

> 🎯 **매일 꾸준히 성장하기!**

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
    all_first_dates = []
    total_problems_all = 0
    
    for username, data in users_data.items():
        if data['problems'] and 'stats' in data:
            first_date = data['stats']['first_date']
            if first_date:
                all_first_dates.append(datetime.strptime(first_date, '%Y-%m-%d').date())
            
            total_problems_all += data['total_count']
    
    if all_first_dates:
        study_start_date = min(all_first_dates).strftime('%Y-%m-%d')
        
        # 전체 도전 기간 계산 (한국 시간 기준)
        start_date = min(all_first_dates)
        end_date = get_korea_today()
        
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
    table_content = """| 이름 | 시작일 | 풀이 문제 수 | 성공한 날 | 실패한 날 | 출석률 | 최근 활동 |
|------|--------|-------------|----------|----------|--------|-----------|
"""
    
    for username, data in users_data.items():
        last_activity = data['last_update'] if data['last_update'] else "-"
        
        if data['problems'] and 'stats' in data:
            # 저장된 통계 사용
            stats = data['stats']
            start_date = stats['first_date']
            success_days = stats['success_days']
            failure_days = stats['failure_days']
            attendance_rate = stats['success_rate']
            
            table_content += f"| {username} | {start_date} | {data['total_count']}문제 | {success_days}일 | {failure_days}일 | {attendance_rate:.1f}% | {last_activity} |\n"
        else:
            table_content += f"| {username} | - | 0문제 | 0일 | 0일 | - | {last_activity} |\n"
    
    # 기존 참여자 섹션부터 끝까지 모든 자동 생성 콘텐츠 제거
    participants_start_pattern = r'\n## 👥 참여자.*'
    content = re.sub(participants_start_pattern + r'.*$', '', content, flags=re.DOTALL)
    
    # 진행 현황 업데이트 (한국 시간 기준)
    today_str = get_korea_now().strftime('%Y년 %m월 %d일')
    
    # 새로운 섹션 생성
    if users_data and all_first_dates:
        new_section = f"""

## 👥 참여자

{table_content}
## 📊 전체 스터디 통계

- **📅 스터디 시작일**: {study_start_date}
- **📈 총 풀이 문제**: {total_problems_all}개
- **⏱️ 도전 기간**: {total_weekdays_all}일째 도전 중!
- **👥 참여자 수**: {len(users_data)}명

---

## 📈 진행 현황

- **현재 진행**: 총 {total_problems_all}문제 완료 ({today_str} 기준)
"""
    else:
        new_section = f"""

## 👥 참여자

{table_content}
## 📊 전체 스터디 통계

- **📊 아직 문제를 푼 참여자가 없습니다.**

---

## 📈 진행 현황

- **현재 진행**: 스터디 준비 중 ({today_str} 기준)
"""
    
    # 새로운 섹션 추가
    content += new_section
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("🔍 폴더 구조 스캔 중...")
    try:
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
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
