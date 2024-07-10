from functools import lru_cache

from fastapi import Depends

from core.cache import get_cache_service
from core.enum import IndexName
from core.service import CommonService
from core.storage import get_storage_service
from models.person import Person


@lru_cache()
def get_person_service(
    cache=Depends(get_cache_service),
    elastic=Depends(get_storage_service),
) -> CommonService:
    return CommonService(
        cache=cache,
        elastic=elastic,
        model=Person,
        index=IndexName.persons,
    )
