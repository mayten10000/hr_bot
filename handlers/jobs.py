from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.queries import get_all_jobs, delete_job
from keyboards.inline import job_keyboard, admin_keyboard, delete_job_keyboard
from aiogram.filters import Command
from states.JobForm import process_add_job_form
from config import Config, load_config
import logging

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format
)

router = Router()

@router.message(Command("jobs"))
async def list_jobs(message: types.Message):
    jobs = get_all_jobs()
    await message.answer("Выберите вакансию", reply_markup=job_keyboard(jobs))

@router.callback_query(F.data == "add_job")  
async def delete_job_handler(callback: types.CallbackQuery, state: FSMContext):
    await process_add_job_form(callback.message, state)
    await callback.answer()  
    
@router.callback_query(F.data == "delete_job")
async def delete_job_callback(callback: CallbackQuery):
    jobs = get_all_jobs()
    del_keyboard = delete_job_keyboard(jobs)
    await callback.message.edit_text('jobs_for_deleting: ', reply_markup=del_keyboard)
    await callback.answer()
    
@router.callback_query(F.data.startswith("delete_"))
async def process_delete_job(callback: CallbackQuery):
    logging.info(f"process_delete_job is started (data={callback})")
    job_id = callback.data.split("_")[-1]
    delete_job(job_id)
    logging.info(f"Job (id={job_id} deleted")
    
    jobs = get_all_jobs()
    new_del_keyboard = delete_job_keyboard(jobs)
    await callback.message.edit_text(
        text="jobs_for_deleting",
        reply_markup=new_del_keyboard
    )

@router.message(Command("jobs"))
async def test_jobs(message: types.Message):
    await message.answer("Тест: сработала команда /jobs")
