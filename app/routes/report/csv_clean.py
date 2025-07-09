import pandas as pd
import os

# CSV 파일들이 있는 폴더 경로 설정 (본인 경로에 맞게 수정하세요)
data_dir = 'data/finance'

# 해당 폴더의 모든 파일을 하나씩 확인
for file in os.listdir(data_dir):
    # .csv로 끝나는 파일만 처리
    if file.endswith('.csv'):
        
        # 파일명에서 .csv 제거 후 '_' 기준으로 분리
        parts = file.replace('.csv', '').split('_')
        
        # 정상적인 파일명인지 확인 (예: 삼성전자_005930.csv)
        if len(parts) >= 2:
            stock_name = parts[0]  # 종목명
            file_path = os.path.join(data_dir, file)  # 전체 파일 경로

            try:
                # CSV 파일 읽기
                df = pd.read_csv(file_path)

                # 이미 '종목명' 컬럼이 있는 경우 건너뜀
                if '종목명' in df.columns:
                    print(f"[건너뜀] {file} - 이미 '종목명' 컬럼이 있습니다.")
                    continue  # 다음 파일로 넘어감

                # 종목명 컬럼 추가
                df['종목명'] = stock_name

                # 덮어쓰기 저장
                df.to_csv(file_path, index=False)
                print(f"[완료] {file} - '종목명' 컬럼 추가했습니다.")

            except Exception as e:
                print(f"[에러] {file} 처리 중 오류 발생: {e}")

        else:
            print(f"[주의] 파일명 '{file}'에서 종목명 또는 코드 분리가 정상적으로 되지 않습니다.")
