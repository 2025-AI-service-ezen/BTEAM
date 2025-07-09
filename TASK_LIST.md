## 프로젝트 1단계: 상관관계 기반 감성 사전 구축 태스크 목록

### Task 1: 데이터 로드 및 전처리

**ID:** `156512b1-3d45-4cdd-a64d-9225847773fa`
**Description:** `merged_news_stock.csv` 파일을 로드하고, 'date' 컬럼을 datetime 형식으로 변환 후 시간 순서대로 정렬합니다. '전일비' 컬럼을 숫자형으로 클리닝하고, 종속 변수(`price_up`: 다음 날 종가가 오늘 종가보다 높으면 1, 아니면 0)를 정의합니다.
**Implementation Guide:** `app/services/ai/analyzer.py`의 `load_and_split_data` 함수 내에서 이 작업을 수행합니다. `clean_price_change` 함수를 활용하여 '전일비'를 처리하고, `price_up` 컬럼을 생성합니다.
**Verification Criteria:** `load_and_split_data` 함수가 `df` DataFrame을 반환할 때, 'date' 컬럼이 datetime 형식이고, '전일비'가 숫자형이며, 'price_up' 컬럼이 올바르게 생성되었는지 확인합니다.
**Related Files:**
- `app/services/ai/analyzer.py` (TO_MODIFY)
- `data/finance/merged_news_stock.csv` (REFERENCE)

### Task 2: 데이터셋 분할

**ID:** `fe664107-6421-4699-95b9-f4b211a3be9f`
**Description:** 전처리된 데이터를 학습(70%), 검증(15%), 테스트(15%) 세트로 시간 순서대로 분할합니다.
**Implementation Guide:** `app/services/ai/analyzer.py`의 `load_and_split_data` 함수 내에서 `iloc`를 사용하여 시간 기반 분할을 구현합니다. `train_df`, `val_df`, `test_df`를 반환하도록 합니다.
**Verification Criteria:** `load_and_split_data` 함수가 반환하는 `train_df`, `val_df`, `test_df`의 행 수가 올바른 비율로 분할되었는지, 그리고 각 데이터셋이 시간 순서대로 정렬되어 있는지 확인합니다.
**Dependencies:** 데이터 로드 및 전처리 (`156512b1-3d45-4cdd-a64d-9225847773fa`)
**Related Files:**
- `app/services/ai/analyzer.py` (TO_MODIFY)

### Task 3: 단어 빈도 및 주가 변동 분석

**ID:** `d8fe78c8-17d6-45f5-8516-96b5847c5703`
**Description:** 학습 데이터셋의 각 뉴스 기사(`tokens` 컬럼)에서 단어(토큰)를 추출하고, 각 단어가 포함된 뉴스 기사의 주가 변동(`price_up`)을 추적합니다.
**Implementation Guide:** `app/services/ai/analyzer.py`의 `build_sentiment_dictionary` 함수 내에서 `tokens` 컬럼을 순회하며 각 단어의 출현 횟수와 해당 시점의 `price_up` 값을 기록합니다. `collections.defaultdict`를 활용하여 단어별 긍정/부정 카운트를 저장합니다.
**Verification Criteria:** `build_sentiment_dictionary` 함수가 단어별 `positive_count`, `negative_count`, `total_count`를 정확하게 집계하는지 확인합니다.
**Dependencies:** 데이터셋 분할 (`fe664107-6421-4699-95b9-f4b211a3be9f`)
**Related Files:**
- `app/services/ai/analyzer.py` (TO_MODIFY)

### Task 4: 단어-주가 상관관계 계산

**ID:** `deb5a0f5-1ee0-4c6b-9aea-e764894a5fdd`
**Description:** 각 단어의 출현 여부와 주가 등락(`price_up`) 간의 상관관계를 계산합니다. 이 상관계수는 해당 단어가 주가 등락에 미치는 영향의 강도와 방향을 나타냅니다.
**Implementation Guide:** `app/services/ai/analyzer.py`의 `build_sentiment_dictionary` 함수 내에서 집계된 카운트를 바탕으로 각 단어의 상관계수를 계산합니다. 간단한 방법으로 `(positive_count - negative_count) / total_count`를 사용할 수 있습니다.
**Verification Criteria:** `build_sentiment_dictionary` 함수가 각 단어에 대해 올바른 상관계수를 계산하는지, 특히 긍정적인 단어는 양수, 부정적인 단어는 음수의 상관계수를 가지는지 확인합니다.
**Dependencies:** 단어 빈도 및 주가 변동 분석 (`d8fe78c8-17d6-45f5-8516-96b5847c5703`)
**Related Files:**
- `app/services/ai/analyzer.py` (TO_MODIFY)

### Task 5: 감성 사전 생성 및 저장

**ID:** `cb999792-8ffa-46e2-bea9-b5bb41a9906d`
**Description:** 계산된 상관계수를 바탕으로 긍정 단어 목록(상관계수 > 0)과 부정 단어 목록(상관계수 < 0)을 생성하고, 각 단어와 해당 상관계수를 포함하는 감성 사전을 JSON 파일 형태로 저장합니다.
**Implementation Guide:** `app/services/ai/analyzer.py`의 `build_sentiment_dictionary` 함수 내에서 계산된 상관계수를 `sentiment_dictionary.json` 파일로 저장합니다. 단어와 상관계수를 키-값 쌍으로 저장하며, 상관계수 기준으로 정렬하여 저장합니다.
**Verification Criteria:** `app/models/sentiment_dictionary.json` 파일이 올바른 JSON 형식으로 생성되었는지, 파일 내에 단어와 해당 상관계수가 포함되어 있으며, 상관계수 기준으로 정렬되어 있는지 확인합니다.
**Dependencies:** 단어-주가 상관관계 계산 (`deb5a0f5-1ee0-4c6b-9aea-e764894a5fdd`)
**Related Files:**
- `app/services/ai/analyzer.py` (TO_MODIFY)
- `app/models/sentiment_dictionary.json` (CREATE)
