# Elasticsearch 하이브리드 검색 파이프라인 가이드

## 1. 개요

하이브리드 검색은 **키워드 검색(BM25)**과 **벡터 검색(KNN)**의 점수를 결합하여, 키워드 매칭의 정확성과 의미 기반 검색의 유연성을 동시에 활용하는 방식이다.

```
사용자 쿼리
    │
    ├──→ [BM25 키워드 검색] ──→ 텍스트 매칭 점수 (boost 가중치)
    │        └─ Elasticsearch match query + 동의어 분석기
    │
    ├──→ [KNN 벡터 검색] ──→ 코사인 유사도 점수 (boost 가중치)
    │        └─ 쿼리 텍스트 → 임베딩 모델 → 벡터 → dense_vector 필드 검색
    │
    └──→ [점수 결합] ──→ 최종 랭킹 결과
             └─ Elasticsearch가 두 점수를 boost 비율로 합산
```

---

## 2. 의존성

### Python 패키지

```bash
pip install elasticsearch sentence-transformers
```

| 패키지 | 용도 |
|---|---|
| `elasticsearch` (>=8.x) | Elasticsearch 클라이언트 |
| `sentence-transformers` | 텍스트 → 벡터 변환 |

### 임베딩 모델

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('jhgan/ko-sbert-nli')
```

- **모델**: `jhgan/ko-sbert-nli` — 한국어 특화 Sentence-BERT
- **벡터 차원**: 768
- **최초 로드 시 HuggingFace에서 다운로드**됨 → 프로덕션에서는 로컬 캐시 경로 지정 권장 (6절 참조)

---

## 3. 인덱스 설계

### 3.1 전체 매핑 스키마

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "analysis": {
      "filter": {
        "my_synonym_filter": {
          "type": "synonym",
          "synonyms": [
            "강아지, 멍멍이, 댕댕이, 개",
            "고양이, 야옹이, 냥이",
            "포토카드, 포토 카드, 포카"
          ]
        }
      },
      "analyzer": {
        "my_synonym_analyzer": {
          "tokenizer": "standard",
          "filter": ["lowercase", "my_synonym_filter"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "id":             { "type": "keyword" },
      "product_name":   { "type": "text", "analyzer": "my_synonym_analyzer" },
      "description":    { "type": "text", "analyzer": "standard" },
      "category":       { "type": "keyword" },
      "product_vector": {
        "type": "dense_vector",
        "dims": 768,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}
```

### 3.2 설계 포인트

| 항목 | 설명 |
|---|---|
| **`dense_vector`** | `index: true`가 있어야 KNN 검색이 가능하다. `similarity: cosine`은 정규화된 임베딩에 적합. |
| **`dims: 768`** | 사용하는 임베딩 모델의 출력 차원과 반드시 일치해야 한다. |
| **동의어 분석기** | BM25 검색 시 동의어 확장을 적용한다. `text` 타입 필드에 `analyzer`로 지정. |
| **`number_of_shards`** | 데이터 규모에 맞게 조정. 수십만 건 이하는 1~2개로 충분. |
| **`number_of_replicas`** | PoC에서는 0이었으나, 프로덕션에서는 **1 이상** 권장 (고가용성). |

### 3.3 동의어 사전

동의어는 두 가지 형식을 지원한다:

```
# 양방향 동의어: 어느 쪽으로 검색해도 서로 매칭
"강아지, 멍멍이, 댕댕이, 개"

# 단방향 동의어: 왼쪽 → 오른쪽으로만 확장
"갤탭 => 갤럭시탭"
```

> **프로덕션 권장**: 인라인 `synonyms` 대신 `synonyms_path`로 외부 파일을 지정하면 인덱스 재생성 없이 동의어를 관리할 수 있다.
>
> ```json
> {
>   "type": "synonym",
>   "synonyms_path": "analysis/synonyms.txt"
> }
> ```
> 파일 경로는 Elasticsearch의 `config/` 디렉토리 기준 상대경로이다.

---

## 4. 데이터 인덱싱

### 4.1 벡터 생성 + Bulk 색인

```python
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer

# 연결 및 모델 로드
es = Elasticsearch(ES_URL, request_timeout=30)
model = SentenceTransformer(MODEL_NAME)

def index_documents(documents: list[dict], index_name: str):
    """
    documents: [{"id": "...", "product_name": "...", "description": "...", "category": "..."}, ...]
    """
    actions = []
    for doc in documents:
        # 검색 대상 텍스트를 결합하여 벡터 생성
        full_text = f"{doc['product_name']} {doc['description']}"
        vector = model.encode(full_text).tolist()

        doc["product_vector"] = vector
        actions.append({
            "_index": index_name,
            "_source": doc
        })

    # Bulk API로 일괄 색인
    success, errors = helpers.bulk(es, actions, raise_on_error=False)
    print(f"색인 완료: {success}건 성공, {len(errors)}건 실패")
    return success, errors
```

