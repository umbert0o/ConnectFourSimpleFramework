from __future__ import annotations

import pytest

from connect_four.ui.renderer import _compute_dimensions, HEADER_HEIGHT


class TestComputeDimensions:
    def test_standard_board(self) -> None:
        result = _compute_dimensions(rows=6, cols=7, cell_size=100, header_height=80)
        assert result == (700, 680, 700, 600)

    def test_non_standard_board(self) -> None:
        result = _compute_dimensions(rows=5, cols=5, cell_size=80, header_height=80)
        assert result == (400, 480, 400, 400)

    def test_large_board_exceeds_max(self) -> None:
        w, h, _, _ = _compute_dimensions(
            rows=15, cols=15, cell_size=100, header_height=80
        )
        assert w > 1200 or h > 900

    def test_default_header_matches_constant(self) -> None:
        w, h, bw, bh = _compute_dimensions(6, 7, 100, HEADER_HEIGHT)
        assert h == bh + HEADER_HEIGHT
        assert w == bw

    def test_single_column(self) -> None:
        result = _compute_dimensions(rows=4, cols=1, cell_size=100, header_height=80)
        assert result == (100, 480, 100, 400)


class TestOldConstantsRemoved:
    def test_no_board_width_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "BOARD_WIDTH")

    def test_no_board_height_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "BOARD_HEIGHT")

    def test_no_window_width_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "WINDOW_WIDTH")

    def test_no_window_height_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "WINDOW_HEIGHT")

    def test_no_cell_size_constant(self) -> None:
        import connect_four.ui.renderer as mod

        assert not hasattr(mod, "CELL_SIZE")

    def test_header_height_still_exists(self) -> None:
        import connect_four.ui.renderer as mod

        assert hasattr(mod, "HEADER_HEIGHT")
        assert mod.HEADER_HEIGHT == 80


class TestDrawStatusRemoved:
    def test_no_draw_status_method(self) -> None:
        from connect_four.ui.renderer import PygameRenderer

        assert not hasattr(PygameRenderer, "_draw_status")

    def test_no_show_status_method(self) -> None:
        from connect_four.ui.renderer import PygameRenderer

        assert not hasattr(PygameRenderer, "show_status")
