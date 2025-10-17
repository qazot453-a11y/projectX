from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(has_matrices=False):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить новую матрицу")]
        ],
        resize_keyboard=True
    )
    
    if has_matrices:
        keyboard.keyboard.append([KeyboardButton(text="📊 Вывести матрицу")])
    
    return keyboard

def get_size_keyboard():
    # Создаем список строк для клавиатуры
    keyboard_lines = []
    
    # Создаем кнопки 10x10
    buttons = []
    for i in range(1, 11):
        row_buttons = []
        for j in range(1, 11):
            row_buttons.append(InlineKeyboardButton(
                text=f"{i}x{j}", 
                callback_data=f"size_{i}_{j}"
            ))
        keyboard_lines.append(row_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_lines)

def get_matrices_list_keyboard(matrices_dict):
    # Создаем кнопки для каждой матрицы
    buttons = []
    for name in matrices_dict.keys():
        buttons.append([InlineKeyboardButton(
            text=name, 
            callback_data=f"show_{name}"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)