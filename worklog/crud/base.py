"""
This module contains the base interface for CRUD 
(Create, Read, Update, Delete) operations.
"""

from typing import Generic, List, Optional, Type, TypeVar

from pydantic import UUID4, BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from worklog.log import get_logger

ORMModelType = TypeVar("ORMModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


log = get_logger(__name__)


class CRUDRepository(Generic[ORMModelType, CreateSchemaType, UpdateSchemaType]):
    """Base interface for CRUD operations."""

    def __init__(self, model: Type[ORMModelType]) -> None:
        """
        Initializes the class with the given ORM model.

        Args:
            model (Type[ORMModelType]): The ORM model to be initialized.
        """

        self._model: Type[ORMModelType] = model
        self._name: str = model.__name__

    async def count(self, session: AsyncSession) -> int:
        """
        Asynchronously counts the number of records in the database.

        Args:
            session (Session): The database session to use.

        Returns:
            int: The number of records in the database.
        """
        log.debug("counting %s", self._name)
        subquery = select(self._model).subquery()
        result = await session.execute(select(func.count()).select_from(subquery))
        return result.scalar().first()

    async def get_one_by_id(
        self, session: AsyncSession, id: str | UUID4
    ) -> ORMModelType | None:
        """
        Asynchronously gets a record by its ID.

        Args:
            session (Session): The database session to use.
            id (str | UUID4): The ID of the record to retrieve.

        Returns:
            Optional[ORMModel]: The retrieved record, or None if not found.
        """
        log.debug("getting %s with id=%s", self._name, id)
        result = await session.execute(select(self._model).filter(self._model.id == id))
        return result.scalars().first()

    async def get_many_by_ids(
        self, session: AsyncSession, ids: List[str | UUID4]
    ) -> List[ORMModelType]:
        """
        Asynchronously gets multiple records by their IDs.

        Args:
            session (Session): The database session to use.
            ids (List[str | UUID4]): The IDs of the records to retrieve.

        Returns:
            List[ORMModel]: A list of retrieved records.
        """

        log.debug("getting %s with ids=%s", self._name, ids)
        result = await session.execute(
            select(self._model).filter(self._model.id.in_(ids))
        )
        return result.scalars().all()

    async def get_one(
        self, session: AsyncSession, *args, **kwargs
    ) -> Optional[ORMModelType]:
        """
        Asynchronously retrieves one ORMModelType using the provided session and optional
        arguments and keyword arguments.

        Args:
            session (Session): The database session to use.
            *args: Variable length argument list used for filtering. For example filter(User.name == 'John')
            **kwargs: Keyword arguments used for filter_by. For example filter_by(name='John')

        Returns:
            Optional[ORMModelType]: The retrieved record, or None if not found.
        """

        log.debug("getting %s with args=%s, kwargs=%s", self._name, args, kwargs)
        result = await session.execute(
            select(self._model).filter(*args).filter_by(**kwargs)
        )
        return result.scalars().first()

    async def get_many(
        self, session: AsyncSession, *args, offset: int = 0, limit: int = 100, **kwargs
    ) -> List[ORMModelType]:
        """
        Asynchronously gets multiple ORMModel objects from the database with optional filtering and limiting.

        Args:
            session (Session): The database session.
            *args: Positional arguments for filtering the query. For example filter(User.name == 'John')
            offset (int, optional): The number of results to skip. Defaults to 0.
            limit (int, optional): The maximum number of results to return. Defaults to 100.
            **kwargs: Keyword arguments for filtering the query. For example filter_by(name='John')

        Returns:
            List[ORMModelType]: A list of ORMModel objects retrieved from the database.
        """
        log.debug("getting all %s with args=%s, kwargs=%s", self._name, args, kwargs)
        result = await session.execute(
            select(self._model)
            .filter(*args)
            .filter_by(**kwargs)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> ORMModelType:
        """
        Asynchronously creates a new ORMModel instance and adds it to the session.

        Args:
            session (Session): The database session.
            obj_in (CreateSchemaType): The input data for creating the ORMModel instance.

        Returns:
            ORMModelType: The newly created ORMModel instance.
        """
        log.debug("creating %s with obj_in=%s", self._name, obj_in)
        obj_in_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
        db_obj = self._model(**obj_in_data)  # type: ignore
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def create_many(
        self, session: AsyncSession, objs_in: List[CreateSchemaType]
    ) -> List[ORMModelType]:
        """
        Asynchronously creates multiple ORMModel instances and adds them to the session.

        Args:
            session (Session): The database session.
            objs_in (List[CreateSchemaType]): The input data for creating the ORMModel instances.

        Returns:
            List[ORMModelType]: A list of newly created ORMModel instances.
        """
        objs_in_data = [
            obj.model_dump(exclude_unset=True, exclude_none=True) for obj in objs_in
        ]
        db_objs = [self._model(**obj_in_data) for obj_in_data in objs_in_data]  # type: ignore
        session.add_all(db_objs)
        await session.commit()
        await session.refresh(db_objs)
        return db_objs

    async def _create_many_from_orm_objects(
        self, session: AsyncSession, objs: List[ORMModelType]
    ) -> List[ORMModelType]:
        """
        Asynchronously creates multiple ORMModel instances from a list of ORMModelType objects and adds them to the session.
        Args:
            session: The asynchronous session to use for creating the objects.
            objs: The list of ORMModelType objects to create the new objects from.
        Returns:
            List[ORMModelType]: The newly created objects.
        """
        session.add_all(objs)
        await session.commit()
        return objs

    async def _create_from_orm_object(
        self, session: AsyncSession, obj: ORMModelType
    ) -> ORMModelType:
        """
        Create an object from the given ORM object using the provided session.
        Args:
            session: The asynchronous session to use for creating the object.
            obj: The ORMModelType object to create the new object from.
        Returns:
            ORMModelType: The newly created object.
        """
        log.debug("creating %s with obj=%s", self._name, obj)
        session.add(obj)
        await session.commit()
        return obj

    async def delete(self, session: AsyncSession, obj: ORMModelType) -> ORMModelType:
        """
        Asynchronously deletes the given ORMModel object using the provided session.

        Args:
            session (Session): The database session to use for the deletion.
            obj (ORMModel): The object to be deleted from the database.

        Returns:
            ORMModel: The deleted object.
        """
        log.debug("deleting %s with obj=%s", self._name, obj)
        await session.delete(obj)
        await session.commit()
        return obj


    async def update(self, session: AsyncSession, obj: ORMModelType, obj_in: UpdateSchemaType) -> ORMModelType:
        """
        Asynchronously updates the given ORMModel object using the provided session and input data.

        Args:
            session (Session): The database session to use for the update.
            obj (ORMModel): The object to be updated in the database.
            obj_in (UpdateSchemaType): The input data for the update.

        Returns:
            ORMModel: The updated object.
        """
        update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_data.items():
            setattr(obj, field, value)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj