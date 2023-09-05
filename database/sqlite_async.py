import aiosqlite

from . import Database


class AsyncSqlite(Database):
    def __init__(self, server, **kwargs):
        super().__init__(server, **kwargs)
        self.server = server
        self.conn = None

    async def connect_db(self):
        self.conn = await self.server.connect(self.basic.get("file_address"))

    async def init_table(self):
        """
        Initialize table schema structure.
        """
        async with aiosqlite.connect(self.basic.get("file_address")) as conn:
            with open(self.basic["sql_address"], mode="r") as file:
                conn.row_factory = aiosqlite.Row
                await conn.executescript(file.read())
                await conn.commit()
                print("Initialize database completed!")

    async def select_db(self, table, get="*", prep=None, **condition):
        await self.connect_db()
        sql = f"SELECT {get} FROM {table}"
        if condition:
            where = f" WHERE {','.join(condition.keys())}={','.join(['?'])}"
            if len(condition) == 1:
                sql += where
            else:
                where = f" {prep} ".join(
                    [
                        f"{''.join(m.keys())}={''.join(['?'])}"
                        for m in [{i: j} for i, j in condition.items()]
                    ]
                )
                sql += " WHERE " + where
        try:
            async with self.conn.execute(sql, tuple(condition.values())) as cursor:
                return await cursor.fetchall()
        except self.server.Error as ex:
            await self.conn.rollback()
            return f"Error:{ex}"

    async def insert(self, table, data, **condition):
        await self.connect_db()
        keys = ",".join(data.keys())
        values = ",".join(["?"] * len(data))
        try:
            sql = f"INSERT INTO {table}({keys}) VALUES({values});"
            where = f" WHERE {','.join(condition.keys())}={','.join(['?'])};"
            sql += where
            if await self.conn.execute(sql, tuple(condition.values())):
                await self.conn.commit()
        except self.server.Error as ex:
            await self.conn.rollback()
            return f"Error:{ex}"

    async def update(self, table, data, **condition):
        await self.connect_db()
        s = ""
        for k, v in data.items():
            s += f"{k}='{v}',"
        s = s[:-1]
        try:
            sql = f"UPDATE {table} SET {s}"
            where = f" WHERE {','.join(condition.keys())}={','.join(['?'])};"
            sql += where
            if await self.conn.execute(sql, tuple(condition.values())):
                await self.conn.commit()
        except self.server.Error as ex:
            await self.conn.rollback()
            return f"Error:{ex}"

    async def delete(self, table, **condition):
        await self.connect_db()
        sql = f"DELETE FROM {table}"
        where = f" WHERE {','.join(condition.keys())}={','.join(['?'])};"
        sql += where
        try:
            if await self.conn.execute(sql, tuple(condition.values())):
                await self.conn.commit()
        except self.server.Error as ex:
            await self.conn.rollback()
            return f"Error:{ex}"

    async def just_exe(self, sql):
        """Just execute sql command. Like more than one table query"""

        try:
            async with self.conn.execute(sql) as cursor:
                return await cursor.fetchall()
        except self.server.Error as ex:
            return f"Error:{ex}"
