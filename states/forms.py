from aiogram.fsm.state import StatesGroup, State

class JobForm(StatesGroup):
    waiting_for_job_title = State()
    waiting_for_job_description = State()
    waiting_for_job_requirements = State()
    waiting_for_job_optionals = State()
    waiting_for_job_salary = State()

class ApplicationForm(StatesGroup):
    confirming_skills = State()

class ApplicationState(StatesGroup):
    confirming_skills = State()