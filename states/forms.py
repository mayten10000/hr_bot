from aiogram.fsm.state import StatesGroup, State


class JobForm(StatesGroup):
    waiting_for_job_title = State()
    waiting_for_job_description = State()
    waiting_for_job_requirements = State()
    waiting_for_job_optionals = State()
    waiting_for_job_salary = State()

class ApplicationState(StatesGroup):
    # Состояния для подачи заявки
    job_selection = State()      # Выбор вакансии
    skills_selection = State()   # Выбор навыков
    name = State()              # Ввод имени (добавлено недостающее состояние)
    phone = State()             # Ввод телефона
    confirmation = State()      # Подтверждение