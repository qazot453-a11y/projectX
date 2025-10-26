from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from app.keyboards import (
    get_main_keyboard, get_size_keyboard, get_matrices_list_keyboard, 
    get_delete_matrices_keyboard, get_operations_keyboard, get_save_matrix_keyboard
)
from app.convert import convert_to_2d, format_number
from functions import (
    matrix_det, matrix_multiply_by_scalar, matrix_subtraction, matrix_add,
    matrix_is_singular, matrix_transpose, matrix_algebraic_complement, matrix_inverse,
    matrix_multiply, matrix_rank
)
import re

router = Router()

# Глобальный словарь для хранения матриц всех пользователей
user_databases = {}

# Временное хранилище для операций с двумя матрицами
operation_storage = {}

class MatrixStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_size = State()
    waiting_for_rows = State()
    waiting_for_manual_size = State()
    waiting_for_operation = State()
    waiting_for_scalar = State()
    waiting_for_first_matrix = State()
    waiting_for_second_matrix = State()
    waiting_for_save_name = State()

def get_user_matrices(user_id):
    """Получает словарь матриц пользователя, создает если нет"""
    if user_id not in user_databases:
        user_databases[user_id] = {}
    return user_databases[user_id]

def save_user_matrix(user_id, matrix_name, matrix_data):
    """Сохраняет матрицу пользователя с ограничением в 10 матриц"""
    user_matrices = get_user_matrices(user_id)
    
    # Ограничение на 10 матриц
    if len(user_matrices) >= 10:
        # Удаляем самую старую матрицу
        oldest_key = next(iter(user_matrices))
        del user_matrices[oldest_key]
    
    user_matrices[matrix_name] = matrix_data
    return user_matrices

def format_matrix_output(matrix_2d, name="Результат"):
    """Форматирует матрицу для вывода с красивым форматированием чисел"""
    matrix_str = f"<b>Матрица '{name}':</b>\n"
    matrix_str += "<pre>"
    
    # Находим максимальную ширину элемента для выравнивания
    max_width = 0
    for row in matrix_2d:
        for element in row:
            formatted = format_number(element)
            max_width = max(max_width, len(formatted))
    
    # Форматируем каждую строку
    for row in matrix_2d:
        formatted_row = []
        for element in row:
            formatted_element = format_number(element)
            # Выравниваем по правому краю
            formatted_row.append(formatted_element.rjust(max_width))
        
        matrix_str += "│ " + " ".join(formatted_row) + " │\n"
    
    matrix_str += "</pre>"
    return matrix_str

def convert_to_storage_format(matrix_2d):
    """Конвертирует двумерную матрицу в формат хранения"""
    storage_data = []
    for row in matrix_2d:
        storage_data.extend(row)
        storage_data.append(';')
    return storage_data

def sanitize_matrix_name(name):
    """Очищает имя матрицы от недопустимых символов"""
    # Заменяем пробелы и специальные символы на подчеркивания
    sanitized = re.sub(r'[^\w]', '_', name)
    # Убираем множественные подчеркивания
    sanitized = re.sub(r'_+', '_', sanitized)
    # Убираем подчеркивания в начале и конце
    sanitized = sanitized.strip('_')
    return sanitized

# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    await message.answer(
        f"🤖 Добро пожаловать в калькулятор матриц, {message.from_user.first_name}!\n\n"
        "Возможности бота:\n"
        "• Создание и хранение матриц\n"
        "• Все основные операции с матрицами\n"
        "• Визуализация матриц\n"
        "• Удаление матриц\n\n"
        f"Сохранено матриц: {len(user_matrices)}/10\n\n"
        "Доступные команды:\n"
        "/start - начать работу\n"
        "/my_matrices - показать все матрицы\n"
        "/delete_matrix - удалить матрицу\n\n"
        "Для начала работы нажмите кнопку ниже 👇",
        reply_markup=get_main_keyboard(has_matrices=len(user_matrices) > 0)
    )

