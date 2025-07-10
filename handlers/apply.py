from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.queries import get_job_details, add_candidate
from keyboards.inline import skills_keyboard
from states.forms import ApplicationState

router = Router()

@router.callback_query(F.data.startswith("apply_"))
async def apply(callback: CallbackQuery, state: FSMContext):
    job_id = int(callback.data.split("_")[1])
    job = get_job_details(job_id)
    # ...
