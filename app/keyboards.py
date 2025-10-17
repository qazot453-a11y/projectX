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
            [KeyboardButton(text="🧮 Вычислить детерминант")]
        ])
    
    return keyboard

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

def get_matrices_list_keyboard(matrices_dict, action="show"):
    """
    action: "show" для показа матрицы, "det" для вычисления детерминанта
    """
    # Создаем кнопки для каждой матрицы
    buttons = []
    for name in matrices_dict.keys():
        buttons.append([InlineKeyboardButton(
            text=name, 
            callback_data=f"{action}_{name}"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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