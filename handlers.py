from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal
from models import User, Lesson
from config import ADMIN_ID
import calendar
from datetime import datetime
from my_calendar import create_calendar_with_slots, get_free_slots


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = update.message.from_user

    db = SessionLocal()

    try:
        # Проверяем, есть ли пользователь в базе
        db_user = db.query(User).filter_by(telegram_id=user_data.id).first()
        if not db_user:
            db_user = User(
                telegram_id=user_data.id,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
            )
            db.add(db_user)
            db.commit()

        # Отправляем разные клавиатуры для админа и обычного пользователя
        if user_data.id == ADMIN_ID:
            text = "Добро пожаловать, Админ! Выберите одну из опций:"
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Посмотреть мои записи", callback_data="viewLesson"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Посмотреть пользователей", callback_data="viewUsers"
                    )
                ],
            ]
        else:
            text = "Добро пожаловать! Выберите одну из опций:"
            keyboard = [
                [InlineKeyboardButton("Записаться", callback_data="signUp")],
                [InlineKeyboardButton("Мои записи", callback_data="myLesson")],
                [InlineKeyboardButton("FAQ", callback_data="info")],
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

    finally:
        db.close()


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    user_id = query.from_user.id

    try:
        if query.data == "signUp":
            # Проверяем, есть ли у пользователя уроки
            lessons_exist = db.query(Lesson).filter_by(user_id=user_id).first()

            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Записаться", callback_data="subscribe")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back")],
                ],
            )

            if lessons_exist:
                await query.edit_message_text(
                    text="У вас уже есть запись на урок!", reply_markup=keyboard
                )
            else:
                await query.edit_message_text(
                    text=f"{query.from_user.username}, вы впервые здесь!Предлагаем записаться на вводный урок!",
                    reply_markup=keyboard,
                )

        elif query.data == "subscribe":
            free_slot = get_free_slots()
            calendar = create_calendar_with_slots(free_slot)
            await query.edit_message_text(
                text="Выберите день для записи:", reply_markup=calendar
            )

        elif query.data.startswith("day_"):
            # Пользователь выбрал день
            selected_day = int(query.data.split("_")[1])
            context.user_data["selected_day"] = selected_day

            # Создаем клавиатуру для выбора времени
            time_slots = ["10:00", "12:00", "14:00", "16:00"]  # Пример временных слотов
            keyboard = [
                [
                    InlineKeyboardButton(time, callback_data=f"time_{time}")
                    for time in time_slots
                ]
            ]
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])

            await query.edit_message_text(
                text=f"Вы выбрали {selected_day}. Теперь выберите время:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif query.data.startswith("time_"):
            # Пользователь выбрал время
            selected_time = query.data.split("_")[1]
            selected_day = context.user_data.get("selected_day", "не выбран")

            # Сохраняем выбранное время
            context.user_data["selected_time"] = selected_time

            await query.edit_message_text(
                text=f"Вы выбрали {selected_day} день, время: {selected_time}. Подтвердите ваш выбор.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Подтвердить", callback_data="confirm")],
                        [InlineKeyboardButton("⬅️ Назад", callback_data="back")],
                    ]
                ),
            )
        elif query.data == "confirm":
            # Подтверждаем выбор
            day = context.user_data.get("selected_day", "не выбран")
            time = context.user_data.get("selected_time", "не выбран")
            time_str = f"{day} {time}"
            start_time = datetime.strptime(time_str, "%d %H:%M").strftime("%H:%M")

            # Сохраняем запись в базе
            lesson = Lesson(
                user_id=user_id, subject="Анлгийский", start_time=start_time
            )  # Пример формата записи
            db.add(lesson)
            db.commit()

            await query.edit_message_text(
                text=f"Вы успешно записались на {day} число в {time}!",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
                ),
            )

        elif query.data == "myLesson":
            user_lessons = db.query(Lesson).filter_by(user_id=user_id).all()

            if user_lessons:
                lessons_text = "\n".join(
                    [
                        f"{lesson.subject} в {lesson.start_time.strftime('%H:%M')}"
                        for lesson in user_lessons
                    ]
                )
                await query.edit_message_text(text=f"Ваши уроки:\n{lessons_text}")
            else:
                await query.edit_message_text(text="У вас пока нет записей.")

        elif query.data == "info":
            await query.edit_message_text(
                text="Информация о боте: как пользоваться, зачем он нужен и прочее."
            )

        elif query.data == "viewLesson" and user_id == ADMIN_ID:
            # Логика для просмотра всех уроков (для админа) — сделаем позже
            await query.edit_message_text(
                text="(Админ) Здесь будет список всех уроков."
            )

        elif query.data == "viewUsers" and user_id == ADMIN_ID:
            # Логика для просмотра всех пользователей (для админа) — сделаем позже
            await query.edit_message_text(
                text="(Админ) Здесь будет список всех пользователей."
            )
        elif query.data == "back":
            # Вернуть пользователя в главное меню
            if user_id == ADMIN_ID:
                text = "Добро пожаловать, Админ! Выберите одну из опций:"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Посмотреть мои записи", callback_data="viewLesson"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Посмотреть пользователей", callback_data="viewUsers"
                        )
                    ],
                ]
            else:
                text = "Добро пожаловать! Выберите одну из опций:"
                keyboard = [
                    [InlineKeyboardButton("Записаться", callback_data="signUp")],
                    [InlineKeyboardButton("Мои записи", callback_data="myLesson")],
                    [InlineKeyboardButton("FAQ", callback_data="info")],
                ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup)

        else:
            await query.edit_message_text(text="Неизвестная команда.")
    finally:
        db.close()


def create_calendar():
    # Получаем текущую дату
    now = datetime.now()
    month_days = calendar.monthcalendar(now.year, now.month)

    # Создаем клавиатуру для календаря
    keyboard = []
    for week in month_days:
        row = []
        for day in week:
            if day != 0:
                # Добавляем кнопку с номером дня
                row.append(InlineKeyboardButton(str(day), callback_data=f"day_{day}"))
            else:
                row.append(InlineKeyboardButton(" ", callback_data="empty"))
        keyboard.append(row)

    # Добавляем кнопку "Назад"
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])

    return InlineKeyboardMarkup(keyboard)
