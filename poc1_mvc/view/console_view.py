from collections.abc import Callable
from .interfaces import IView


class ConsoleView(IView):
    _SEP = "=" * 52
    _THIN = "-" * 52

    def show_main_menu(self) -> None:
        print(f"\n{self._SEP}")
        print("      S-Semi 반도체 시료 생산주문관리 시스템")
        print(self._SEP)
        print("  1. 고객 관리")
        print("  2. 시료 관리")
        print("  3. 주문 관리")
        print("  4. 재고 관리")
        print("  5. 공정 현황")
        print("  0. 종료")
        print(self._SEP)

    def show_sub_menu(self, title: str, options: list[str]) -> None:
        print(f"\n[ {title} ]")
        print(self._THIN)
        for opt in options:
            print(f"  {opt}")
        print("  0. 돌아가기")
        print(self._THIN)

    def show_list(
        self,
        title: str,
        items: list,
        headers: list[str],
        row_fn: Callable[[object], list[str]],
    ) -> None:
        print(f"\n[ {title} ] — 총 {len(items)}건")
        if not items:
            print("  데이터가 없습니다.")
            return

        rows = [row_fn(item) for item in items]
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))

        fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
        print(self._THIN)
        print(fmt.format(*headers))
        print(self._THIN)
        for row in rows:
            print(fmt.format(*[str(c) for c in row]))
        print(self._THIN)

    def show_detail(self, title: str, fields: list[tuple[str, str]]) -> None:
        print(f"\n[ {title} ]")
        print(self._THIN)
        for label, value in fields:
            print(f"  {label:<14}: {value}")
        print(self._THIN)

    def show_options(self, options: list[str]) -> None:
        for opt in options:
            print(f"  {opt}")

    def show_message(self, message: str) -> None:
        print(f"  >> {message}")

    def show_error(self, message: str) -> None:
        print(f"  [오류] {message}")

    def get_input(self, prompt: str) -> str:
        return input(f"  {prompt}: ").strip()

    def get_choice(self, prompt: str = "선택") -> str:
        return input(f"\n  {prompt} > ").strip()
