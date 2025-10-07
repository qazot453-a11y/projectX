#умножение квадратной матрицы на число
def mq_prodnum():
    try:
        n = int(input('Какого порядка матрица?\n'))
    except ValueError:
        print('Некорректное число')
        
    matrix = list(int(a) for a in input('Элементы матрицы (в строчку, ' \
    'через пробел, сначала элементы первой строки, потом второй и т.д)\n').split())
    
    if len(matrix) **0.5 != n:
        exit('Количество элементов не соответствует порядку')
        ### <Назад> или <Попытаться снова> ####
    
    else:
        try:
            mnozh = float(input('На какое число домножить:\n'))
            new_matrix = []
            while matrix: ##делим список из символов на строки матрицы по порядку
                new_matrix.append(matrix[:n])
                del matrix[:n]
            
        
            k = len(new_matrix)
            for i in range(k): ##перемножаем элементы матрицы на число и заносим в список
                str_new = list()
                for a in new_matrix[i]:
                    str_new.append(a * mnozh)
                new_matrix.append(str_new)
            
            for i in range(n): ##удаляем старую матрицу из списка
                del new_matrix[0]
            
            print(*new_matrix, sep='\n') ##вывод строк матрицы в стобец (имитация матрицы без 
                                         ##корректного расположения элементов, с обозначением списка)

        except ValueError: #не пропускает не число (например, "1 0")
            print('Множитель задан некорректно')
 
mq_prodnum()