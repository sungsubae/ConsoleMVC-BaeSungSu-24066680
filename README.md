# ConsoleMVC — PoC 1: MVC 스켈레톤

**S-Semi 반도체 시료 생산주문관리 시스템** 개발을 위한 4단계 PoC 중 첫 번째 단계입니다.  
콘솔 기반 Python 애플리케이션의 MVC 패키지 구조와 역할 분리를 완성합니다.

---

## PoC 로드맵

```
  ┌──────────────────────┐
  │  PoC 1 ✅ (현재)     │──┐
  │  MVC 스켈레톤        │  │
  └──────────────────────┘  │
  ┌──────────────────────┐  │   ┌────────────────────────────┐
  │  PoC 2               │──┼──▶│  반도체 시료               │
  │  JSON 데이터 영속성  │  │   │  생산주문관리 시스템        │
  └──────────────────────┘  │   └────────────────────────────┘
  ┌──────────────────────┐  │
  │  PoC 3               │──┤
  │  데이터 모니터링 Tool │  │
  └──────────────────────┘  │
  ┌──────────────────────┐  │
  │  PoC 4               │──┘
  │  Dummy 데이터 생성   │
  └──────────────────────┘
```

각 PoC는 **독립 저장소**로 관리됩니다. `IRepository`, `IView`, `IController` 인터페이스(ABC)를 통해 구현체를 자유롭게 교체할 수 있도록 설계하여 PoC 간 의존성을 제거했습니다.

---

## 아키텍처

### MVC 계층 구조

```
                        ┌──────────────────────────────────────────┐
                        │              Controller 계층              │
                        │                                          │
                        │  ┌──────────────────────────────────┐   │
                        │  │          AppController           │   │
                        │  │    (메인 루프 · Repository 생성) │   │
                        │  └────────────────┬─────────────────┘   │
                        │                   │ 위임                  │
                        │   ┌───────┬───────┼────────┬──────┐      │
                        │   ▼       ▼       ▼        ▼      ▼      │
                        │ Cust.  Sample  Order   Inven. Process    │
                        │ Ctrl   Ctrl    Ctrl    Ctrl   Ctrl       │
                        └────┬──────────────────────────┬──────────┘
                             │                          │
              show_*()/get_*()                find/save/update/delete
                             │                          │
               ┌─────────────▼──────────┐  ┌───────────▼────────────┐
               │       View 계층         │  │      Model 계층         │
               │                        │  │                        │
               │  ≪interface≫ IView     │  │  ≪interface≫           │
               │         ↓              │  │  IRepository[T]        │
               │    ConsoleView         │  │         ↓              │
               │  print() / input()     │  │  InMemoryRepository    │
               │  (입출력 전담)          │  │  (PoC 2에서 교체)       │
               └────────────┬───────────┘  └────────────────────────┘
                            │
                       ┌────▼────┐
                       │  사용자  │
                       └─────────┘
```

### 사용자 인터랙션 흐름

```
  사용자           ConsoleView          AppController       SubController        IRepository
    │                   │                    │                    │                   │
    │                   │◀── show_main_menu()│                    │                   │
    │◀── 메뉴 출력 ─────│                    │                    │                   │
    │─── 입력 (예: "1") ──────────────────▶│                    │                   │
    │                   │  get_choice() → "1"│                    │                   │
    │                   │                    │── handle() ───────▶│                   │
    │                   │◀──────────── show_sub_menu() ──────────│                   │
    │◀── 서브메뉴 출력 ─│                    │                    │                   │
    │─── 입력 (예: "2") ──────────────────────────────────────▶ │                   │
    │                   │◀──────────── get_input("이름") ────────│                   │
    │◀── 프롬프트 출력 ─│                    │                    │                   │
    │─── "홍길동" 입력 ────────────────────────────────────────▶│                   │
    │                   │                    │                    │── save(entity) ──▶│
    │                   │                    │                    │◀── entity ────────│
    │                   │◀──────────── show_message("등록 완료") ─│                   │
    │◀── 결과 출력 ─────│                    │                    │                   │
```

---

## 클래스 구조

### 인터페이스 계층

