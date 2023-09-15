import asyncio
import os
import uuid

from apiflask import APIFlask
from flask import redirect, url_for

from .employee import Employee

from .user import user
from .ledger import ledger
from .admin import admin

app = APIFlask(__name__, title="固定资产管理系统", version="0.2", docs_ui="redoc")
app.secret_key = os.getenv("SECRET_KEY", "ocefjVp_pL4Iens21FTjsA")

app.register_blueprint(user)
app.register_blueprint(ledger)
app.register_blueprint(admin)

import sqlite3
from sqlite3 import dbapi2


def init_db():
    engine = dbapi2.connect("assert.db")
    engine.row_factory = sqlite3.Row
    with open("table.sql") as f:
        engine.cursor().executescript(f.read())
    engine.commit()
    print("Initialize database completed!")


def init_data():
    """注入基础数据"""
    # 用户表
    db = sqlite3.connect("assert.db")

    db.cursor().execute(f"INSERT INTO department VALUES (1,'生产部','生产营运部')")
    db.cursor().execute(f"INSERT INTO department VALUES (2,'总经办','')")
    db.cursor().execute(f"INSERT INTO department VALUES (3,'财务部','')")
    db.cursor().execute(f"INSERT INTO department VALUES (4,'人事部','')")
    db.cursor().execute(f"INSERT INTO department VALUES (5,'市场部','市场发展部')")
    db.cursor().execute(f"INSERT INTO department VALUES (6,'物流部','')")
    db.cursor().execute(f"INSERT INTO department VALUES (7,'行政部','')")
    db.cursor().execute(f"INSERT INTO department VALUES (8,'宜昌所','宜昌市内及市外')")
    db.cursor().execute(f"INSERT INTO department VALUES (9,'恩施办','')")
    db.cursor().execute(f"INSERT INTO department VALUES (10,'荆州所','')")
    db.cursor().execute(f"INSERT INTO department VALUES (11,'襄阳所','')")
    db.cursor().execute(f"INSERT INTO department VALUES (12,'十堰办','')")
    db.cursor().execute(f"INSERT INTO department VALUES (13,'荆门办','')")
    db.cursor().execute(f"INSERT INTO department VALUES (14,'特渠部','')")

    db.cursor().execute(f"INSERT INTO category VALUES ('1','房屋及建筑物','')")
    db.cursor().execute(f"INSERT INTO category VALUES ('2','办公家具','')")
    db.cursor().execute(f"INSERT INTO category VALUES ('3','电脑及打印机','')")
    db.cursor().execute(f"INSERT INTO category VALUES ('4','家电','')")
    db.cursor().execute(f"INSERT INTO category VALUES ('5','机械设备','')")
    db.cursor().execute(f"INSERT INTO category VALUES ('6','数码产品','')")
    db.cursor().execute(f"INSERT INTO category VALUES ('7','车辆','')")
    db.cursor().execute(f"INSERT INTO category VALUES ('8','其他','')")

    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('01','建筑物','1')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('02','房屋','1')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('01','桌','2')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('02','椅','2')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('01','电脑','3')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('02','打印机','3')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('01','风扇','4')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('02','取暖器','4')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('03','白板','4')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('04','净水机','4')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('05','烘手机','4')")

    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('01','激光笔','6')")
    db.cursor().execute(
        f"INSERT INTO type (tid,name,cid) VALUES ('02','TypeC转网口转换器','6')"
    )
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('01','轿车','7')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('02','SUV','7')")
    db.cursor().execute(f"INSERT INTO type (tid,name,cid) VALUES ('03','MPV','7')")

    mei = Employee(104900)
    mei.set_password("12345")
    db.cursor().execute(
        f"INSERT INTO user (user_id,role_id,username, password) VALUES (104900,8,'梅煜', '{mei.password}')"
    )

    # 角色表
    db.cursor().execute("INSERT INTO role VALUES (8,'God', '上帝')")
    db.cursor().execute("INSERT INTO role VALUES (4,'Administrator', '超级管理员')")
    db.cursor().execute("INSERT INTO role VALUES (2,'Moderator', '协管员')")
    db.cursor().execute("INSERT INTO role VALUES (1,'User', '普通用户')")

    # 权限表
    db.cursor().execute("INSERT INTO permission VALUES (1,'update', '修改')")
    db.cursor().execute("INSERT INTO permission VALUES (2,'create', '增加')")
    db.cursor().execute("INSERT INTO permission VALUES (3,'download', '下载')")
    db.cursor().execute("INSERT INTO permission VALUES (4,'query', '查看')")
    db.cursor().execute("INSERT INTO permission VALUES (5,'find', '看人')")
    db.cursor().execute("INSERT INTO permission VALUES (6,'delete', '删除')")

    # 角色权限表
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (8,1)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (8,2)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (8,3)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (8,4)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (8,5)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (8,6)"
    )

    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (4,2)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (4,3)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (4,4)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (4,6)"
    )

    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (2,1)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (2,3)"
    )
    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (2,4)"
    )

    db.cursor().execute(
        "INSERT INTO role_permission (role_id,permission_id) VALUES (1,2)"
    )

    db.commit()
    print("Datas has been inserted successful!")


def run():
    app.run(host="0.0.0.0", debug=True)


@app.get("/")
def index():
    return redirect(url_for("user.login_show"))