@router.message(Command("my_matrices"))
async def show_my_matrices(message: Message):
    """Команда для просмотра статистики по матрицам пользователя"""
    user_id = message.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    if not user_matrices:
        await message.answer("У вас нет сохраненных матриц.")
        return
    
    matrices_list = "📊 Ваши матрицы:\n\n"
    for i, (name, data) in enumerate(user_matrices.items(), 1):
        matrix_2d = convert_to_2d(data)
        rows = len(matrix_2d)
        cols = len(matrix_2d[0]) if matrix_2d else 0
        matrices_list += f"{i}. {name} - размер: {rows}x{cols}\n"
    
    matrices_list += f"\nВсего матриц: {len(user_matrices)}/10"
    await message.answer(matrices_list)

@router.message(Command("delete_matrix"))
async def delete_matrix_command(message: Message):
    """Команда для удаления матриц"""
    user_id = message.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    if not user_matrices:
        await message.answer("У вас нет сохраненных матриц для удаления.")
        return
    
    await message.answer(
        "Выберите матрицу для удаления:",
        reply_markup=get_delete_matrices_keyboard(user_matrices)
    )

@router.message(F.text == "➕ Добавить новую матрицу")
async def process_add_matrix(message: Message, state: FSMContext):
    await state.set_state(MatrixStates.waiting_for_name)
    await message.answer(
        "Введите название для новой матрицы:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text == "📊 Вывести матрицу")
async def process_show_matrix(message: Message):
    user_id = message.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    if not user_matrices:
        await message.answer("У вас нет сохраненных матриц.")
        return
    
    await message.answer(
        "Выберите матрицу для отображения:",
        reply_markup=get_matrices_list_keyboard(user_matrices, "show")
    )

@router.message(F.text == "🧮 Операции с матрицами")
async def show_operations(message: Message):
    user_id = message.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    if not user_matrices:
        await message.answer("У вас нет сохраненных матриц.")
        return
    
    await message.answer(
        "Выберите операцию:",
        reply_markup=get_operations_keyboard()
    )

# Обработчики операций
@router.callback_query(F.data.startswith("op_"))
async def process_operation_selection(callback: CallbackQuery, state: FSMContext):
    operation = callback.data.replace("op_", "")
    user_id = callback.from_user.id
    
    if operation == "back":
        await callback.message.answer(
            "Главное меню:",
            reply_markup=get_main_keyboard(has_matrices=len(get_user_matrices(user_id)) > 0)
        )
        await callback.answer()
        return
    
    await state.update_data(current_operation=operation)
    
    if operation in ["add", "sub", "multiply"]:
        # Операции с двумя матрицами
        await state.set_state(MatrixStates.waiting_for_first_matrix)
        operation_names = {
            "add": "Сложение",
            "sub": "Вычитание", 
            "multiply": "Умножение матриц"
        }
        await callback.message.answer(
            f"Выбрана операция: {operation_names[operation]}\n"
            "Выберите первую матрицу:",
            reply_markup=get_matrices_list_keyboard(get_user_matrices(user_id), "select_first")
        )
    elif operation == "scalar":
        # Умножение на скаляр
        await state.set_state(MatrixStates.waiting_for_first_matrix)
        await callback.message.answer(
            "Выбрана операция: Умножение на скаляр\n"
            "Выберите матрицу:",
            reply_markup=get_matrices_list_keyboard(get_user_matrices(user_id), "select_scalar")
        )
    else:
        # Операции с одной матрицей
        await state.set_state(MatrixStates.waiting_for_first_matrix)
        operation_names = {
            "det": "Детерминант",
            "transpose": "Транспонирование",
            "inverse": "Обратная матрица",
            "complement": "Алгебраическое дополнение",
            "singular": "Проверка на сингулярность",
            "rank": "Ранг матрицы"
        }
        await callback.message.answer(
            f"Выбрана операция: {operation_names[operation]}\n"
            "Выберите матрицу:",
            reply_markup=get_matrices_list_keyboard(get_user_matrices(user_id), "select_single")
        )
    
    await callback.answer()

# Обработчики выбора матриц для операций
@router.callback_query(F.data.startswith("select_first_"), MatrixStates.waiting_for_first_matrix)
async def process_first_matrix_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    matrix_name = callback.data.replace("select_first_", "")
    user_matrices = get_user_matrices(user_id)
    
    if matrix_name not in user_matrices:
        await callback.answer("Матрица не найдена!")
        return
    
    # Сохраняем первую матрицу
    operation_storage[user_id] = {
        "first_matrix": matrix_name,
        "first_matrix_data": user_matrices[matrix_name]
    }
    
    await state.set_state(MatrixStates.waiting_for_second_matrix)
    
    user_data = await state.get_data()
    operation = user_data.get("current_operation")
    operation_names = {
        "add": "сложения",
        "sub": "вычитания",
        "multiply": "умножения"
    }
    
    await callback.message.answer(
        f"Выбрана матрица: {matrix_name}\n"
        f"Выберите вторую матрицу для {operation_names[operation]}:",
        reply_markup=get_matrices_list_keyboard(user_matrices, "select_second", matrix_name)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("select_second_"), MatrixStates.waiting_for_second_matrix)
async def process_second_matrix_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    matrix_name = callback.data.replace("select_second_", "")
    user_data = await state.get_data()
    operation = user_data.get("current_operation")
    user_matrices = get_user_matrices(user_id)
    
    if matrix_name not in user_matrices:
        await callback.answer("Матрица не найдена!")
        return
    
    # Получаем данные обеих матриц
    first_matrix_name = operation_storage[user_id]["first_matrix"]
    first_matrix_data = operation_storage[user_id]["first_matrix_data"]
    second_matrix_data = user_matrices[matrix_name]
    
    # Выполняем операцию
    try:
        matrix1_2d = convert_to_2d(first_matrix_data)
        matrix2_2d = convert_to_2d(second_matrix_data)
        
        if operation == "add":
            result = matrix_add(matrix1_2d, matrix2_2d)
            result_name = f"Сумма_{first_matrix_name}_{matrix_name}"
        elif operation == "sub":
            result = matrix_subtraction(matrix1_2d, matrix2_2d)
            result_name = f"Разность_{first_matrix_name}_{matrix_name}"
        elif operation == "multiply":
            result = matrix_multiply(matrix1_2d, matrix2_2d)
            result_name = f"Произведение_{first_matrix_name}_{matrix_name}"
        
        # Форматируем результат
        result_str = format_matrix_output(result, result_name)
        
        # Сохраняем результат для возможного сохранения
        operation_storage[user_id]["result"] = result
        operation_storage[user_id]["result_name"] = result_name
        
        await callback.message.answer(
            result_str,
            parse_mode='HTML',
            reply_markup=get_save_matrix_keyboard()
        )
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при выполнении операции: {str(e)}")
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("select_single_"), MatrixStates.waiting_for_first_matrix)
async def process_single_matrix_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    matrix_name = callback.data.replace("select_single_", "")
    user_data = await state.get_data()
    operation = user_data.get("current_operation")
    user_matrices = get_user_matrices(user_id)
    
    if matrix_name not in user_matrices:
        await callback.answer("Матрица не найдена!")
        return
    
    matrix_data = user_matrices[matrix_name]
    
    try:
        matrix_2d = convert_to_2d(matrix_data)
        
        if operation == "det":
            if len(matrix_2d) != len(matrix_2d[0]):
                await callback.message.answer("❌ Матрица должна быть квадратной для вычисления детерминанта!")
                await state.clear()
                return
            
            result = matrix_det(matrix_2d)
            await callback.message.answer(
                f"🔢 Детерминант матрицы '{matrix_name}':\n"
                f"<b>det = {format_number(result)}</b>",
                parse_mode='HTML'
            )
            
        elif operation == "rank":
            result = matrix_rank(matrix_2d)
            await callback.message.answer(
                f"📈 Ранг матрицы '{matrix_name}':\n"
                f"<b>rank = {result}</b>",
                parse_mode='HTML'
            )
            
        elif operation == "transpose":
            result = matrix_transpose(matrix_2d)
            result_str = format_matrix_output(result, f"Транспонированная_{matrix_name}")
            
            # Сохраняем результат для возможного сохранения
            operation_storage[user_id] = {
                "result": result,
                "result_name": f"Транспонированная_{matrix_name}"
            }
            
            await callback.message.answer(
                result_str,
                parse_mode='HTML',
                reply_markup=get_save_matrix_keyboard()
            )
            
        elif operation == "inverse":
            result = matrix_inverse(matrix_2d)
            result_str = format_matrix_output(result, f"Обратная_{matrix_name}")
            
            operation_storage[user_id] = {
                "result": result,
                "result_name": f"Обратная_{matrix_name}"
            }
            
            await callback.message.answer(
                result_str,
                parse_mode='HTML',
                reply_markup=get_save_matrix_keyboard()
            )
            
        elif operation == "complement":
            result = matrix_algebraic_complement(matrix_2d)
            result_str = format_matrix_output(result, f"Алгебраическое_дополнение_{matrix_name}")
            
            operation_storage[user_id] = {
                "result": result,
                "result_name": f"Алгебраическое_дополнение_{matrix_name}"
            }
            
            await callback.message.answer(
                result_str,
                parse_mode='HTML',
                reply_markup=get_save_matrix_keyboard()
            )
            
        elif operation == "singular":
            is_singular = matrix_is_singular(matrix_2d)
            status = "сингулярна" if is_singular else "не сингулярна"
            await callback.message.answer(
                f"🔍 Матрица '{matrix_name}' {status}"
            )
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при выполнении операции: {str(e)}")
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data.startswith("select_scalar_"), MatrixStates.waiting_for_first_matrix)
async def process_scalar_matrix_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    matrix_name = callback.data.replace("select_scalar_", "")
    user_matrices = get_user_matrices(user_id)
    
    if matrix_name not in user_matrices:
        await callback.answer("Матрица не найдена!")
        return
    
    # Сохраняем выбранную матрицу
    operation_storage[user_id] = {
        "matrix_name": matrix_name,
        "matrix_data": user_matrices[matrix_name]
    }
    
    await state.set_state(MatrixStates.waiting_for_scalar)
    await callback.message.answer(
        f"Выбрана матрица: {matrix_name}\n"
        "Введите скаляр (число) для умножения:"
    )
    await callback.answer()

