def mult_matrix(matrix: list) -> float:
    """
    Вычисляет детерминант матрицы любого порядка
    
    Args:
        matrix: матрица в виде списка списков
    
    Returns:
        float: значение детерминанта матрицы
    """
    # Проверка, что матрица квадратная
    n = len(matrix)
    for row in matrix:
        if len(row) != n:
            raise ValueError("Матрица должна быть квадратной")
    
    # Базовые случаи для матриц малого порядка
    if n == 1:
        return matrix[0][0]
    
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    
    if n == 3:
        # Правило Саррюса для матрицы 3x3
        return (matrix[0][0] * matrix[1][1] * matrix[2][2] +
                matrix[0][1] * matrix[1][2] * matrix[2][0] +
                matrix[0][2] * matrix[1][0] * matrix[2][1] -
                matrix[0][2] * matrix[1][1] * matrix[2][0] -
                matrix[0][1] * matrix[1][0] * matrix[2][2] -
                matrix[0][0] * matrix[1][2] * matrix[2][1])
    
    # Рекурсивное вычисление для матриц большего порядка
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
        minor_det = mult_matrix(minor)
        
        # Добавляем к общей сумме с учетом знака
        sign = 1 if j % 2 == 0 else -1
        determinant += sign * matrix[0][j] * minor_det
    
    return determinant


def input_matrix():
    n = int(input("Введите порядок матрицы: "))
    
    print(f"Введите элементы матрицы {n}x{n} построчно:")
    matrix = []
    
    for i in range(n):
        row = list(map(float, input(f"Строка {i+1}: ").split()))
        if len(row) != n:
            raise ValueError(f"Ожидается {n} элементов в строке, получено {len(row)}")
        matrix.append(row)
    
    return matrix




print(f"Determinant = {mult_matrix(input_matrix())}")
