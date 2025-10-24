def convert_to_2d(matrix_data):
    """
    Преобразует матрицу из одномерного массива с разделителем ';' 
    в двумерный список (list[list[float]])
    """
    matrix_2d = []
    current_row = []
    
    for item in matrix_data:
        if item == ';':
            if current_row:  # Добавляем строку только если она не пустая
                matrix_2d.append(current_row)
                current_row = []
        else:
            current_row.append(float(item))
    
    # Добавляем последнюю строку, если она есть
    if current_row:
        matrix_2d.append(current_row)
    
    return matrix_2d

def format_number(x):
    """Форматирует число: выводит целую часть если число целое, иначе 2 знака после запятой"""
    if x == int(x):
        return str(int(x))
    else:
        return f"{x:.2f}".rstrip('0').rstrip('.')