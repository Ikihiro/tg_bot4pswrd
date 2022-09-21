import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class DataBase:
    def __init__(self, pool):
        self.pool: Pool = pool

    @classmethod
    async def create(cls):
        pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            database=config.DB_NAME,
            host=config.DB_HOST
        )
        return cls(pool)

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchrow: bool = False,
                      fetchval: bool = False,
                      execute: bool = False):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)
        ])
        return sql, tuple(parameters.values())

    # Таблица для пользователей
    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
        telegram_id BIGINT PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username VARCHAR(255) NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users;"
        return await self.execute(sql, fetch=True)

    async def add_user(self, telegram_id, full_name, username):
        sql = "INSERT INTO users (telegram_id, full_name, username) VALUES ($1, $2, $3) returning *;"
        return await self.execute(sql, telegram_id, full_name, username, fetchrow=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    # Таблица для паролей
    async def create_table_pwds(self):
        sql = """
        CREATE TABLE IF NOT EXISTS pwds (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT,
        site VARCHAR(255) NOT NULL,
        pwd VARCHAR(255) NOT NULL UNIQUE,
        FOREIGN KEY (telegram_id) REFERENCES users (telegram_id) ON DELETE CASCADE
        );
        """
        await self.execute(sql, execute=True)

    async def select_pwd(self, **kwargs):
        sql = "SELECT * FROM pwds WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def add_pwd(self, telegram_id, site, pwd):
        sql = "INSERT INTO pwds (telegram_id, site, pwd) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, telegram_id, site, pwd, fetchrow=True)

    async def update_pwd(self, telegram_id, site, pwd):
        sql = "UPDATE pwds SET pwd = $1 WHERE telegram_id = $2 AND site = $3;"
        return await self.execute(sql, pwd, telegram_id, site, execute=True)

    async def delete_pwd(self, **kwargs):
        sql = "DELETE FROM pwds WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, execute=True)

    async def delete_all_pwds(self):
        return await self.execute("DELETE FROM pwds WHERE True;", execute=True)

    # Таблица для стикеров
    async def create_table_stickers(self):
        sql = """
        CREATE TABLE IF NOT EXISTS stickers (
        id SERIAL PRIMARY KEY,
        mood VARCHAR(255) NOT NULL,
        url VARCHAR(255) NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    async def select_all_stickers(self):
        sql = "SELECT * FROM stickers;"
        return await self.execute(sql, fetch=True)

    async def select_sticker(self, **kwargs):
        sql = "SELECT * FROM stickers WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def add_sticker(self, mood, url):
        sql = "INSERT INTO stickers (mood, url) VALUES ($1, $2) returning *;"
        return await self.execute(sql, mood, url, fetch=True)

    async def count_sticker(self):
        sql = "SELECT COUNT(*) FROM sticker;"
        return await self.execute(sql, fetchval=True)
