import tempfile
import unittest
from unittest.mock import patch

from core.bunny import Bunny
from core.fsm_dispatcher import FSMDispatcher
from core.grid import Grid
from core.sl_dispatcher import SLDispatcher
from main import create_dispatcher


class BunnyMovementTests(unittest.TestCase):
    def test_move_updates_origin_and_destination_cells(self):
        grid = Grid(screen=None)
        bunny = Bunny("F")
        self.assertTrue(grid.place_bunny(bunny, 1, 1))

        self.assertTrue(bunny.move(1, 0, grid))

        self.assertIsNone(grid.cells[1][1])
        self.assertIs(grid.cells[1][2], bunny)
        self.assertEqual((bunny.x, bunny.y), (2, 1))

    def test_move_cannot_enter_an_occupied_cell(self):
        grid = Grid(screen=None)
        first = Bunny("F")
        second = Bunny("M")
        grid.place_bunny(first, 1, 1)
        grid.place_bunny(second, 2, 1)

        self.assertFalse(first.move(1, 0, grid))

        self.assertIs(grid.cells[1][1], first)
        self.assertIs(grid.cells[1][2], second)
        self.assertEqual((first.x, first.y), (1, 1))


class DispatcherInitializationTests(unittest.TestCase):
    def test_missing_sl_models_falls_back_to_fsm(self):
        with tempfile.TemporaryDirectory() as model_path:
            with patch(
                "main.SLDispatcher",
                side_effect=FileNotFoundError(f"No models in {model_path}"),
            ):
                dispatcher = create_dispatcher("SL")

        self.assertIsInstance(dispatcher, FSMDispatcher)

    def test_rl_is_not_advertised_as_a_supported_mode(self):
        with self.assertRaisesRegex(ValueError, "'FSM' or 'SL'"):
            create_dispatcher("RL")

    def test_sl_dispatcher_reports_all_missing_models(self):
        with tempfile.TemporaryDirectory() as model_path:
            with self.assertRaises(FileNotFoundError) as context:
                SLDispatcher(model_path=model_path)

        message = str(context.exception)
        self.assertIn("female_sl_logreg.joblib", message)
        self.assertIn("male_sl_logreg.joblib", message)


if __name__ == "__main__":
    unittest.main()
