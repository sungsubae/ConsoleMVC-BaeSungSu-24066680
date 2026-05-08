import unittest
from io import StringIO
from unittest.mock import patch
import sys
from poc1_mvc.view.console_view import ConsoleView


def _capture(fn, *args, **kwargs) -> str:
    buf = StringIO()
    sys.stdout = buf
    try:
        fn(*args, **kwargs)
    finally:
        sys.stdout = sys.__stdout__
    return buf.getvalue()


class TestConsoleView(unittest.TestCase):
    def setUp(self):
        self.view = ConsoleView()

    def test_show_main_menu(self):
        out = _capture(self.view.show_main_menu)
        self.assertIn("S-Semi", out)
        self.assertIn("1. 고객 관리", out)
        self.assertIn("0. 종료", out)

    def test_show_sub_menu(self):
        out = _capture(self.view.show_sub_menu, "고객 관리", ["1. 목록", "2. 등록"])
        self.assertIn("고객 관리", out)
        self.assertIn("1. 목록", out)
        self.assertIn("0. 돌아가기", out)

    def test_show_list_with_items(self):
        class Item:
            pass

        item = Item()
        out = _capture(
            self.view.show_list,
            "테스트 목록",
            [item],
            ["ID", "이름"],
            lambda x: ["A001", "홍길동"],
        )
        self.assertIn("ID", out)
        self.assertIn("홍길동", out)

    def test_show_list_empty(self):
        out = _capture(self.view.show_list, "빈 목록", [], ["ID", "이름"], lambda x: [])
        self.assertIn("데이터가 없습니다", out)

    def test_show_list_wide_cell(self):
        # 셀 값이 헤더보다 긴 경우 — 컬럼 너비 자동 조정 경로
        out = _capture(
            self.view.show_list,
            "목록",
            [object()],
            ["A"],
            lambda x: ["매우길고긴값입니다"],
        )
        self.assertIn("매우길고긴값입니다", out)

    def test_show_detail(self):
        out = _capture(self.view.show_detail, "상세 정보", [("이름", "홍길동"), ("나이", "30")])
        self.assertIn("이름", out)
        self.assertIn("홍길동", out)

    def test_show_options(self):
        out = _capture(self.view.show_options, ["1. 대기", "2. 진행중"])
        self.assertIn("1. 대기", out)
        self.assertIn("2. 진행중", out)

    def test_show_message(self):
        out = _capture(self.view.show_message, "저장되었습니다.")
        self.assertIn("저장되었습니다", out)

    def test_show_error(self):
        out = _capture(self.view.show_error, "오류입니다.")
        self.assertIn("오류입니다", out)

    @patch("builtins.input", return_value="입력값")
    def test_get_input(self, _):
        self.assertEqual(self.view.get_input("프롬프트"), "입력값")

    @patch("builtins.input", return_value="1")
    def test_get_choice_default_prompt(self, _):
        self.assertEqual(self.view.get_choice(), "1")

    @patch("builtins.input", return_value="3")
    def test_get_choice_custom_prompt(self, _):
        self.assertEqual(self.view.get_choice("선택하세요"), "3")


if __name__ == "__main__":
    unittest.main()