@router.message(MatrixStates.waiting_for_scalar)
async def process_scalar_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    try:
        scalar = float(message.text)
        
        matrix_name = operation_storage[user_id]["matrix_name"]
        matrix_data = operation_storage[user_id]["matrix_data"]
        
        matrix_2d = convert_to_2d(matrix_data)
        result = matrix_multiply_by_scalar(matrix_2d, scalar)
        result_name = f"Умноженная_на_{format_number(scalar)}_{matrix_name}"
        
        result_str = format_matrix_output(result, result_name)
        
        # Сохраняем результат для возможного сохранения
        operation_storage[user_id]["result"] = result
        operation_storage[user_id]["result_name"] = result_name
        
        await message.answer(
            result_str,
            parse_mode='HTML',
            reply_markup=get_save_matrix_keyboard()
        )
        
    except ValueError:
        await message.answer("❌ Ошибка! Введите корректное число.")
        return
    
    await state.clear()

# Обработчик сохранения результата
@router.callback_query(F.data == "save_result")
async def process_save_request(callback: CallbackQuery, state: FSMContext):
    """Обработчик запроса на сохранение результата"""
    user_id = callback.from_user.id
    
    if user_id not in operation_storage or "result" not in operation_storage[user_id]:
        await callback.answer("Результат не найден!")
        return
    
    await state.set_state(MatrixStates.waiting_for_save_name)
    await callback.message.answer(
        "Введите название для сохранения результата:"
    )
    await callback.answer()

