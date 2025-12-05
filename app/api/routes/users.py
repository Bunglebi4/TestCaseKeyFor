from typing import Annotated

from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.params import Parameter
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User
from app.domain.services import UserService
from app.schemas import UserCreate, UserResponse, UserUpdate


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(db_session)


class UserController(Controller):
    path = "/users"
    tags = ["users"]
    dependencies = {"user_service": Provide(provide_user_service)}
    
    @post(
        "/",
        status_code=HTTP_201_CREATED,
        summary="Create a new user",
    )
    async def create_user(
        self,
        user_service: UserService,
        data: UserCreate,
    ) -> UserResponse:
        user = await user_service.create_user(data)
        return UserResponse(
            id=user.id,
            name=user.name,
            surname=user.surname,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    
    @get(
        "/",
        summary="Get list of users",
    )
    async def list_users(
        self,
        user_service: UserService,
        limit: Annotated[int, Parameter(ge=1, le=100)] = 100,
        offset: Annotated[int, Parameter(ge=0)] = 0,
    ) -> list[UserResponse]:
        users = await user_service.list_users(limit=limit, offset=offset)
        return [
            UserResponse(
                id=user.id,
                name=user.name,
                surname=user.surname,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users
        ]
    
    @get(
        "/{user_id:int}",
        summary="Get user by ID",
    )
    async def get_user(
        self,
        user_service: UserService,
        user_id: int,
    ) -> UserResponse:
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTP_404_NOT_FOUND
        
        return UserResponse(
            id=user.id,
            name=user.name,
            surname=user.surname,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    
    @put(
        "/{user_id:int}",
        summary="Update user",
    )
    async def update_user(
        self,
        user_service: UserService,
        user_id: int,
        data: UserUpdate,
    ) -> UserResponse:
        user = await user_service.update_user(user_id, data)
        if not user:
            raise HTTP_404_NOT_FOUND
        
        return UserResponse(
            id=user.id,
            name=user.name,
            surname=user.surname,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    
    @delete(
        "/{user_id:int}",
        status_code=HTTP_204_NO_CONTENT,
        summary="Delete user",
    )
    async def delete_user(
        self,
        user_service: UserService,
        user_id: int,
    ) -> None:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTP_404_NOT_FOUND
