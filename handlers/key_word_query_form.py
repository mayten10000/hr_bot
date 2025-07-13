from idlelib.window import add_windows_to_menu
from pkgutil import get_data

from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from services.search import get_similarity_scores

router = Router()

class QueryForm(StatesGroup):
    waiting_for_query = State()

@router.callback_query(F.data == 'call_bm25', StateFilter(default_state))
async def get_key_word_query(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("enter_key_words")

    await state.set_state(QueryForm.waiting_for_query)

@router.message(StateFilter(QueryForm.waiting_for_query))
async def handle_key_word_query(message: Message, state: FSMContext):
    query = message.text.strip()

    if not query:
        await message.answer('empty_query_error')
        return

    await get_similarity_scores(message, query)
    await state.clear()