@router.message(MatrixStates.waiting_for_save_name)
async def process_save_name_input(message: Message, state: FSMContext):
    """Обработчик ввода имени для сохранения результата"""
    user_id = message.from_user.id
    matrix_name = message.text.strip()
    
    if user_id not in operation_storage or "result" not in operation_storage[user_id]:
        await message.answer("Результат не найден!")
        await state.clear()
        return
    
    # Проверяем, есть ли уже матрица с таким именем
    user_matrices = get_user_matrices(user_id)
    if matrix_name in user_matrices:
        await message.answer(
            f"Матрица с названием '{matrix_name}' уже существует. "
            "Введите другое название:"
        )
        return
    
    # Сохраняем матрицу
    result = operation_storage[user_id]["result"]
    storage_data = convert_to_storage_format(result)
    
    save_user_matrix(user_id, matrix_name, storage_data)
    user_matrices = get_user_matrices(user_id)
    
    await message.answer(
        f"✅ Матрица '{matrix_name}' успешно сохранена!\n"
        f"Всего матриц: {len(user_matrices)}/10",
        reply_markup=get_main_keyboard(has_matrices=len(user_matrices) > 0)
    )
    
    # Очищаем временное хранилище
    if user_id in operation_storage:
        del operation_storage[user_id]
    
    await state.clear()

