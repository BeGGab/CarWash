import uuid
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession



async def created_carwash(session: AsyncSession, data: SCarwashCreate) -> 