from fastapi import Depends, HTTPException, status
from app.auth.models.user import UserDB
from app.auth.core.dependencies import get_current_user


class RequireRoles:
    def __init__(self, *allowed_roles: str):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: UserDB = Depends(get_current_user)
    ) -> UserDB:

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes"
            )

        return current_user