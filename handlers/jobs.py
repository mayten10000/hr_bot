from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.queries import get_all_jobs, delete_job
from keyboards.inline import job_keyboard, admin_keyboard
from states.forms import JobForm
from aiogram.filters import Command

router = Router()

@router.message(Command("jobs"))
async def list_jobs(message: types.Message):
    jobs = get_all_jobs()
    if jobs:
        await message.answer("Выберите вакансию:", reply_markup=job_keyboard(jobs))
    else:
        await message.answer("Нет доступных вакансий")

@router.callback_query(F.data == "add_job")
async def start_adding_job(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название вакансии:")
    await state.set_state(JobForm.title)
    await callback.answer()

@router.callback_query(F.data == "delete_job")
async def start_deleting_job(callback: CallbackQuery, state: FSMContext):
    jobs = get_all_jobs()
    if jobs:
        await callback.message.answer(
            "Выберите вакансию для удаления:",
            reply_markup=job_keyboard(jobs, prefix="delete_")
        )
    else:
        await callback.answer("Нет вакансий для удаления", show_alert=True)
    await callback.answer()