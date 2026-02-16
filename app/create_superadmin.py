import asyncio
from app.database import async_session
from app.auth.services.user import create_user
from app.auth.models.user import UserRole


async def main():

    async with async_session() as db:

        await create_user(
            db=db,
            username="super",
            password="1234",
            email="admin@email.com",
            role=UserRole.SUPERADMIN
        )


asyncio.run(main())