"""
This module contains the base interface for CRUD 
(Create, Read, Update, Delete) operations.
"""

from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4, BaseModel
from sqlalchemy import func, select

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
        
    async def get_one_by_id(self, session: AsyncSession, id: str | UUID4) -> ORMModelType | None:
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
    
    async def get_many_by_ids(self, session: AsyncSession, ids: List[str | UUID4]) -> List[ORMModelType]:
        """
        Asynchronously gets multiple records by their IDs.

        Args:
            session (Session): The database session to use.
            ids (List[str | UUID4]): The IDs of the records to retrieve.

        Returns:
            List[ORMModel]: A list of retrieved records.
        """
        
        log.debug("getting %s with ids=%s", self._name, ids)
        result = await session.execute(select(self._model).filter(self._model.id.in_(ids)))
        return result.scalars().all()
    
    async def get_one(self, session: AsyncSession, *args, **kwargs) -> Optional[ORMModelType]:
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
        result = await session.execute(select(self._model).filter(*args).filter_by(**kwargs))
        return result.scalars().first()

    async def get_many(self, session: AsyncSession, *args, offset: int = 0, limit: int = 100, **kwargs) -> List[ORMModelType]:
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
        result = await session.execute(select(self._model).filter(*args).filter_by(**kwargs).offset(offset).limit(limit))
        return result.scalars().all()
    
    async def create(self, session: AsyncSession, obj_in: CreateSchemaType) -> ORMModelType:
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