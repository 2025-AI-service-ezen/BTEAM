
import pandas as pd
from konlpy.tag import Okt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib
import os
import re
import json
from collections import defaultdict

# 한국어 형태소 분석기 초기화
okt = Okt()

def clean_price_change(text):
    """'전일비' 컬럼의 문자열을 숫자로 변환합니다."""
    if isinstance(text, (int, float)):
        return text
    if not isinstance(text, str):
        return 0

    text = text.strip()
    sign = 1
    if '하락' in text:
        sign = -1
    
    # 숫자만 추출
    num_str = re.sub(r'[^\d]', '', text)
    if not num_str:
        return 0

    return sign * int(num_str)

def build_sentiment_dictionary(df, output_path):
    """뉴스 단어와 주가 등락 간의 상관관계를 분석하여 감성 사전을 구축합니다."""
    word_sentiment_scores = defaultdict(lambda: {'positive_count': 0, 'negative_count': 0, 'total_count': 0})

    for index, row in df.iterrows():
        tokens_str = row['tokens']
        price_up = row['price_up']

        # tokens_str이 문자열이 아니거나 비어있으면 건너뛰기
        if not isinstance(tokens_str, str) or not tokens_str.strip():
            continue

        # 문자열 형태의 리스트를 실제 리스트로 변환
        try:
            # '['와 ']'를 제거하고 쉼표로 분리하여 단어 리스트 생성
            words = [word.strip().strip("'") for word in tokens_str.strip('[]').split(',') if word.strip()]
        except Exception as e:
            print(f"토큰 파싱 오류: {tokens_str}, 오류: {e}")
            continue

        for word in words:
            word_sentiment_scores[word]['total_count'] += 1
            if price_up == 1:
                word_sentiment_scores[word]['positive_count'] += 1
            else:
                word_sentiment_scores[word]['negative_count'] += 1

    sentiment_dictionary = {}
    for word, counts in word_sentiment_scores.items():
        pos_count = counts['positive_count']
        neg_count = counts['negative_count']
        total_count = counts['total_count']

        if total_count > 0:
            # 간단한 상관계수 (긍정 발생 비율 - 부정 발생 비율)
            # 실제 상관계수는 더 복잡하지만, 여기서는 방향성을 보기 위함
            correlation = (pos_count - neg_count) / total_count
            sentiment_dictionary[word] = correlation

    # 상관계수 기준으로 정렬하여 저장
    sorted_sentiment = dict(sorted(sentiment_dictionary.items(), key=lambda item: item[1], reverse=True))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_sentiment, f, ensure_ascii=False, indent=4)
    
    print(f"감성 사전 구축 완료 및 저장: {output_path}")
    return sorted_sentiment

def analyze_sentiment(text, sentiment_dict):
    """뉴스 기사 텍스트의 감성 점수를 분석합니다. (데이터 기반 감성 사전 사용)"""
    if not isinstance(text, str):
        return 0

    nouns = okt.nouns(text)
    score = 0
    for word in nouns:
        if word in sentiment_dict:
            score += sentiment_dict[word]
    return score

def train_model(train_df, val_df, model_path, sentiment_dict):
    """감성 점수와 주가 데이터를 사용하여 주가 등락 예측 모델을 학습합니다."""
    # 피처 엔지니어링 (감성 점수 계산)
    train_df['sentiment_score'] = train_df['tokens'].apply(lambda x: analyze_sentiment(x, sentiment_dict))
    val_df['sentiment_score'] = val_df['tokens'].apply(lambda x: analyze_sentiment(x, sentiment_dict))
    
    # 사용할 특성 선택
    features = ['sentiment_score', '전일비', '거래량']
    
    # 데이터 클리닝 (NaN 값 제거)
    train_df = train_df.dropna(subset=features + ['price_up'])
    val_df = val_df.dropna(subset=features + ['price_up'])
    
    X_train = train_df[features]
    y_train = train_df['price_up']
    X_val = val_df[features]
    y_val = val_df['price_up']

    # 3. 모델 학습
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # 4. 모델 저장
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    
    print(f"모델 학습 완료 및 저장: {model_path}")
    print(f"학습 데이터 정확도: {model.score(X_train, y_train):.4f}")
    print(f"검증 데이터 정확도: {model.score(X_val, y_val):.4f}")

def predict_price_movement(news_text, previous_day_change, volume, model_path, sentiment_dict_path):
    """학습된 모델을 사용하여 주가 등락을 예측합니다."""
    if not os.path.exists(model_path):
        raise FileNotFoundError("학습된 모델 파일을 찾을 수 없습니다.")
    if not os.path.exists(sentiment_dict_path):
        raise FileNotFoundError("감성 사전 파일을 찾을 수 없습니다.")
        
    # 1. 모델 로드
    model = joblib.load(model_path)
    
    # 2. 감성 사전 로드
    with open(sentiment_dict_path, 'r', encoding='utf-8') as f:
        sentiment_dict = json.load(f)

    # 3. 입력 데이터 생성
    sentiment_score = analyze_sentiment(news_text, sentiment_dict)
    input_data = pd.DataFrame([[sentiment_score, previous_day_change, volume]], 
                              columns=['sentiment_score', '전일비', '거래량'])
    
    # 4. 예측
    prediction = model.predict(input_data)
    prediction_proba = model.predict_proba(input_data)
    
    return {
        'prediction': '상승' if prediction[0] == 1 else '하락',
        'probability': {
            'down': f"{prediction_proba[0][0]:.2%}",
            'up': f"{prediction_proba[0][1]:.2%}"
        }
    }

# 이 파일이 직접 실행될 때 모델 학습을 수행
if __name__ == '__main__':
    # 경로 설정
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    data_file = os.path.join(project_root, 'data', 'finance', 'merged_news_stock.csv')
    model_file = os.path.join(project_root, 'app', 'models', 'stock_prediction_model.pkl')
    sentiment_dict_file = os.path.join(project_root, 'app', 'models', 'sentiment_dictionary.json')
    
    try:
        train_df, val_df, test_df = load_and_split_data(data_file)
        
        # 1단계: 감성 사전 구축
        sentiment_dict = build_sentiment_dictionary(train_df, sentiment_dict_file)

        # 2단계: 예측 모델 학습
        train_model(train_df, val_df, model_file, sentiment_dict)
        
        # 3단계: 모델 비교 (여기서는 아직 구현되지 않음)

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"오류 발생: {e}")

