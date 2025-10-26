from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(has_matrices=False):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить новую матрицу")]
        ],
        resize_keyboard=True
    )
    
    if has_matrices:
        keyboard.keyboard.extend([
            [KeyboardButton(text="📊 Вывести матрицу")],
            [KeyboardButton(text="🧮 Операции с матрицами")]
        ])
    
    return keyboard

def get_operations_keyboard():
    """Клавиатура с операциями над матрицами"""
    keyboard_lines = [
        [InlineKeyboardButton(text="🔢 Детерминант", callback_data="op_det"),
         InlineKeyboardButton(text="📈 Ранг матрицы", callback_data="op_rank")],
        [InlineKeyboardButton(text="✖️ Умножить на скаляр", callback_data="op_scalar"),
         InlineKeyboardButton(text="❓ Сингулярность", callback_data="op_singular")],
        [InlineKeyboardButton(text="➕ Сложение", callback_data="op_add"),
         InlineKeyboardButton(text="➖ Вычитание", callback_data="op_sub")],
        [InlineKeyboardButton(text="✖️ Умножение матриц", callback_data="op_multiply")],
        [InlineKeyboardButton(text="🔄 Транспонирование", callback_data="op_transpose"),
         InlineKeyboardButton(text="🔄 Обратная матрица", callback_data="op_inverse")],
        [InlineKeyboardButton(text="📐 Алг. дополнение", callback_data="op_complement")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="op_back")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_lines)

def get_size_keyboard():
    # Создаем список строк для клавиатуры 5x5
    keyboard_lines = []
    
    # Создаем кнопки от 1x1 до 5x5
    for i in range(1, 6):
        row_buttons = []
        for j in range(1, 6):
            row_buttons.append(InlineKeyboardButton(
                text=f"{i}x{j}", 
                callback_data=f"size_{i}_{j}"
            ))
        keyboard_lines.append(row_buttons)
    
    # Добавляем кнопку ручного ввода
    keyboard_lines.append([InlineKeyboardButton(
        text="⌨️ Ввести размер вручную", 
        callback_data="manual_size"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_lines)

def get_matrices_list_keyboard(matrices_dict, action="show", selected_matrix=None):
    """
    action: тип операции
    selected_matrix: уже выбранная матрица (для операций с двумя матрицами)
    """
    # Создаем кнопки для каждой матрицы
    buttons = []
    for name in matrices_dict.keys():
        if selected_matrix == name:
            # Помечаем уже выбранную матрицу
            text = f"✅ {name}"
        else:
            text = name
        buttons.append([InlineKeyboardButton(
            text=text, 
            callback_data=f"{action}_{name}"
        )])
    
    # Добавляем кнопку отмены
    buttons.append([InlineKeyboardButton(
        text="🔙 Отмена", 
        callback_data="operation_cancel"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_save_matrix_keyboard():
    """Клавиатура для сохранения результата операции"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="💾 Сохранить результат", 
            callback_data="save_result"
        )
    ]])

def get_delete_matrices_keyboard(matrices_dict):
    """Клавиатура для удаления матриц"""
    buttons = []
    for name in matrices_dict.keys():
        buttons.append([InlineKeyboardButton(
            text=f"❌ {name}", 
            callback_data=f"delete_{name}"
        )])
    
    # Добавляем кнопку отмены
    buttons.append([InlineKeyboardButton(
        text="🔙 Отмена", 
        callback_data="delete_cancel"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)