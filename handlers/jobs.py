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
    await message.answer("Выберите вакансию", reply_markup=job_keyboard(jobs))


@router.callback_query(F.data == "add_job")
async def add_job(callback: CallbackQuery):
    

@router.callback_query(F.data == "delete_job")
async def delete_job(callback: CallbackQuery):
    jobs = get_all_jobs()
    # ...
@router.message(Command("jobs"))
async def test_jobs(message: types.Message):
    await message.answer("Тест: сработала команда /jobs")
