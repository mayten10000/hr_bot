from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from config import Config, load_config
from database.queries import add_job 

import logging
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_categories_keyboard, get_checking_job_form_keyboard
from filters.filters import IsAdmin

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format
)

class JobForm(StatesGroup):
    waiting_for_job_category = State()
    waiting_for_job_title = State()
    waiting_for_job_description = State()
    waiting_for_job_requirements = State()
    waiting_for_job_optionals = State()
    waiting_for_job_salary = State()
    
router = Router()

@router.message(Command(commands='cancel'), StateFilter(default_state), IsAdmin())
async def process_cancel_command_in_ds(message: Message):
    await message.answer('no_cancel')

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_out_ds(message: Message, state: FSMContext):
    await message.answer('yes_cancel')
    await state.clear()

@router.callback_query(StateFilter(default_state), F.data.in_({"add_job", "is_not_correct_job_form"}), IsAdmin())
async def process_add_job_form(callback: CallbackQuery, state: FSMContext):
    await callback.answer('job_form_settings')

    await callback.message.edit_text('category:', reply_markup=get_categories_keyboard(hr_mod=True))
    await state.set_state(JobForm.waiting_for_job_category)

@router.callback_query(StateFilter(JobForm.waiting_for_job_category))
async def process_add_job_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(job_category=callback.data.split('_')[-1])

    await callback.answer()
    await callback.message.answer('title: ')
    await state.set_state(JobForm.waiting_for_job_title)
    
@router.message(StateFilter(JobForm.waiting_for_job_title))#, F.text.func(lambda text:  10 <= len(text) <= 50))
async def process_add_job_tittle(message: Message, state: FSMContext):
    await state.update_data(job_title=message.text)
    
    await message.answer('description: ')
    await state.set_state(JobForm.waiting_for_job_description)
    
@router.message(StateFilter(JobForm.waiting_for_job_description))#, F.text.func(lambda text:  100 <= len(text) <= 500))
async def process_add_job_description(message: Message, state: FSMContext):
    await state.update_data(job_description=message.text)
    
    await message.answer('requirements: ')
    await state.set_state(JobForm.waiting_for_job_requirements)
    
@router.message(StateFilter(JobForm.waiting_for_job_requirements))#, F.text.func(lambda text:  150 <= len(text) <= 300))
async def process_add_job_requirements(message: Message, state: FSMContext):
    await state.update_data(job_requirements=message.text)
    
    await message.answer('optionals: ')
    await state.set_state(JobForm.waiting_for_job_optionals)
    
@router.message(StateFilter(JobForm.waiting_for_job_optionals))#, F.text.func(lambda text:  150 <= len(text) <= 300))
async def process_add_job_optionals(message: Message, state: FSMContext):
    await state.update_data(job_optionals=message.text)
    
    await message.answer('salary: ')
    await state.set_state(JobForm.waiting_for_job_salary)
    
@router.message(StateFilter(JobForm.waiting_for_job_salary))
async def process_add_job_optionals(message: Message, state: FSMContext):
    await state.update_data(job_salary=message.text)
    
    data = await state.get_data()
    #add_job(*data)

    fields = 'Job Form\n' + '\n'.join([f"{k}: {v}" for k, v in data.items()])
    await message.answer(fields)
    await message.answer("checking_job_form", reply_markup=get_checking_job_form_keyboard())

@router.callback_query(F.data == 'is_correct_job_form')
async def process_finish_add_job_form(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    add_job(
        job_category=data['job_category'],
        job_title=data['job_title'],
        job_description=data['job_description'],
        job_requirements=data['job_requirements'],
        job_optionals=data['job_optionals'],
        job_salary=data['job_salary']
    )
    
    logging.info(f"Job added ({data})")
    await callback.answer("job_added")

    await state.clear()
    
@router.callback_query(F.data == 'is_not_correct_job_form')
async def process_wrong_job_form(callback: CallbackQuery, state: FSMContext):
    await callback.answer('new_try_job_form')

    await state.clear()
    await process_add_job_form(callback, state)