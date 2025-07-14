import asyncio
from gc import callbacks

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from rank_bm25 import BM25Okapi
import re
import numpy as np
from aiogram import Router, F, Dispatcher
from aiogram.types import CallbackQuery, Message

from pymorphy2 import MorphAnalyzer

from database.queries import get_all_full_jobs, get_job_details
from keyboards.inline import job_keyboard_by_id

router = Router()
morph = MorphAnalyzer()

def tokenize_v1(text):
    return text.lower().split()

def tokenize_v2(text):
    parse_text =  re.findall(r'\b\w+\b', text.lower())
    return [morph.parse(token)[0].normal_form for token in parse_text]

def prepare_tokenize_corpus():
    documents = [f"{v[0]} {v[1]} {v[2]} {v[3]} {v[4]}" for v in get_all_full_jobs()]
    return [tokenize_v2(doc) for doc in documents]

def get_tokenize_query(query):
    return tokenize_v2(query)

async def get_similarity_scores(message: Message, state: FSMContext, query):
    def compute():
        bm25 = BM25Okapi(prepare_tokenize_corpus())
        scores = bm25.get_scores(get_tokenize_query(query))
        if np.max(scores) > 0.0:
            normalized_scores = scores / np.max(scores)
        else:
            normalized_scores = scores
        related_scores = {i: normalized_scores[i] for i in range(len(scores))}
        return list(filter(lambda x: x[1] != 0.0, sorted(related_scores.items(), reverse=True, key=lambda x: x[1])))

    res = await asyncio.to_thread(compute)

    print(res)
    jobs_id = [job[0] + 1 for job in res]
    jobs = [get_job_details(ID) for ID in jobs_id]
    key = StorageKey(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        user_id=message.from_user.id
    )
    storage = state.storage
    await storage.set_data(key, {"jobs": jobs, "ids": jobs_id})
    await message.answer("job_choice", reply_markup=await job_keyboard_by_id(jobs, jobs_id, page=0))


