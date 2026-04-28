"""
User API routes.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from pheno.adapters.api.dependencies import (
    get_create_user_use_case,
    get_deactivate_user_use_case,
    get_get_user_use_case,
    get_list_users_use_case,
    get_update_user_use_case,
)
from pheno.application.dtos.user import (
    CreateUserDTO,
    UpdateUserDTO,
    UserDTO,
    UserFilterDTO,
)
from pheno.application.use_cases.user import (
    CreateUserUseCase,
    DeactivateUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from pheno.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def create_user(
    dto: CreateUserDTO,
    use_case: Annotated[CreateUserUseCase, Depends(get_create_user_use_case)],
) -> UserDTO:
    """
    Create a new user.
    """
    try:
        return await use_case.execute(dto)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/{user_id}", response_model=UserDTO)
async def get_user(
    user_id: str,
    use_case: Annotated[GetUserUseCase, Depends(get_get_user_use_case)],
) -> UserDTO:
    """
    Get a user by ID.
    """
    try:
        return await use_case.execute(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{user_id}", response_model=UserDTO)
async def update_user(
    user_id: str,
    dto: UpdateUserDTO,
    use_case: Annotated[UpdateUserUseCase, Depends(get_update_user_use_case)],
) -> UserDTO:
    """
    Update a user.
    """
    try:
        # Override user_id from path
        dto = UpdateUserDTO(user_id=user_id, name=dto.name, email=dto.email)
        return await use_case.execute(dto)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    use_case: Annotated[DeactivateUserUseCase, Depends(get_deactivate_user_use_case)],
) -> None:
    """
    Deactivate a user.
    """
    try:
        await use_case.execute(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/", response_model=list[UserDTO])
async def list_users(
    use_case: Annotated[ListUsersUseCase, Depends(get_list_users_use_case)],
    limit: int = 100,
    offset: int = 0,
) -> list[UserDTO]:
    """
    List users with pagination.
    """
    filter_dto = UserFilterDTO(limit=limit, offset=offset)
    return await use_case.execute(filter_dto)