# Обработчик отмены операций
@router.callback_query(F.data == "operation_cancel")
async def process_operation_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Операция отменена.")
    await callback.answer()

@router.callback_query(F.data == "delete_cancel")
async def process_delete_cancel(callback: CallbackQuery):
    await callback.message.answer("Удаление отменено.")
    await callback.answer()

# ... (остальные обработчики остаются без изменений)

@router.message(MatrixStates.waiting_for_name)
async def process_matrix_name(message: Message, state: FSMContext):
    matrix_name = message.text.strip()
    user_id = message.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    # Проверяем, есть ли уже матрица с таким именем
    if matrix_name in user_matrices:
        await message.answer(
            f"Матрица с названием '{matrix_name}' уже существует. "
            "Введите другое название:"
        )
        return
    
    await state.update_data(matrix_name=matrix_name)
    await state.set_state(MatrixStates.waiting_for_size)
    await message.answer(
        "Выберите размер матрицы (от 1x1 до 5x5) или введите вручную:",
        reply_markup=get_size_keyboard()
    )

@router.callback_query(F.data.startswith("size_"), MatrixStates.waiting_for_size)
async def process_size_selection(callback: CallbackQuery, state: FSMContext):
    size_data = callback.data.split('_')
    rows = int(size_data[1])
    cols = int(size_data[2])
    
    await set_matrix_size(state, rows, cols)
    await callback.message.answer(
        f"Выбран размер: {rows}x{cols}\n"
        f"Введите {rows} строк(у/и) матрицы.\n"
        f"Введите 1 строку (числа через пробел):"
    )
    await callback.answer()

@router.callback_query(F.data == "manual_size", MatrixStates.waiting_for_size)
async def process_manual_size_request(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MatrixStates.waiting_for_manual_size)
    await callback.message.answer(
        "Введите размер матрицы в формате:\n"
        "<строки> <столбцы>\n\n"
        "Например: 3 4\n"
        "Максимальный размер: 10x10"
    )
    await callback.answer()