```
  abc.ABC
  ├── IRepository[T]              model/interfaces.py
  │   ├── find_all() → list[T]
  │   ├── find_by_id(id) → T | None
  │   ├── save(entity) → T
  │   ├── update(entity) → T | None
  │   └── delete(id) → bool
  │
  ├── IView                       view/interfaces.py
  │   ├── show_main_menu()
  │   ├── show_sub_menu(title, options)
  │   ├── show_list(title, items, headers, row_fn)
  │   ├── show_detail(title, fields)
  │   ├── show_options(options)
  │   ├── show_message(message)
  │   ├── show_error(message)
  │   ├── get_input(prompt) → str
  │   └── get_choice(prompt) → str
  │
  ├── IController                 controller/interfaces.py
  │   └── run()
  │
  └── ISubController              controller/interfaces.py
      └── handle()
```

### 구현체 계층

```
  IRepository[T]
  └── InMemoryRepository[T]       model/repository.py
        내부: _store: dict[str, T]

  IView
  └── ConsoleView                 view/console_view.py
        내부: _SEP, _THIN (구분선 상수)

  IController
  └── AppController               controller/app_controller.py
        의존: IView
        생성: InMemoryRepository × 5 (Customer/Sample/Order/Inventory/Process)
        라우팅: {"1": CustomerController, "2": SampleController, ...}

  ISubController
  ├── CustomerController          controller/customer_controller.py
  │     의존: IRepository[Customer], IView
  ├── SampleController            controller/sample_controller.py
  │     의존: IRepository[Sample], IView
  ├── OrderController             controller/order_controller.py
  │     의존: IRepository[Order], IRepository[Customer],
  │           IRepository[Sample], IRepository[Process], IView
  │           (주문 등록 시 Process 레코드 자동 생성)
  ├── InventoryController         controller/inventory_controller.py
  │     의존: IRepository[Inventory], IRepository[Sample], IView
  └── ProcessController           controller/process_controller.py
        의존: IRepository[Process], IRepository[Order], IView
```

---

## 도메인 모델

```
  CUSTOMER                ORDER                  PROCESS
  ┌─────────────┐         ┌──────────────────┐   ┌────────────────────┐
  │ id (PK)     │─────┐   │ id (PK)          │──▶│ id (PK)            │
  │ name        │     └──▶│ customer_id (FK) │   │ order_id (FK)      │
  │ company     │         │ sample_id (FK)   │   │ stage              │
  │ contact     │         │ quantity         │   │  설계/제조/검사/납품 │
  └─────────────┘    ┌───▶│ status           │   │ status             │
                     │    │  대기/진행중/완료 │   │  대기/진행중/완료   │
  SAMPLE             │    │  /취소           │   │ updated_at         │
  ┌─────────────┐    │    │ created_at       │   └────────────────────┘
  │ id (PK)     │────┤    └──────────────────┘    ※ 주문 등록 시 자동 생성
  │ name        │    │
  │ type        │    │    INVENTORY
  │ specification│   │    ┌──────────────────┐
  └─────────────┘    └───▶│ id (PK)          │
                          │ sample_id (FK)   │
                          │ quantity         │
                          └──────────────────┘
```

---

## 디렉터리 구조

```
ConsoleMVC-BaeSungSu-24066680/
│
├── poc1_mvc/                        # PoC 1 패키지 (import poc1_mvc 로 재사용 가능)
│   ├── __main__.py                  # python -m poc1_mvc 진입점
│   ├── main.py                      # main() 함수 정의
│   │
│   ├── model/
│   │   ├── interfaces.py            # IRepository[T]  ← ABC 인터페이스
│   │   ├── entities.py              # Customer, Sample, Order, Inventory, Process
│   │   │                            # + OrderStatus, ProcessStage, ProcessStatus (Enum)
│   │   └── repository.py            # InMemoryRepository 구현체
│   │
│   ├── view/
│   │   ├── interfaces.py            # IView  ← ABC 인터페이스
│   │   └── console_view.py          # ConsoleView 구현체
│   │
│   └── controller/
│       ├── interfaces.py            # IController, ISubController  ← ABC
│       ├── app_controller.py        # 메인 루프 · Repository 생성 · 라우팅
│       ├── customer_controller.py   # 고객 CRUD
│       ├── sample_controller.py     # 시료 CRUD
│       ├── order_controller.py      # 주문 CRUD + 공정 자동 생성
│       ├── inventory_controller.py  # 재고 조회/등록/수정
│       └── process_controller.py    # 공정 단계·상태 변경
│
└── tests/
    ├── helpers.py                   # MockView — 큐 기반 입력 시뮬레이션
    ├── test_model.py                # 엔티티·InMemoryRepository 단위 테스트
    ├── test_view.py                 # ConsoleView 단위 테스트 (stdout 캡처)
    ├── test_ctrl_customer.py
    ├── test_ctrl_sample.py
    ├── test_ctrl_order.py
    ├── test_ctrl_inventory.py
    ├── test_ctrl_process.py
    └── test_ctrl_app.py
```

