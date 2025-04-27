from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import SessionLocal
from models import FreeSlot
import calendar


def get_free_slots():
    db = SessionLocal()
    try:
        slots = db.query(FreeSlot).all()
        return slots
    finally:
        db.close()


def create_calendar_with_slots(slots):
    now = datetime.now()
    month_days = calendar.monthcalendar(now.year, now.month)
    keyboard = []

    for week in month_days:
        row = []
        for day in week:
            if day != 0:
                # Проверяем, есть ли свободные слоты для этого дня
                available_slots = [
                    slot.time.strftime("%H:%M")
                    for slot in slots
                    if slot.date.day == day
                ]
                if available_slots:
                    # Если есть слоты, делаем кнопку активной
                    row.append(
                        InlineKeyboardButton(
                            f"{day} ({', '.join(available_slots)})",
                            callback_data=f"day_{day}",
                        )
                    )
                else:
                    # Если нет слотов, делаем кнопку серой и неактивной
                    row.append(
                        InlineKeyboardButton(
                            f"{day} (нет слотов)",
                            callback_data="empty",
                            disabled=True,  # Отключаем кнопку АААААААААААААААААААААА
                        )
                    )
            else:
                # Если день пустой (например, в начале или конце месяца)
                row.append(InlineKeyboardButton(" ", callback_data="empty"))
        keyboard.append(row)

    # Добавляем кнопку "Назад"
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)
