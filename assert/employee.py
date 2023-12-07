import uuid
import os
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash
import aiosqlite

from database.sqlite_async import AsyncSqlite
from database import Database
from auth import WebSecurity

db = AsyncSqlite(aiosqlite, file_address="assert.db", sql_address="table.sql")
base = Database(sqlite3, file_address="pepsi_yc")

secure = WebSecurity(os.getenv("SECRET_KEY", "ocefjVp_pL4Iens21FTjsA"))


class Employee:
    def __init__(self, user_id):
        self.user_id = user_id
        self.role_id = None
        self.username = None
        self.password = None
        self.create_time = None
        self.gender = None
        self.department_id = None
        self.avatar = None
        self.telephone = None

    # @username.getter
    # def username(self, value):
    #     if not value:
    #         raise ValueError("必须有用户名")
    #     self._username = value

    def to_dict(self):
        properties = ["username"]
        return {prop: getattr(self, prop, None) for prop in properties}

    @staticmethod
    async def get_user_by_id(user_id):
        user = await db.select_db("user", user_id=user_id)
        if user:
            _ = Employee(user[0][0])
            _.role_id = user[0][1]
            _.username = user[0][2]
            _.password = user[0][3]
            _.create_time = user[0][4]
            _.gender = user[0][5]
            _.department_id = user[0][6]
            _.avatar = user[0][7]
            _.telephone = user[0][8]
            return _
        return None

    @staticmethod
    async def get_department_by_id(department_id):
        department = await db.select_db(
            "department", "department_name", department_id=department_id
        )
        return department[0][0]

    @staticmethod
    async def get_user_by_token(token):
        user_id = secure.get_info_by_token(token, "uid")
        if user_id:
            curr_user = await Employee.get_user_by_id(user_id=user_id)
            return curr_user

    async def insert_user(self, user_id):
        return await db.insert(
            "user",
            {"user_id": user_id, "username": self.username, "password": self.password},
        )

    async def save_avatar(self, avatar_address):
        with open(avatar_address, "rb") as f:
            # index = avatar_address.rindex('.')
            # format = avatar_address[index:]
            self.avatar = f.read()
            if len(self.avatar) < 128 * 1024:
                await db.insert(
                    "user",
                    {"avatar": self.avatar},
                    user_id=self.user_id,
                )
            else:
                return None

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        is_valid = check_password_hash(self.password, password)
        return is_valid

    async def alter_password(self, new):
        self.set_password(password=new)
        await db.update("user", {"password": self.password}, user_id=self.user_id)

    async def get_privileges(self, token):
        rid = secure.get_info_by_token(token, key="rid")
        permissions = await db.just_exe(
            f"SELECT permission_name from permission p join role_permission rp ON p.permission_id =rp.permission_id WHERE rp.role_id ={rid};"
        )
        return permissions
