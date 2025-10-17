from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from app.keyboards import get_main_keyboard, get_size_keyboard, get_matrices_list_keyboard, get_delete_matrices_keyboard
from app.convert import convert_to_2d
from functions import matrix_det

router = Router()

# Глобальный словарь для хранения матриц всех пользователей
# Структура: {user_id: {matrix_name: matrix_data}}
user_databases = {}

class MatrixStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_size = State()
    waiting_for_rows = State()
    waiting_for_manual_size = State()  # Новое состояние для ручного ввода размера

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

@router.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    await message.answer(
        f"🤖 Добро пожаловать в калькулятор матриц, {message.from_user.first_name}!\n\n"
        "Возможности бота:\n"
        "• Создание и хранение матриц\n"
        "• Вычисление детерминанта\n"
        "• Визуализация матриц\n"
        "• Удаление матриц\n\n"
        f"Ваш ID: {user_id}\n"
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

@router.message(F.text == "🧮 Вычислить детерминант")
async def process_determinant(message: Message):
    user_id = message.from_user.id
    user_matrices = get_user_matrices(user_id)
    
    if not user_matrices:
        await message.answer("У вас нет сохраненных матриц.")
        return
    
    await message.answer(
        "Выберите матрицу для вычисления детерминанта:",
        reply_markup=get_matrices_list_keyboard(user_matrices, "det")
    )

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
    matrix_str = f"Матрица '{matrix_name}':\n"
    for row in matrix_2d:
        matrix_str += "│ " + " ".join(f"{x:8.2f}" for x in row) + " │\n"
    
    await callback.message.answer(f"<pre>{matrix_str}</pre>", parse_mode='HTML')
    await callback.answer()

@router.callback_query(F.data.startswith("det_"))
async def process_determinant_calculation(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_matrices = get_user_matrices(user_id)
    matrix_name = callback.data.split('_')[1]
    
    if matrix_name not in user_matrices:
        await callback.answer("Матрица не найдена!")
        return
    
    matrix_data = user_matrices[matrix_name]
    
    try:
        # Преобразуем в двумерный вид
        matrix_2d = convert_to_2d(matrix_data)
        
        # Проверяем, что матрица квадратная
        if len(matrix_2d) != len(matrix_2d[0]):
            await callback.message.answer(
                f"❌ Матрица '{matrix_name}' не является квадратной! "
                f"Размер: {len(matrix_2d)}x{len(matrix_2d[0])}\n"
                f"Детерминант можно вычислить только для квадратных матриц."
            )
            await callback.answer()
            return
        
        # Вычисляем детерминант
        determinant = matrix_det(matrix_2d)
        
        # Форматируем вывод матрицы
        matrix_str = f"Матрица '{matrix_name}':\n"
        for row in matrix_2d:
            matrix_str += "│ " + " ".join(f"{x:8.2f}" for x in row) + " │\n"
        
        # Отправляем результат
        await callback.message.answer(
            f"<pre>{matrix_str}</pre>\n"
            f"🔢 Детерминант матрицы '{matrix_name}':\n"
            f"<b>det = {determinant:.6f}</b>",
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при вычислении детерминанта матрицы '{matrix_name}': {str(e)}"
        )
    
    await callback.answer()