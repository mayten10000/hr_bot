from aiogram import Router

from handlers.apply import router as router_apply
from handlers.candidates import router as router_candidates
from handlers.jobs import router as router_jobs
from handlers.start import router as router_start
from handlers.job_form import router as router_job_form

main_router = Router()

main_router.include_router(router_apply)
main_router.include_router(router_candidates)
main_router.include_router(router_jobs)
main_router.include_router(router_start)
main_router.include_router(router_job_form)

__all__ = ["main_router"]