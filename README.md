# 주식 분석 및 예측 웹 애플리케이션

이 프로젝트는 주식 뉴스 감성 분석을 통해 주가 변동을 예측하고, 다양한 모델의 성능을 비교 분석하는 Flask 기반의 웹 애플리케이션입니다.

## 주요 기능 및 프로젝트 단계

이 프로젝트는 다음과 같은 3단계로 진행됩니다.

### 1단계: 상관관계 기반 감성 사전 구축
- 뉴스의 단어들과 주가 등락 간의 상관관계를 분석하여 데이터 기반의 긍정/부정 단어 목록(감성 사전)을 생성합니다.
- 각 단어는 주가 변동에 미치는 영향의 강도와 방향을 나타내는 상관계수를 가집니다.

### 2단계: 가중치 기반 주가 예측 모델 구성
- 1단계에서 구축된 감성 사전을 바탕으로 새로운 뉴스 기사의 감성 점수를 계산합니다.
- 계산된 감성 점수와 기존 주가 정보를 활용하여 다음 날 주가 등락을 예측하는 머신러닝 모델을 구축합니다.

### 3단계: 예측 모델 비교 분석
- 완성된 감성 기반 예측 모델의 성능을 선형 회귀 모델 및 시계열 회귀 모델과 비교 분석하여 그 효과를 검증합니다.
- 각 모델의 예측 정확도와 장단점을 평가하고 보고서를 작성합니다.

## 기술 스택

- **Backend:** Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** MySQL
- **AI/ML:** Pandas, Scikit-learn, Konlpy (PyTorch/TensorFlow는 시스템 사양 및 호환성(GTX 960)을 고려하여 도입 예정)
- **Deployment:** Docker (예정)

## 설치 및 실행 방법

1.  **저장소 복제:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **가상환경 생성 및 활성화:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate    # Windows
    ```

3.  **의존성 설치:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **데이터베이스 설정:**
    - `db.py` 파일의 DB 연결 정보를 실제 환경에 맞게 수정합니다.
    - `data/finance/merged_news_stock.csv` 파일을 DB에 적재합니다. (관련 스크립트 필요 시 추가)

5.  **프로젝트 단계별 실행:**
    - 각 단계별 구현이 완료되면 `app/services/ai/analyzer.py` 스크립트를 실행하여 모델 학습 및 감성 사전 구축을 진행합니다.
    ```bash
    python app/services/ai/analyzer.py
    ```

6.  **애플리케이션 실행:**
    ```bash
    python app.py
    ```

7.  **웹 브라우저에서 접속:**
    - `http://127.0.0.1:5000`

## 사용 방법

- 회원가입 후 로그인합니다.
- 메인 페이지에서 거래량 순위가 높은 종목을 확인하거나, 원하는 종목을 검색합니다.
- `/report/ai` 페이지에서 종목명을 입력하여 AI 예측 리포트를 확인할 수 있습니다. (2단계 완료 후)# BTEAM
