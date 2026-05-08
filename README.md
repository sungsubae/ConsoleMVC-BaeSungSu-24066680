# ConsoleMVC — PoC 1: MVC 스켈레톤

S-Semi 반도체 시료 생산주문관리 시스템을 위한 콘솔 기반 MVC 스켈레톤입니다.

## 시작하기

```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 실행
python -m poc1_mvc
```

> Python 3.12+ / 외부 의존성 없음

## 기능

| 메뉴 | 동작 |
|------|------|
| 고객 관리 | 등록 · 조회 · 수정 · 삭제 |
| 시료 관리 | 등록 · 조회 · 수정 · 삭제 |
| 주문 관리 | 등록 · 조회 · 상태 변경 · 삭제 |
| 재고 관리 | 등록 · 조회 · 수량 수정 |
| 공정 현황 | 단계 변경 · 상태 변경 |

주문 등록 시 공정 레코드(`설계` 단계)가 자동으로 생성됩니다.

> PoC 1은 인메모리 저장소를 사용하므로 종료 시 데이터가 초기화됩니다.

## 아키텍처

```
          ┌───────────────────────────────────────────┐
          │              Controller                    │
          │  AppController ──▶ SubController × 5      │
          │  (메인 루프 · 라우팅)  (도메인별 CRUD)     │
          └──────────┬───────────────────┬────────────┘
                     │                   │
              IView 호출          IRepository 호출
                     │                   │
          ┌──────────▼──────┐  ┌─────────▼──────────┐
          │      View        │  │       Model         │
          │  ConsoleView     │  │  InMemoryRepository │
          │  (입출력 전담)   │  │  (PoC 2에서 교체)   │
          └─────────────────┘  └────────────────────┘
```

모든 레이어는 ABC 인터페이스(`IView`, `IRepository`, `IController`)를 통해 연결됩니다.
PoC 2에서 `InMemoryRepository`를 `JsonRepository`로 교체할 때 다른 코드는 변경하지 않아도 됩니다.

## 도메인 모델

```
  CUSTOMER ──▶ ORDER ──▶ PROCESS
               │          (주문 생성 시 자동)
               ▼
  SAMPLE ──▶ INVENTORY
```

| 엔티티 | 주요 필드 |
|--------|-----------|
| Customer | name, company, contact |
| Sample | name, type, specification |
| Order | customer_id, sample_id, quantity, status |
| Inventory | sample_id, quantity |
| Process | order_id, stage, status |

## 프로젝트 구조

```
poc1_mvc/
├── model/        interfaces.py · entities.py · repository.py
├── view/         interfaces.py · console_view.py
└── controller/   interfaces.py · app_controller.py · *_controller.py × 5

tests/
├── helpers.py    MockView (큐 기반 입력 시뮬레이션)
└── test_*.py     파일별 단위 테스트
```

## 테스트

```bash
# 전체 실행
python -m pytest tests/ -v

# 커버리지 측정
.venv\Scripts\python.exe -m coverage run -m pytest tests/
.venv\Scripts\python.exe -m coverage report --include="poc1_mvc/*"
```

**110 tests · 100% coverage**

Controller 테스트는 `MockView`로 사용자 입력을 시뮬레이션합니다.

```python
def test_create_valid(run, view, repo):
    run(["2", "0"], ["홍길동", "S-Semi", "010-1234-5678"])
    assert any("등록" in m for m in view.messages)
```

## PoC 구성

이 저장소는 4단계 PoC 중 1번째입니다. 각 PoC는 독립 저장소로 관리됩니다.

| # | 내용 | 상태 |
|---|------|------|
| 1 | MVC 스켈레톤 | ✅ 현재 |
| 2 | JSON 데이터 영속성 (CRUD) | |
| 3 | 데이터 모니터링 Tool | |
| 4 | Dummy 데이터 생성 Tool | |
