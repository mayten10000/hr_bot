from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.queries import get_job_details, add_candidate, get_job_skills
from keyboards.inline import skills_keyboard
from states.forms import ApplicationState

router = Router()

@router.callback_query(F.data.startswith("apply_"))
async def apply_for_job(callback: CallbackQuery, state: FSMContext):
    try:
        job_id = int(callback.data.split("_")[1])
        job = get_job_details(job_id)

        if not job:
            await callback.answer("Вакансия не найдена", show_alert=True)
            return

        await state.update_data(
            job_id=job_id,
            job_title=job[0],
            job_description=job[1],
            job_salary=job[2]
        )

        required_skills = get_job_skills(job_id)

        if not required_skills:
            await callback.message.answer("Для этой вакансии не указаны требуемые навыки")
            await state.set_state(ApplicationState.name)
            await callback.message.answer("Введите ваше имя:")
            return
        await state.set_state(ApplicationState.skills_selection)
        await callback.message.answer(
            "Отметьте ваши навыки:\n"
            "✅ - владею\n"
            "❌ - не владею",
            reply_markup=skills_keyboard(required_skills)
        )
        await callback.answer()
    except Exception as e:
        await callback.answer("Произошла ошибка, попробуйте позже", show_alert=True)
        print(f"Error in apply_for_job: {e}")


@router.callback_query(F.data.startswith("skill_"), ApplicationState.skills_selection)
async def process_skill_selection(callback: CallbackQuery, state: FSMContext):
    try:
        _, skill, choice = callback.data.split("_")
        user_data = await state.get_data()
        score = user_data.get("score", 0)
        skills = user_data.get("skills", {})
        skills[skill] = (choice == "yes")
        await state.update_data(skills=skills)

        await callback.answer(f"Навык {skill} {'добавлен' if choice == 'yes' else 'отмечен как отсутствующий'}")
        if choice == 'yes':
            score += 1
            await state.update_data(score=score)
        await callback.answer(f"Совпадений по навыкам {score}")
    except Exception as e:
        await callback.answer("Ошибка при сохранении навыка", show_alert=True)
        print(f"Error in process_skill_selection: {e}")


@router.callback_query(F.data == "submit_skills", ApplicationState.skills_selection)
async def finish_skills_selection(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ApplicationState.name)
    await callback.message.answer("Введите ваше имя:")
    await callback.answer()


@router.message(ApplicationState.name)
async def process_name(message: Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer("Пожалуйста, введите корректное имя")
        return

    await state.update_data(name=message.text.strip())
    await message.answer("Теперь введите ваш номер телефона:")
    await state.set_state(ApplicationState.phone)


@router.message(ApplicationState.phone)
async def process_phone(message: Message, state: FSMContext):

    phone = message.text.strip()
    cleaned_phone = ''.join(c for c in phone if c.isdigit())
    if len(cleaned_phone) < 5:
        await message.answer("Пожалуйста, введите корректный номер телефона (минимум 5 цифр)")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()

    confirmed_skills = [skill for skill, has in data.get('skills', {}).items() if has]

    confirmation_text = (
        f"Проверьте ваши данные:\n\n"
        f"🔹 Вакансия: {data['job_title']}\n"
        f"🔹 Имя: {data['name']}\n"
        f"🔹 Телефон: {data['phone']}\n"
        f"🔹 Навыки: {', '.join(confirmed_skills) if confirmed_skills else 'Нет подтвержденных навыков'}"
    )

    await message.answer(confirmation_text)
    await message.answer("Все верно? (да/нет)")
    await state.set_state(ApplicationState.confirmation)


@router.message(ApplicationState.confirmation)
async def process_confirmation(message: Message, state: FSMContext):
    response = message.text.strip().lower()

    if response == 'да':
        data = await state.get_data()

        add_candidate(
            name=data['name'],
            job_id=data['job_id'],
            phone=data['phone'],
            skills=data['skills'],
            match_score=data['score']
        )

        await message.answer("✅ Ваша заявка принята! Спасибо за участие.")
        await state.clear()
    else:
        await message.answer("Давайте начнем заново. Введите ваше имя:")
        await state.set_state(ApplicationState.name)