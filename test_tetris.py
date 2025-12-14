import pytest
from unittest.mock import patch, MagicMock, call
import pygame
import random
import tetris


def test_tetris_init():
    game = tetris.Tetris(10, 20)
    assert game.width == 10
    assert game.height == 20
    assert len(game.grid) == 20
    assert len(game.grid[0]) == 10
    assert game.game_over == False
    assert game.score == 0
    assert game.current_piece is not None

def test_new_piece():
    game = tetris.Tetris(10, 20)

    with patch('random.choice') as mock_choice:

        mock_choice.side_effect = [
            tetris.SHAPES[0],  # форма
            tetris.COLORS[0]  # цвет
        ]

        piece = game.new_piece()

        assert piece.x == 5
        assert piece.y == 0
        assert piece.shape == tetris.SHAPES[0]
        assert piece.color == tetris.COLORS[0]

def test_valid_move():
    game = tetris.Tetris(10, 20)

    piece = tetris.Tetromino(4, 0, tetris.SHAPES[0])

    result = game.valid_move(piece, 0, 0, 0)
    assert result == True

    result = game.valid_move(piece, 0, 1, 0)
    assert result == True


def test_clear_lines():
    game = tetris.Tetris(4, 6)  # Маленькая сетка для теста

    lines = game.clear_lines()
    assert lines == 0

    game.grid[2] = [tetris.RED, tetris.RED, tetris.RED, tetris.RED]
    lines = game.clear_lines()
    assert lines == 1
    assert game.grid[2] == [0, 0, 0, 0]


def test_lock_piece():
    game = tetris.Tetris(10, 20)

    simple_shape = [
        ["O....", ".....", ".....", ".....", "....."],
        [".....", ".....", ".....", ".....", "....."]
    ]
    simple_piece = tetris.Tetromino(5, 5, simple_shape)
    simple_piece.color = tetris.BLUE
    simple_piece.rotation = 0

    with patch.object(game, 'clear_lines', return_value=2):
        with patch.object(game, 'new_piece') as mock_new_piece:
            next_piece = tetris.Tetromino(5, 0, tetris.SHAPES[1])
            mock_new_piece.return_value = next_piece

            with patch.object(game, 'valid_move', return_value=True):
                lines = game.lock_piece(simple_piece)

                assert lines == 2
                assert game.score == 200
                mock_new_piece.assert_called_once()

                assert game.grid[5][5] == tetris.BLUE  # Простая фигура 1x1


@pytest.mark.parametrize("full_rows, expected", [
    (0, 0),  # Нет полных линий
    (1, 1),  # Одна полная линия
    (2, 2),  # Две полные линии
    (3, 3),  # Три полные линии
])
def test_clear_lines_parametrized(full_rows, expected):
    game = tetris.Tetris(4, 10)

    for i in range(full_rows):
        game.grid[i] = [tetris.RED for _ in range(4)]

    lines = game.clear_lines()
    assert lines == expected

@pytest.mark.parametrize("shape_index, piece_x, piece_y, move_x, move_y, rotation, expected", [
    (0, 5, 0, 0, 1, 0, True),  # Движение вниз из центра
    (0, 6, 0, 1, 0, 0, False),  # Движение вправо за границу
    (0, 0, 18, 0, 1, 0, False),  # Движение вниз за границу (y=18 + форма)

    # Фигура T
    (1, 5, 0, 0, 1, 0, True),
])
def test_valid_move_parametrized(shape_index, piece_x, piece_y, move_x, move_y, rotation, expected):
    game = tetris.Tetris(10, 20)
    piece = tetris.Tetromino(piece_x, piece_y, tetris.SHAPES[shape_index])

    result = game.valid_move(piece, move_x, move_y, rotation)
    assert result == expected


def test_update():
    game = tetris.Tetris(10, 20)
    game.game_over = False

    old_y = game.current_piece.y

    with patch.object(game, 'valid_move', return_value=True):
        game.update()
        assert game.current_piece.y == old_y + 1

    with patch.object(game, 'valid_move', return_value=False):
        with patch.object(game, 'lock_piece') as mock_lock:
            game.update()
            mock_lock.assert_called_once()

def test_lock_piece_game_over():
    game = tetris.Tetris(10, 20)

    with patch.object(game, 'clear_lines', return_value=0):
        with patch.object(game, 'new_piece') as mock_new_piece:
            new_piece = tetris.Tetromino(5, 0, tetris.SHAPES[0])
            mock_new_piece.return_value = new_piece

            with patch.object(game, 'valid_move', return_value=False):
                game.lock_piece(game.current_piece)
                assert game.game_over == True


def test_draw_score():
    screen = MagicMock()

    with patch('pygame.font.Font') as mock_font:
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance

        mock_text = MagicMock()
        mock_font_instance.render.return_value = mock_text

        tetris.draw_score(screen, 1500, 10, 20)

        mock_font.assert_called_once_with(None, 36)
        mock_font_instance.render.assert_called_once_with("Score: 1500", True, tetris.WHITE)
        screen.blit.assert_called_once_with(mock_text, (10, 20))


def test_draw_game_over():
    screen = MagicMock()

    with patch('pygame.font.Font') as mock_font:
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance

        mock_text = MagicMock()
        mock_font_instance.render.return_value = mock_text

        tetris.draw_game_over(screen, 100, 200)

        mock_font.assert_called_once_with(None, 48)
        mock_font_instance.render.assert_called_once_with("Game Over", True, tetris.RED)
        screen.blit.assert_called_once_with(mock_text, (100, 200))


def test_tetromino_init():
    shape = tetris.SHAPES[0]

    with patch('random.choice') as mock_choice:
        mock_choice.return_value = tetris.RED

        piece = tetris.Tetromino(3, 5, shape)

        assert piece.x == 3
        assert piece.y == 5
        assert piece.shape == shape
        assert piece.color == tetris.RED
        assert piece.rotation == 0


@pytest.fixture(autouse=True)
def mock_pygame():
    with patch('pygame.init'):
        with patch('pygame.display.set_mode'):
            with patch('pygame.time.Clock'):
                yield


if __name__ == "__main__":
    pytest.main([__file__, "-v"])