@router.message(MatrixStates.waiting_for_manual_size)
async def process_manual_size_input(message: Message, state: FSMContext):
    try:
        # Разбиваем ввод на две части
        parts = message.text.strip().split()
        if len(parts) != 2:
            await message.answer(
                "❌ Неверный формат! Введите два числа через пробел.\n"
                "Например: 3 4"
            )
            return
        
        rows = int(parts[0])
        cols = int(parts[1])
        
        # Проверяем допустимость размеров
        if rows < 1 or cols < 1 or rows > 10 or cols > 10:
            await message.answer(
                "❌ Неверный размер! Строки и столбцы должны быть от 1 до 10.\n"
                "Попробуйте снова:"
            )
            return
        
        await set_matrix_size(state, rows, cols)
        await message.answer(
            f"Выбран размер: {rows}x{cols}\n"
            f"Введите {rows} строк(у/и) матрицы.\n"
            f"Введите 1 строку (числа через пробел):"
        )
        
    except ValueError:
        await message.answer(
            "❌ Ошибка! Введите целые числа.\n"
            "Например: 3 4"
        )

async def set_matrix_size(state: FSMContext, rows: int, cols: int):
    """Устанавливает размер матрицы и переходит к вводу строк"""
    await state.update_data(
        rows=rows,
        cols=cols,
        current_row=0,
        matrix_data=[]
    )
    await state.set_state(MatrixStates.waiting_for_rows)

@router.message(MatrixStates.waiting_for_rows)
async def process_row_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    rows = user_data['rows']
    cols = user_data['cols']
    current_row = user_data['current_row']
    matrix_data = user_data['matrix_data']
    matrix_name = user_data['matrix_name']
    
    try:
        # Преобразуем ввод в числа
        row_elements = list(map(float, message.text.split()))
        
        # Дополняем нулями если нужно
        while len(row_elements) < cols:
            row_elements.append(0.0)
        
        # Обрезаем если слишком много элементов
        row_elements = row_elements[:cols]
        
        matrix_data.extend(row_elements)
        matrix_data.append(';')  # Спецсимвол конца строки
        
        current_row += 1
        
        await state.update_data(
            current_row=current_row,
            matrix_data=matrix_data
        )
        
        if current_row < rows:
            await message.answer(f"Введите {current_row + 1} строку:")
        else:
            # Сохраняем матрицу
            save_user_matrix(user_id, matrix_name, matrix_data)
            user_matrices = get_user_matrices(user_id)
            
            await message.answer(
                f"✅ Матрица '{matrix_name}' успешно сохранена!\n"
                f"Размер: {rows}x{cols}\n"
                f"Всего матриц: {len(user_matrices)}/10",
                reply_markup=get_main_keyboard(has_matrices=len(user_matrices) > 0)
            )
            await state.clear()
            
    except ValueError:
        await message.answer("Ошибка! Введите числа через пробел:")

@router.callback_query(F.data.startswith("show_"))
async def process_matrix_display(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_matrices = get_user_matrices(user_id)
    matrix_name = callback.data.split('_')[1]
    
    if matrix_name not in user_matrices:
        await callback.answer("Матрица не найдена!")
        return
    
    matrix_data = user_matrices[matrix_name]
    
    # Преобразуем в двумерный вид
    matrix_2d = convert_to_2d(matrix_data)
    
    # Форматируем вывод
    matrix_str = format_matrix_output(matrix_2d, matrix_name)
    
    await callback.message.answer(matrix_str, parse_mode='HTML')
    await callback.answer()

@router.callback_query(F.data.startswith("delete_"))
async def process_matrix_deletion(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    if callback.data == "delete_cancel":
        await callback.message.answer("Удаление отменено.")
        await callback.answer()
        return
    
    matrix_name = callback.data.split('_')[1]
    
    if matrix_name not in user_matrices:
        await callback.answer("Матрица не найдена!")
        return
    
    # Удаляем матрицу
    del user_matrices[matrix_name]
    
    await callback.message.answer(
        f"✅ Матрица '{matrix_name}' успешно удалена!\n"
        f"Осталось матриц: {len(user_matrices)}/10",
        reply_markup=get_main_keyboard(has_matrices=len(user_matrices) > 0)
    )
    await callback.answer()