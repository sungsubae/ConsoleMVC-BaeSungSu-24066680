import sys
from io import StringIO
from unittest.mock import patch
import pytest
from poc1_mvc.view.console_view import ConsoleView


# ── Fixture & 헬퍼 ──────────────────────────────────────────────────────────
@pytest.fixture
def view():
    return ConsoleView()


def _capture(fn, *args, **kwargs) -> str:
    buf = StringIO()
    sys.stdout = buf
    try:
        fn(*args, **kwargs)
    finally:
        sys.stdout = sys.__stdout__
    return buf.getvalue()


# ── show_* 메서드 ────────────────────────────────────────────────────────────
def test_show_main_menu(view):
    out = _capture(view.show_main_menu)
    assert "S-Semi" in out
    assert "1. 고객 관리" in out
    assert "0. 종료" in out


def test_show_sub_menu(view):
    out = _capture(view.show_sub_menu, "고객 관리", ["1. 목록", "2. 등록"])
    assert "고객 관리" in out
    assert "1. 목록" in out
    assert "0. 돌아가기" in out


def test_show_list_with_items(view):
    out = _capture(
        view.show_list,
        "테스트 목록",
        [object()],
        ["ID", "이름"],
        lambda x: ["A001", "홍길동"],
    )
    assert "ID" in out
    assert "홍길동" in out


def test_show_list_empty(view):
    out = _capture(view.show_list, "빈 목록", [], ["ID", "이름"], lambda x: [])
    assert "데이터가 없습니다" in out


def test_show_list_wide_cell(view):
    out = _capture(
        view.show_list,
        "목록",
        [object()],
        ["A"],
        lambda x: ["매우길고긴값입니다"],
    )
    assert "매우길고긴값입니다" in out


def test_show_detail(view):
    out = _capture(view.show_detail, "상세 정보", [("이름", "홍길동"), ("나이", "30")])
    assert "이름" in out
    assert "홍길동" in out


def test_show_options(view):
    out = _capture(view.show_options, ["1. 대기", "2. 진행중"])
    assert "1. 대기" in out
    assert "2. 진행중" in out


def test_show_message(view):
    out = _capture(view.show_message, "저장되었습니다.")
    assert "저장되었습니다" in out


def test_show_error(view):
    out = _capture(view.show_error, "오류입니다.")
    assert "오류입니다" in out


# ── get_* 메서드 ─────────────────────────────────────────────────────────────
def test_get_input(view):
    with patch("builtins.input", return_value="입력값"):
        assert view.get_input("프롬프트") == "입력값"


def test_get_choice_default_prompt(view):
    with patch("builtins.input", return_value="1"):
        assert view.get_choice() == "1"


def test_get_choice_custom_prompt(view):
    with patch("builtins.input", return_value="3"):
        assert view.get_choice("선택하세요") == "3"
