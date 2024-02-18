"""
This module contains the base interface for CRUD 
(Create, Read, Update, Delete) operations.
"""

from typing import List, Optional, Type, TypeVar

from pydantic import UUID4, BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from worklog.log import get_logger

ORMModel = TypeVar("ORMModel")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


log = get_logger(__name__)


class CRUDRepository:
    """Base interface for CRUD operations."""
    
    def __init__(self, model: Type[ORMModel]) -> None:
        """
        Initializes the class with the given ORM model.

        Args:
            model (Type[ORMModel]): The ORM model to be initialized.
        """
        
        self._model: Type[ORMModel] = model
        self._name: str = model.__name__
        
    async def get_by_id(self, session: Session, id: str | UUID4) -> Optional[ORMModel]:
        """
        Asynchronously gets a record by its ID.

        Args:
            session (Session): The database session to use.
            id (str | UUID4): The ID of the record to retrieve.

        Returns:
            Optional[ORMModel]: The retrieved record, or None if not found.
        """
        log.debug("getting %s with id=%s", self._name, id)
        result = session.execute(select(self._model).filter(self._model.id == id))
        return result.scalars().first()
    
    async def get_one(self, session: Session, *args, **kwargs) -> Optional[ORMModel]:
        """
        Asynchronously retrieves one ORMModel using the provided session and optional 
        arguments and keyword arguments. 
        
        Args:
            session (Session): The database session to use.
            *args: Variable length argument list used for filtering. For example filter(User.name == 'John')
            **kwargs: Keyword arguments used for filter_by. For example filter_by(name='John')
        
        Returns:
            Optional[ORMModel]: The retrieved record, or None if not found.
        """
        
        log.debug("getting %s with args=%s, kwargs=%s", self._name, args, kwargs)
        result = session.execute(select(self._model).filter(*args).filter_by(**kwargs))
        return result.scalars().first()

    async def get_many(self, session: Session, *args, offset: int = 0, limit: int = 100, **kwargs) -> List[ORMModel]:
        """
        Asynchronously gets multiple ORMModel objects from the database with optional filtering and limiting.

        Args:
            session (Session): The database session.
            *args: Positional arguments for filtering the query. For example filter(User.name == 'John')
            offset (int, optional): The number of results to skip. Defaults to 0.
            limit (int, optional): The maximum number of results to return. Defaults to 100.
            **kwargs: Keyword arguments for filtering the query. For example filter_by(name='John')

        Returns:
            List[ORMModel]: A list of ORMModel objects retrieved from the database.
        """
        log.debug("getting all %s with args=%s, kwargs=%s", self._name, args, kwargs)
        result = session.execute(select(self._model).filter(*args).filter_by(**kwargs).offset(offset).limit(limit))
        return result.scalars().all()
    
    async def create(self, session: Session, obj_in: CreateSchemaType) -> ORMModel:
        """
        Asynchronously creates a new ORMModel instance and adds it to the session. 

        Args:
            session (Session): The database session.
            obj_in (CreateSchemaType): The input data for creating the ORMModel instance.

        Returns:
            ORMModel: The newly created ORMModel instance.
        """
        log.debug("creating %s with obj_in=%s", self._name, obj_in)
        obj_in_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
        db_obj = self._model(**obj_in_data)  # type: ignore
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    
    async def delete(self, session: Session, obj: ORMModel) -> ORMModel:
        """
        Asynchronously deletes the given ORMModel object using the provided session.

        Args:
            session (Session): The database session to use for the deletion.
            obj (ORMModel): The object to be deleted from the database.

        Returns:
            ORMModel: The deleted object.
        """
        log.debug("deleting %s with obj=%s", self._name, obj)
        session.delete(obj)
        await session.commit()
        return obj