### 4.2 대량 데이터 색인 시 참고사항

- **배치 처리**: `helpers.bulk`의 `chunk_size` 파라미터로 한 번에 보내는 문서 수를 조절 (기본 500)
- **벡터 생성 병목**: `model.encode()`가 가장 느린 구간. 배치 인코딩(`model.encode(texts_list)`)으로 처리하면 GPU 활용 시 대폭 빨라짐
- **refresh 제어**: 대량 색인 중에는 `refresh_interval: -1`로 설정 후, 완료 후 `_refresh` API 호출

---

## 5. 하이브리드 검색 쿼리 (핵심)

### 5.1 쿼리 구조

Elasticsearch의 `search` API에서 **`knn` 파라미터와 `query` 파라미터를 동시에** 전달하면, 두 결과의 점수가 자동으로 합산되어 하이브리드 검색이 수행된다.

```python
def hybrid_search(query: str, index_name: str, k: int = 10) -> dict:
    # 1) 쿼리 텍스트를 벡터로 변환
    query_vector = model.encode(query).tolist()

    # 2) 하이브리드 검색 실행
    search_body = {
        # ── KNN (벡터 검색) ──
        "knn": {
            "field": "product_vector",      # dense_vector 필드명
            "query_vector": query_vector,    # 쿼리 벡터
            "k": k,                          # 최종 반환할 KNN 결과 수
            "num_candidates": 100,           # ANN 탐색 후보 수
            "boost": 0.6                     # ← 벡터 검색 가중치
        },
        # ── BM25 (키워드 검색) ──
        "query": {
            "match": {
                "product_name": {
                    "query": query,
                    "boost": 0.4             # ← 키워드 검색 가중치
                }
            }
        },
        "_source": ["id", "product_name", "category", "description"],
        "size": k
    }

    response = es.search(index=index_name, body=search_body)
    return response
```

### 5.2 점수 결합 방식

Elasticsearch는 knn과 query를 함께 사용할 때 **두 점수를 단순 합산(linear combination)**한다:

```
최종 점수 = (BM25 점수 × query boost) + (KNN 점수 × knn boost)
```

예를 들어 `knn.boost=0.6`, `query.match.boost=0.4`이면:
- 벡터 유사도가 높은 문서는 KNN 점수가 높아 상위에 노출
- 정확한 키워드가 포함된 문서는 BM25 점수가 높아 상위에 노출
- **두 조건 모두 만족하는 문서가 가장 높은 점수**를 받음

### 5.3 파라미터 상세

#### `knn` 파라미터

| 파라미터 | 설명 | 권장값 |
|---|---|---|
| `field` | `dense_vector` 타입 필드명 | 매핑에 정의한 벡터 필드 |
| `query_vector` | 쿼리 임베딩 벡터 (float 배열) | `model.encode(query).tolist()` |
| `k` | KNN이 반환할 최종 결과 수 | `size`와 동일하게 설정 |
| `num_candidates` | HNSW 탐색 후보 수. 높을수록 정확하지만 느림 | 50~200 (일반적으로 100) |
| `boost` | 벡터 검색 점수 가중치 | 0.3~0.7 (튜닝 필요) |

#### `query` 파라미터

| 파라미터 | 설명 | 권장값 |
|---|---|---|
| `match.{field}.query` | 키워드 검색 쿼리 텍스트 | 사용자 입력 원문 |
| `match.{field}.boost` | 키워드 검색 점수 가중치 | knn boost와 합이 1.0 |

### 5.4 boost 가중치 튜닝 가이드

두 boost의 합을 1.0으로 맞출 필요는 없지만, 비율을 직관적으로 이해하기 위해 **합산 1.0 기준**을 권장한다.

| 시나리오 | knn boost | query boost | 설명 |
|---|---|---|---|
| 의미 검색 중심 | 0.7 | 0.3 | "자취생 밥 해먹기" 같은 자연어 질의에 강함 |
| **균형 (PoC 기본값)** | **0.6** | **0.4** | 범용적으로 적합한 시작점 |
| 키워드 중심 | 0.4 | 0.6 | 상품 코드/정확한 명칭 검색에 유리 |
| 키워드 강화 | 0.3 | 0.7 | 동의어 사전이 잘 구축된 경우 |

> **튜닝 방법**: 평가 데이터셋(query + 정답 ID)을 준비한 뒤, boost 조합별 MRR/Top-K 정확도를 비교하여 최적값을 선택한다 (7절 참조).

