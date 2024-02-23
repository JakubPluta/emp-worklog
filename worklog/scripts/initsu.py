import asyncio

from worklog.scripts.utils import create_first_superuser

if __name__ == "__main__":
    asyncio.run(create_first_superuser())