---

## 실행

### 요구사항

| 항목 | 버전 |
|------|------|
| Python | 3.12 이상 (개발: 3.14.3) |
| 외부 라이브러리 | 없음 (표준 라이브러리만 사용) |

### 가상환경 활성화

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 애플리케이션 실행

```bash
python -m poc1_mvc
```

### 실행 화면 예시

```
  >> S-Semi 시스템을 시작합니다.

====================================================
      S-Semi 반도체 시료 생산주문관리 시스템
====================================================
  1. 고객 관리
  2. 시료 관리
  3. 주문 관리
  4. 재고 관리
  5. 공정 현황
  0. 종료
====================================================

  선택 >
```

> **주의:** PoC 1은 인메모리 저장소를 사용하므로 종료 시 데이터가 초기화됩니다.  
> 데이터 영속성은 PoC 2(JSON 영속성)에서 구현합니다.

---

## 테스트

### 전체 테스트 실행

```bash
python -m pytest tests/ -v
```

### 특정 파일·케이스 실행

```bash
# 특정 파일만
python -m pytest tests/test_ctrl_order.py -v

# 특정 테스트 케이스만
python -m pytest tests/test_ctrl_order.py::TestOrderController::test_create_valid -v
```

### 커버리지 측정

```bash
.venv\Scripts\python.exe -m coverage run -m pytest tests/
.venv\Scripts\python.exe -m coverage report --include="poc1_mvc/*" -m
```

**결과: 110개 테스트 · 502 구문 · 커버리지 100%**

```
Name                                          Stmts   Miss  Cover
-----------------------------------------------------------------
poc1_mvc\model\interfaces.py                      4      0   100%
poc1_mvc\model\entities.py                       39      0   100%
poc1_mvc\model\repository.py                     23      0   100%
poc1_mvc\view\interfaces.py                       3      0   100%
poc1_mvc\view\console_view.py                    58      0   100%
poc1_mvc\controller\interfaces.py                 3      0   100%
poc1_mvc\controller\app_controller.py            29      0   100%
poc1_mvc\controller\customer_controller.py       57      0   100%
poc1_mvc\controller\sample_controller.py         57      0   100%
poc1_mvc\controller\order_controller.py          87      0   100%
poc1_mvc\controller\inventory_controller.py      64      0   100%
poc1_mvc\controller\process_controller.py        60      0   100%
poc1_mvc\main.py                                  6      0   100%
-----------------------------------------------------------------
TOTAL                                           502      0   100%
```

### 테스트 전략

```
  테스트 대상               방법
  ─────────────────────────────────────────────────────────────
  Model                    직접 인스턴스화 후 CRUD 결과 검증
  (entities, repository)

  View                     sys.stdout 리다이렉션으로 출력 캡처
  (ConsoleView)            unittest.mock.patch 로 input() 모킹

  Controller               MockView (IView 구현체)로 교체
  (모든 Controller)        push_choices() / push_inputs() 로
                           사용자 입력 시나리오를 큐에 등록하고
                           messages / errors 리스트로 결과 검증
```

#### MockView 사용 예시

```python
def test_create_valid(self):
    self.view.push_choices("2", "0")                          # 메뉴: 등록 → 돌아가기
    self.view.push_inputs("홍길동", "S-Semi", "010-1234-5678") # 폼 입력값

    self.ctrl.handle()

    self.assertEqual(len(self.repo.find_all()), 1)
    self.assertTrue(any("등록" in m for m in self.view.messages))
```

---

## PoC 2 연동 포인트

`AppController.__init__` 에서 `InMemoryRepository`를 PoC 2의 `JsonRepository`로 교체하면  
나머지 코드 변경 없이 데이터 영속성을 적용할 수 있습니다.

```python
# controller/app_controller.py — PoC 2 전환 시 이 줄만 변경
customer_repo = InMemoryRepository()   # → JsonRepository("customers.json")
sample_repo   = InMemoryRepository()   # → JsonRepository("samples.json")
order_repo    = InMemoryRepository()   # → JsonRepository("orders.json")
inv_repo      = InMemoryRepository()   # → JsonRepository("inventory.json")
process_repo  = InMemoryRepository()   # → JsonRepository("processes.json")
```

`JsonRepository`는 `IRepository[T]` 인터페이스를 구현하기만 하면 됩니다.
