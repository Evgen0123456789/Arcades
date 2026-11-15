
def create_board():
    return [[' ' for _ in range(3)] for _ in range(3)]


def render(board):
    print()
    for i, row in enumerate(board):
        print(' ' + ' | '.join(row))
        if i < 2:
            print('---+---+---')
    print()


def check_winner(board):
    # Проверяем строки
    for row in board:
        if row[0] == row[1] == row[2] != ' ':
            return row[0]

    # Проверяем столбцы
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != ' ':
            return board[0][col]

    # Проверяем диагонали
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]

    return None


def main():
    board = create_board()
    current_player = 'X'
    moves = 0

    while True:
        render(board)

        print(f"Ход игрока {current_player}")

        try:
            row = int(input("Строка (1-3): ")) - 1
            col = int(input("Столбец (1-3): ")) - 1
        except ValueError:
            print("Введите целые числа!")
            continue

        # Проверяем координаты
        if not (0 <= row < 3 and 0 <= col < 3):
            print("Координаты вне поля!")
            continue

        # Проверяем, свободна ли клетка
        if board[row][col] != ' ':
            print("Эта клетка уже занята!")
            continue

        # Делаем ход
        board[row][col] = current_player
        moves += 1

        # Проверяем победу
        winner = check_winner(board)

        if winner:
            render(board)
            print(f"Победил игрок {winner}!")
            break

        # Проверяем ничью
        if moves == 9:
            render(board)
            print("Ничья!")
            break

        # Передаём ход
        current_player = 'O' if current_player == 'X' else 'X'


if __name__ == '__main__':
    main()
