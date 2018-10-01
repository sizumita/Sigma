import asyncpg


class PstManager:
    def __init__(self, user, pwd, database):
        self.credentials = {"user": user, "password": pwd, "database": database, "host": "127.0.0.1"}
        self.db = None

    async def database_in(self):
        self.db = await asyncpg.create_pool(**self.credentials)

    async def _sql(self, sql):
        """use INSERT"""
        await self.db.execute(sql)

    async def _fetch(self, sql):
        """use SELECT"""
        await self.db.fetchrow(sql)

    async def close(self):
        await self.db.close()
