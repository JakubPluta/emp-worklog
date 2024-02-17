from sqlalchemy import select
from worklog import config, security
from worklog.database.session import async_session
from worklog.models import User
from worklog.log import get_logger

log = get_logger(__name__)

async def create_first_superuser() -> None:
    """
    Asynchronously creates the first superuser, checks if the user already exists, 
    and logs the creation or existence of the superuser.
    """
    log.debug("creating first superuser: %s", config.settings.FIRST_SUPERUSER_EMAIL)
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == config.settings.FIRST_SUPERUSER_EMAIL)
        )
        user = result.scalars().first()

        if user is None:
            new_superuser = User(
                email=config.settings.FIRST_SUPERUSER_EMAIL,
                name=config.settings.FIRST_SUPERUSER_NAME,
                hashed_password=security.get_password_hash(
                    config.settings.FIRST_SUPERUSER_PASSWORD
                ),
                is_active=True,
                is_superuser=True,
            )
            session.add(new_superuser)
            await session.commit()
            log.debug("Superuser with email %s was created", config.settings.FIRST_SUPERUSER_EMAIL)
        else:
            log.debug("Superuser with email %s already exists in database", config.settings.FIRST_SUPERUSER_EMAIL)

        
        
async def get_all_users():
    """
    Asynchronous function that retrieves all users from the database and returns them as a list.
    """
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
    
    log.debug("found %d users:", len(users))
    for idx, user in enumerate(users, start=1):
        log.debug("%d. user: %s", idx, user)
    return users