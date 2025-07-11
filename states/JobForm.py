from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery

class JobForm(StatesGroup):
    waiting_for_job_title = State()
    waiting_for_job_description = State()
    waiting_for_job_requirements = State()
    waiting_for_job_optionals = State()
    waiting_for_job_salary = State()
    
states_job_form_router = Router()

@states_job_form_router(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command_in_ds(message: Message):
    await message.answer('no_cancel')

@states_job_form_router(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_out_ds(message: Message, state: FSMContext):
    await message.answer('yes_cancel')
    await state.clear()

@states_job_form_router(StateFilter(default_state))
async def process_add_job_form(message: Message, state: FSMContext):
    await message.answer('job_form_settings')
    
    await message.answer('title: ')
    await state.set_state(JobForm.waiting_for_job_title)
    
@states_job_form_router(StateFilter(JobForm.waiting_for_job_title))
async def process_add_job_tittle(message: Message, state: FSMContext):
    await state.update_data(job_title=message.text)
    
    await message.answer('description: ')
    await state.set_state(JobForm.waiting_for_job_description)
    
@states_job_form_router(StateFilter(JobForm.waiting_for_job_description))
async def process_add_job_description(message: Message, state: FSMContext):
    await state.update_data(job_description=message.text)
    
    await message.answer('requirements: ')
    await state.set_state(JobForm.waiting_for_job_requirements)
    
@states_job_form_router(StateFilter(JobForm.waiting_for_job_requirements))
async def process_add_job_requirements(message: Message, state: FSMContext):
    await state.update_data(job_requirements=message.text)
    
    await message.answer('optionals: ')
    await state.set_state(JobForm.waiting_for_job_optionals)
    
@states_job_form_router(StateFilter(JobForm.waiting_for_job_optionals))
async def process_add_job_optionals(message: Message, state: FSMContext):
    await state.update_data(job_optionals=message.text)
    
    await message.answer('salary: ')
    await state.set_state(JobForm.waiting_for_job_salary)
    
@states_job_form_router(StateFilter(JobForm.waiting_for_job_salary))
async def process_add_job_optionals(message: Message, state: FSMContext):
    await state.update_data(job_salary=message.text)
    
    data = await state.get_data()
    
    