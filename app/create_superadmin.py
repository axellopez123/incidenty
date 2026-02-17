import asyncio
from app.database import SessionLocal
from app.auth.core.dependencies import create_user
from app.auth.models.user import UserDB, UserRole
from app.company.models.company import Company
from app.events.models.event import Event


async def main():

    async with SessionLocal() as db:

        await create_user(
            db=db,
            username="super",
            password="1234",
            email="admin@email.com",
            role=UserRole.SUPERADMIN
        )
        
        


asyncio.run(main())