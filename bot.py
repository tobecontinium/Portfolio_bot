import logging
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import confirmation_keyboard, admin_keyboard, direction_keyboard

from config import dp, bot, ADMIN_ID, CHANNEL_ID

logging.basicConfig(level=logging.INFO)


applications = {}


class Form(StatesGroup):
    name = State()
    age = State()
    direction = State()
    teacher = State()
    portfolio_name = State()
    portfolio_image = State()
    technologies = State()
    link = State()
    confirm = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.reply("Ism va familiyangizni kiriting:👱")


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    await message.reply("Yoshingizni kiriting:🎂")


@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    if not age.isdigit() or not (5 <= int(age) <= 100):
        await message.reply("Iltimos, haqiqiy yoshingizni kiriting. Misol: 25")
        return
    async with state.proxy() as data:
        data['age'] = age
    await Form.next()
    await message.reply("Yo'nalishni tanlang:🪧", reply_markup=direction_keyboard())


@dp.callback_query_handler(lambda c: c.data.startswith('direction_'), state=Form.direction)
async def process_direction(callback_query: types.CallbackQuery, state: FSMContext):
    direction = callback_query.data.split('_')[1]
    async with state.proxy() as data:
        data['direction'] = direction
    await Form.next()
    await callback_query.message.reply("O'qituvchi ismini kiriting:📧", reply_markup=types.ReplyKeyboardRemove())
    await callback_query.answer()


@dp.message_handler(state=Form.teacher)
async def process_teacher(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['teacher'] = message.text
    await Form.next()
    await message.reply("Portfolio nomini kiriting:💼")


@dp.message_handler(state=Form.portfolio_name)
async def process_portfolio_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['portfolio_name'] = message.text
    await Form.next()
    await message.reply("Portfolio rasmini yuklang:🖼")


@dp.message_handler(content_types=['photo'], state=Form.portfolio_image)
async def process_portfolio_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['portfolio_image'] = message.photo[-1].file_id
        logging.info(f"Image file_id saved: {data['portfolio_image']}")  # Логирование file_id
    await Form.next()
    await message.reply("Ishlatilgan texnologiyalar ro'yxatini kiriting:🪧")


@dp.message_handler(state=Form.technologies)
async def process_technologies(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['technologies'] = message.text
    await Form.next()
    await message.reply(
        "Agar portfolio uchun havola (link) bo'lsa, kiriting yoki o'tkazib yuborish uchun /skip buyrug'ini bosing:")


@dp.message_handler(commands='skip', state=Form.link)
async def skip_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = 'Havola yoq'
    await Form.next()
    await confirm_data(message, state)


@dp.message_handler(state=Form.link)
async def process_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = message.text
    await Form.next()
    await confirm_data(message, state)


async def confirm_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        confirmation_text = (f"Quyidagi ma'lumotlar kiritildi:\n"
                             f"🧑 Ism va familiya: {data['name']}\n"
                             f"👨‍🦳 Yoshi: {data['age']}\n"
                             f"🪧 Yo'nalish: {data['direction']}\n"
                             f"👨‍🏫 O'qituvchi: {data['teacher']}\n"
                             f"💼 Portfolio nomi: {data['portfolio_name']}\n"
                             f"📱 Texnologiyalar: {data['technologies']}\n"
                             f"🔗 Havola: {data['link']}\n")

        portfolio_image = data.get('portfolio_image', None)

        if portfolio_image:
            try:
                # Send the uploaded image first
                await bot.send_photo(chat_id=message.chat.id, photo=portfolio_image, caption=confirmation_text,
                                     reply_markup=confirmation_keyboard())
            except Exception as e:
                logging.error(f"Error sending image to user: {e}")
                await message.reply("Rasm yuklanmagan.")

        # await message.reply(confirmation_text, reply_markup=confirmation_keyboard())
        await Form.confirm.set()


@dp.callback_query_handler(lambda c: c.data in ['correct', 'incorrect'], state=Form.confirm)
async def process_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback_query.data == 'correct':
            applications[callback_query.from_user.id] = data.as_dict()
            #
            confirmation_text = (f"Quyidagi ma'lumotlar kiritildi:\n"
                                 f"🧑 Ism va familiya: {data['name']}\n"
                                 f"👨‍🦳 Yoshi: {data['age']}\n"
                                 f"🪧 Yo'nalish: {data['direction']}\n"
                                 f"👨‍🏫 O'qituvchi: {data['teacher']}\n"
                                 f"💼 Portfolio nomi: {data['portfolio_name']}\n"
                                 f"📱 Texnologiyalar: {data['technologies']}\n"
                                 f"🔗 Havola: {data['link']}\n")
            #
            # await callback_query.message.answer(confirmation_text)
            #
            portfolio_image = data.get('portfolio_image', None)
            # if portfolio_image:
            #     try:
            #         await bot.send_photo(chat_id=callback_query.from_user.id, photo=portfolio_image,
            #                              caption="Siz yuklagan rasm:")
            #     except Exception as e:
            #         logging.error(f"Error sending image to user: {e}")
            # else:
            #     await callback_query.message.answer("Rasm yuklanmagan.")

            await callback_query.message.answer("Ma'lumotlaringiz qabul qilindi va adminlarga yuborildi.🗃")

            await bot.send_photo(chat_id=ADMIN_ID, photo=portfolio_image, caption=confirmation_text,
                                 reply_markup=admin_keyboard(callback_query.from_user.id))
            await state.finish()
        else:
            await callback_query.message.answer(
                "Iltimos, ma'lumotlarni qayta kiriting. Ism va familiyangizni kiriting.♻️")
            await Form.name.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('admin_'))
async def process_admin_action(callback_query: types.CallbackQuery):
    try:
        action, user_id = callback_query.data.split('_')[1:]
        user_id = int(user_id)
        user_data = applications.get(user_id, {})
        logging.info(f"Admin action data: {user_data}")

        if not user_data:
            await callback_query.answer("Foydalanuvchi ma'lumotlari topilmadi.")
            return

        admin_text = f"""#{user_data['direction']} 

{user_data['portfolio_name']}

💻 Foydalanilgan texnologiyalar: {user_data['technologies'].upper()}

O'quvchi ismi: {user_data['name'].title()}
Yoshi: {user_data['age']}
Mentor: {user_data['teacher']}

Link: {user_data.get('link', 'Havola yoq')}

⭕️ MARS IT SCHOOL
📞 78 777 77 57
📍 Manzil: Toshkent shahar
        """

        portfolio_image = user_data.get('portfolio_image', None)

        if action == 'approve':
            if portfolio_image:
                await bot.send_photo(chat_id=CHANNEL_ID, photo=portfolio_image, caption=admin_text)
                await callback_query.message.edit_text(
                    "Portfolio muvaffaqiyatli tasdiqlandi va kanalda e'lon qilindi.✅")
            else:
                await callback_query.message.edit_text("Rasmlar yuklanmagan. Iltimos, qayta urinib ko'ring.❌")
        elif action == 'reject':
            await bot.send_message(chat_id=user_id, text="Portfolio rad etildi. Iltimos, qayta urinib ko'ring.❌")
            await callback_query.message.edit_text("Portfolio rad etildi.❌")
    except Exception as e:
        logging.error(f"Error processing admin action: {e}")
        await callback_query.answer("Foydalanuvchi ma'lumotlarini qayta ko'rib chiqing.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
