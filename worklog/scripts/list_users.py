import asyncio
from worklog.scripts.utils import get_all_users


if __name__ == "__main__":
    asyncio.run(get_all_users())