### 5.5 multi_match로 여러 필드 검색

검색 대상 필드가 여러 개라면 `multi_match`를 사용한다:

```python
"query": {
    "multi_match": {
        "query": query,
        "fields": ["product_name^2", "description"],  # product_name에 2배 가중치
        "boost": 0.4
    }
}
```

### 5.6 검색 결과 처리

```python
response = hybrid_search("욕실 슬리퍼", index_name="my_index")

for hit in response['hits']['hits']:
    score  = hit['_score']                          # 최종 합산 점수
    source = hit['_source']
    print(f"[{score:.4f}] {source['product_name']}")
```

---

## 6. 프로덕션 체크리스트

### 6.1 설정 외부화

PoC에서 하드코딩된 값들을 환경변수 또는 설정 파일로 분리한다.

```python
import os

# 환경변수에서 읽기 (예시)
ES_URL       = os.getenv("ES_URL", "http://localhost:9200")
ES_INDEX     = os.getenv("ES_INDEX", "products_v1")
ES_TIMEOUT   = int(os.getenv("ES_TIMEOUT", "30"))
MODEL_NAME   = os.getenv("EMBEDDING_MODEL", "jhgan/ko-sbert-nli")
KNN_BOOST    = float(os.getenv("KNN_BOOST", "0.6"))
QUERY_BOOST  = float(os.getenv("QUERY_BOOST", "0.4"))
KNN_K        = int(os.getenv("KNN_K", "10"))
NUM_CANDIDATES = int(os.getenv("NUM_CANDIDATES", "100"))
```

**PoC → 프로덕션 변경 포인트 요약:**

| 항목 | PoC (하드코딩) | 프로덕션 |
|---|---|---|
| ES 주소 | `http://127.0.0.1:9200` | 환경변수 `ES_URL` |
| 인덱스명 | `daiso_final_v1` | 환경변수 `ES_INDEX` |
| 모델명 | `jhgan/ko-sbert-nli` | 환경변수 `EMBEDDING_MODEL` |
| boost 가중치 | `0.6` / `0.4` | 환경변수 또는 설정 파일 |
| replicas | `0` | `1` 이상 |

### 6.2 Elasticsearch 연결 보안

```python
es = Elasticsearch(
    ES_URL,
    basic_auth=(os.getenv("ES_USER"), os.getenv("ES_PASSWORD")),
    ca_certs="/path/to/ca.crt",     # TLS 인증서 (HTTPS 사용 시)
    request_timeout=ES_TIMEOUT,
    max_retries=3,
    retry_on_timeout=True
)
```

### 6.3 임베딩 모델 캐싱

`sentence-transformers`는 기본적으로 `~/.cache/huggingface/`에 모델을 캐싱한다. 프로덕션 서버에서는:

```python
import os

# 캐시 디렉토리 명시 지정
os.environ["TRANSFORMERS_CACHE"] = "/app/models/cache"
os.environ["HF_HOME"] = "/app/models/cache"

# 또는 로컬에 직접 저장한 모델 로드
model = SentenceTransformer("/app/models/ko-sbert-nli")
```

- 배포 전 모델을 미리 다운로드하여 서버에 배치
- HuggingFace 외부 접근이 불가한 환경에서는 로컬 경로 필수

### 6.4 에러 핸들링

```python
from elasticsearch import ConnectionError, NotFoundError, RequestError

try:
    response = es.search(index=ES_INDEX, body=search_body)
except ConnectionError:
    # ES 서버 연결 실패 → 재시도 또는 fallback
    ...
except NotFoundError:
    # 인덱스가 존재하지 않음 → 인덱스 생성 필요
    ...
except RequestError as e:
    # 쿼리 구문 오류 (벡터 차원 불일치 등)
    ...
```

---

## 7. 성능 평가 (간결)

평가 데이터셋(`query` + `target_ids`)을 준비한 뒤, 검색 결과에서 정답이 몇 번째에 나오는지(`Rank`)를 기록하여 아래 지표를 산출한다.

| 지표 | 수식 | 의미 |
|---|---|---|
| **Top-1 정확도** | (1등이 정답인 건수) / 전체 건수 | 첫 번째 결과의 정확성 |
| **Top-K 정확도** | (K등 이내에 정답이 있는 건수) / 전체 건수 | K개 결과 안에 정답이 포함되는 비율 |
| **MRR** | (1/Rank들의 평균) | 정답의 순위가 높을수록 1.0에 가까움 |
| **Latency** | 쿼리당 소요시간 (ms) | 응답 속도 |

boost 가중치 조합별로 위 지표를 비교하여 최적의 설정을 선택한다.
