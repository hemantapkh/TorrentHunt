'''API to connect to the database server'''

import asyncpg


class DataBase:
    def __init__(self, user, password, database):
        self.user = user
        self.password = password
        self.database = database

    async def query(self, method, query, *args):
        con = await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.database,
        )
        row = await getattr(con, method)(query, *args)

        await con.close()
        return row
