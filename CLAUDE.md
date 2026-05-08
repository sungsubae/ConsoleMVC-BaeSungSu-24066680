# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

반도체 회사 **S-Semi**의 **반도체 시료 생산주문관리 시스템** PoC 프로젝트.
콘솔 기반(CLI) Python 애플리케이션이며, 4개의 PoC를 독립 repository로 분리하여 개발한다.

### PoC 구성 (각각 독립 repository)

| PoC | 내용 | 현재 repo |
|-----|------|-----------|
| 1 | MVC 스켈레톤 코드 | **현재 (ConsoleMVC-BaeSungSu-24066680)** |
| 2 | JSON 기반 데이터 영속성 (CRUD) | 별도 repo |
| 3 | 데이터 모니터링 Tool | 별도 repo |
| 4 | Dummy 데이터 생성 Tool | 별도 repo |

PoC 간 의존성 없음 — Interface(ABC) 또는 duck typing으로 결합도를 최소화한다.
최종적으로 4개의 PoC를 통합하여 실제 시스템을 개발한다.

## 런타임 환경

- Python 3.14.3
- 가상환경: `.venv/` (프로젝트 루트)
- 외부 의존성 없음 (표준 라이브러리만 사용)

## 실행 명령

```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 애플리케이션 실행
python -m poc1_mvc

# 또는 직접 실행
python poc1_mvc/main.py
```

## 디렉터리 구조 (설계)

```
ConsoleMVC-BaeSungSu-24066680/
├── poc1_mvc/               # PoC 1 패키지 (현재 개발 대상)
│   ├── __init__.py
│   ├── main.py             # 진입점: App 조립 및 실행 루프
│   ├── model/              # 도메인 모델 및 비즈니스 로직
│   │   ├── __init__.py
│   │   └── interfaces.py   # ABC 기반 인터페이스 정의
│   ├── view/               # 콘솔 출력 담당
│   │   ├── __init__.py
│   │   └── interfaces.py
│   └── controller/         # 입력 처리 및 Model-View 조율
│       ├── __init__.py
│       └── interfaces.py
└── CLAUDE.md
```

> 다른 PoC는 `poc2_persistence/`, `poc3_monitor/`, `poc4_dummy/` 형태로 같은 루트에 추가된다.
> 각 PoC 폴더는 독립 패키지로 `import poc1_mvc` 형태로 다른 PoC나 최종 시스템에서 재사용 가능하도록 설계한다.

## 아키텍처 원칙 (PoC 1)

### MVC 역할 분리

- **Model**: 시료(Sample), 주문(Order), 고객(Customer) 등 도메인 객체. 비즈니스 로직 포함. View/Controller를 직접 참조하지 않음.
- **View**: 콘솔 입출력만 담당. `print()`와 `input()`을 View 외부에서 직접 호출하지 않음.
- **Controller**: 사용자 입력을 받아 Model을 조작하고 View를 갱신. Model과 View 간 중재자.

### 인터페이스 설계

각 레이어는 `abc.ABC` + `@abstractmethod`로 인터페이스를 정의하여 구현체를 교체 가능하게 만든다.
이 구조가 다른 PoC에서 해당 레이어를 독립적으로 import할 수 있는 기반이 된다.

```python
# 예시
from abc import ABC, abstractmethod

class IModel(ABC):
    @abstractmethod
    def get_all(self) -> list: ...

class IView(ABC):
    @abstractmethod
    def render(self, data) -> None: ...

class IController(ABC):
    @abstractmethod
    def handle_input(self, command: str) -> None: ...
```

### 도메인 컨텍스트

S-Semi 시스템의 핵심 엔티티:
- **시료(Sample)**: 반도체 시료 종류, 사양
- **주문(Order)**: 고객별 시료 주문 내역
- **고객(Customer)**: 납품 대상 고객사
- **재고(Inventory)**: 시료 재고 현황
- **공정(Process)**: 시료 생산 공정 현황
