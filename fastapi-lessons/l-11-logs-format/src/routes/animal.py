from fastapi import APIRouter

import logging

logger = logging.getLogger(__name__)

logger.debug("debug message (on routes import)")
logger.info("info message (on routes import)")
logger.warning("warning message (on routes import)")
logger.error("error message (on routes import)")
logger.critical("critical message (on routes import)")

router = APIRouter()

animals = [
    {
        'title': 'котик'
    },
    {
        'title': 'австралийский динго'
    }
]


@router.get('/list')
async def get_animals_list():
    return animals


@router.get('/{animal_position}')
async def get_animal(animal_position: int):
    return animals[animal_position]
