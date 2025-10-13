#TODO: 
# Ввод матриц - complete✅
# Детерминант - complete✅
# Вычитание - complete✅
# Сложение - in process❌
# Союзная матрица - complete✅
# Обратная матрица - in process❌
# Умножение на число - in process❌
# Создание единичной матрицы любого порядка - in process❌
# Создание нуль матрицы - in process❌
# Красивый вывод - complete (FIXME: найти, что выводит None в конце) ✅❌


def input_square_matrix():
    """"Ввод матрицы n-го порядка"""    
    n = int(input("Введите порядок матрицы: "))
    
    print(f"Введите элементы матрицы {n}x{n} построчно:")
    matrix = []
    
    for i in range(n):
        row = list(map(float, input(f"Строка {i+1}: ").split()))
        if len(row) != n:
            raise ValueError(f"Ожидается {n} элементов в строке, получено {len(row)}")
        matrix.append(row)
    
    return matrix


def input_matrix_simple():
    """Ввод прямоугольной матрицы"""
    rows = int(input("Строки: "))
    cols = int(input("Столбцы: "))
    
    print(f"Введите {rows} строк по {cols} чисел:")
    matrix = []
    
    for i in range(rows):
        while True:
            try:
                row = list(map(float, input().split()))
                if len(row) == cols:
                    matrix.append(row)
                    break
                print(f"Нужно {cols} чисел, получено {len(row)}")
            except ValueError:
                print("Только числа!")
    
    return matrix


def det_matrix(matrix: list) -> float:
    """
    Вычисляет детерминант матрицы любого порядка
    
    Аргументы: matrix - матрица в виде списка списков
    
    Возвращает: float - значение детерминанта матрицы
    """
    # Проверка, что матрица квадратная
    n = len(matrix)
    for row in matrix:
        if len(row) != n:
            raise ValueError("Детерминант бывает только у квадратной матрицы😢")
    
    # Базовые случаи для матриц малого порядка
    if n == 1:
        return matrix[0][0]
    
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    
    if n == 3:
        # Правило треугольника(Саррюса) для матрицы 3x3
        return (matrix[0][0] * matrix[1][1] * matrix[2][2] +
                matrix[0][1] * matrix[1][2] * matrix[2][0] +
                matrix[0][2] * matrix[1][0] * matrix[2][1] -
                matrix[0][2] * matrix[1][1] * matrix[2][0] -
                matrix[0][1] * matrix[1][0] * matrix[2][2] -
                matrix[0][0] * matrix[1][2] * matrix[2][1])
    
    # Вычисление для матриц большего порядка
    determinant = 0
    # Разложение по первой строке
    for j in range(n):
        # Создаем минор - матрица без первой строки и j-го столбца
        minor = []
        for i in range(1, n):
            row = []
            for k in range(n):
                if k != j:
                    row.append(matrix[i][k])
            minor.append(row)
        
        # Рекурсивно вычисляем определитель минора
        minor_det = det_matrix(minor)
        
        # Добавляем к общей сумме с учетом знака
        sign = 1 if j % 2 == 0 else -1
        determinant += sign * matrix[0][j] * minor_det
    
    return determinant


def matrix_subtraction(matrix1, matrix2):
    """Вычитание матриц
    Аргументы: matrix1, matrix2 - матрицы(первая минус вторая)
    Возвращает: матрицу-результат вычитания
    """
    if len(matrix1) != len(matrix2) or len(matrix1[0]) != len(matrix2[0]):
        raise ValueError("Размерности матриц не совпадают")
    
    return [[matrix1[i][j] - matrix2[i][j] for j in range(len(matrix1[0]))] 
            for i in range(len(matrix1))]


def algebraic_complement_matrix_compact(matrix):
    """Нахождение союзной матрицы(понадобится для нахождения обратной)
    Аргументы: matrix - матрица, для которой будет найдена союзная
    Возвращает: союзную матрицу
    """
    
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Матрица должна быть квадратной")
    
    def minor_det(mat, excl_row, excl_col):
        """Определитель минора"""
        minor = [row[:excl_col] + row[excl_col+1:] 
                for i, row in enumerate(mat) if i != excl_row]
        return det_matrix(minor)
    
    print("Алгебраическое дополнение введенной матрицы:", end='')
    return [[(1 if (i+j)%2==0 else -1) * minor_det(matrix, i, j) 
            for j in range(n)] for i in range(n)]


def print_matrix(matrix, title="Матрица"):
    """
    Красивый вывод матрицы
    
    Аргументы: matrix: матрица для вывода, title: заголовок
    """
    if not matrix:
        print("Матрица пуста")
        return
    
    print(f"\n{title} {len(matrix)}x{len(matrix[0])}:")
    print("─" * (len(matrix[0]) * 10))
    
    for row in matrix:
        # Форматируем числа для красивого вывода
        formatted_row = [f"{x:8.3f}" if isinstance(x, float) else f"{x:8}" for x in row]
        print(" ".join(formatted_row))
    
    print("─" * (len(matrix[0]) * 10))

# Некоторые тесты:

# print(f"Determinant = {det_matrix(input_matrix())}")
# print(f"Determinant = {print_matrix(matrix_subtraction(input_square_matrix(), input_square_matrix()))}")
# print(print_matrix(algebraic_complement_matrix_compact(input_square_matrix())))
# print(print_matrix(input_matrix_simple()))