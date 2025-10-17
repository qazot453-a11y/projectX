from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from app.keyboards import get_main_keyboard, get_size_keyboard, get_matrices_list_keyboard
from app.convert import convert_to_2d
# Импортируем из корневой папки
from functions import matrix_det

router = Router()

# Глобальный словарь для хранения матриц
user_matrices = {}

class MatrixStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_size = State()
    waiting_for_rows = State()

@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "🤖 Добро пожаловать в калькулятор матриц!\n\n"
        "Возможности бота:\n"
        "• Создание и хранение матриц\n"
        "• Вычисление детерминанта\n"
        "• Визуализация матриц\n\n"
        "Для начала работы нажмите кнопку ниже 👇",
        reply_markup=get_main_keyboard(has_matrices=len(user_matrices) > 0)
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
    if not user_matrices:
        await message.answer("Нет сохраненных матриц.")
        return
    
    await message.answer(
        "Выберите матрицу для отображения:",
        reply_markup=get_matrices_list_keyboard(user_matrices, "show")
    )

@router.message(F.text == "🧮 Вычислить детерминант")
async def process_determinant(message: Message):
    if not user_matrices:
        await message.answer("Нет сохраненных матриц.")
        return
    
    await message.answer(
        "Выберите матрицу для вычисления детерминанта:",
        reply_markup=get_matrices_list_keyboard(user_matrices, "det")
    )

@router.message(MatrixStates.waiting_for_name)
async def process_matrix_name(message: Message, state: FSMContext):
    matrix_name = message.text.strip()
    
    await state.update_data(matrix_name=matrix_name)
    await state.set_state(MatrixStates.waiting_for_size)
    await message.answer(
        "Выберите размер матрицы:",
        reply_markup=get_size_keyboard()
    )

@router.callback_query(F.data.startswith("size_"), MatrixStates.waiting_for_size)
async def process_size_selection(callback: CallbackQuery, state: FSMContext):
    size_data = callback.data.split('_')
    rows = int(size_data[1])
    cols = int(size_data[2])
    
    await state.update_data(
        rows=rows,
        cols=cols,
        current_row=0,
        matrix_data=[]
    )
    await state.set_state(MatrixStates.waiting_for_rows)
    
    await callback.message.answer(
        f"Выбран размер: {rows}x{cols}\n"
        f"Введите {rows} строк(у/и) матрицы.\n"
        f"Введите 1 строку (числа через пробел):"
    )
    await callback.answer()

@router.message(MatrixStates.waiting_for_rows)
async def process_row_input(message: Message, state: FSMContext):
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
            # Ограничение на 10 матриц
            if len(user_matrices) >= 10:
                # Удаляем самую старую матрицу
                oldest_key = next(iter(user_matrices))
                del user_matrices[oldest_key]
            
            user_matrices[matrix_name] = matrix_data
            
            await message.answer(
                f"✅ Матрица '{matrix_name}' успешно сохранена!",
                reply_markup=get_main_keyboard(has_matrices=len(user_matrices) > 0)
            )
            await state.clear()
            
    except ValueError:
        await message.answer("Ошибка! Введите числа через пробел:")

@router.callback_query(F.data.startswith("show_"))
async def process_matrix_display(callback: CallbackQuery):
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