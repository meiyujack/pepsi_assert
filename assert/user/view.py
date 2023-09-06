import json, os

from flask import redirect, url_for, g, flash
from flask.templating import render_template
from . import user

from apiflask import Schema, HTTPTokenAuth
from apiflask.fields import String, Integer, File
from apiflask.validators import Length

from ..employee import Employee, db, secure, base

token_auth = HTTPTokenAuth(scheme="token")


class PasswordIn(Schema):
    original_password = String(required=True)
    new_password = String(required=True)


class UserIdIn(Schema):
    userid = String(required=True, validate=Length(6))


class UserIn(UserIdIn):
    password = String(required=True)


class SignupIn(UserIn):
    username = String(required=True)


class TokenIn(Schema):
    token = String(required=True)


class ProfileIn(Schema):
    avatar = String()
    gender = Integer()
    department = String()
    tel = String()


class AvatarIn(Schema):
    avatar = String()


@user.get("/")
async def login_show():
    return render_template("login.html")


@user.post("/")
@user.input(UserIn, location="form")
# @user_bp.output(UserOut)
async def login_post(data):
    curr_user = await Employee.get_user_by_id(data.get("userid"))
    if curr_user:
        if curr_user.check_password(password=data.get("password")):
            token = secure.generate_token(
                {"uid": curr_user.user_id, "rid": curr_user.role_id}
            )
            # response.headers['token'] = token
            return redirect(url_for("user.profile", token=token))
    flash("请检查用户名或密码。或还未注册？")
    return render_template("login.html")


@user.get("/logout")
@user.input(TokenIn, location="query")
async def logout(query_data):
    token = query_data["token"]
    curr_user = await Employee.get_user_by_token(token)
    if curr_user:
        return redirect(url_for("user.login_show"))


@user.get("/signup")
async def sign_show():
    return render_template("signup.html")


@user.post("/signup")
@user.input(SignupIn, location="form")
async def sign_post(data):
    result = await Employee.get_user_by_id(data["userid"])
    if result:
        return redirect(url_for("user.login_show"))
    else:
        wanna_user = Employee(data["userid"])
        wanna_user.username = data["username"]
        wanna_user.set_password(data["password"])
        if not await wanna_user.insert_user(data["userid"]):
            flash(f"{wanna_user.username}注册成功～")
            return redirect(url_for("user.login_show"))
    return render_template("signup.html")


@user.get("/name")
@user.input(UserIdIn, location="query")
async def get_your_name(data):
    base.connect_db()
    username = base.select_db("user", "name", uid=data["userid"])
    if username:
        username = username[0][0]
        return username
    return ""


@user.get("/avatar")
@user.input(TokenIn, location="query")
async def avatar(data):
    return render_template("update_avatar.html")

@user.post("/avatar")
@user.input(TokenIn, location="query")
@user.input(AvatarIn,location="form_and_files")
async def update_avatar(data,forms):
    print(data)
    print(forms)
    avatar_file = forms["avatar"]
    print(avatar_file)
    token = data["token"]

    uid = secure.get_info_by_token(token, "uid")
    curr = await Employee.get_user_by_id(uid)
    try:
        await curr.save_avatar(avatar_file)
    except:
        return ""


@user.get("/profile")
@user.input(TokenIn, location="query")
# @token_auth.login_required
async def profile(data):
    curr_token = data["token"]
    curr_user = await Employee.get_user_by_token(curr_token)
    if curr_user:
        if curr_user.department_id and curr_user.department_id != "None":
            flash(f"欢迎回来～{curr_user.username}")
            department = await Employee.get_department_by_id(curr_user.department_id)
            return render_template(
                "profile.html",
                curr_user=curr_user,
                department=department,
                token=curr_token,
            )
        return render_template("profile.html", curr_user=curr_user, token=curr_token)
    return None


@user.post("/profile")
@user.input(ProfileIn, location="form")
@user.input(TokenIn, location="query")
async def profile_update(data, query_data):
    print(data)
    curr_token = query_data.get("token")
    if curr_token:
        curr_user = await Employee.get_user_by_token(curr_token)
        avatar = data.get("avatar")
        gender = str(data.get("gender"))
        department_id = data.get("department")
        tel = data.get("tel")
        r = None
        print(avatar)
        if gender != "None":
            if gender != curr_user.gender:
                r = await db.update(
                    "user", {"gender": int(gender)}, user_id=curr_user.user_id
                )
        if department_id:
            if department_id != curr_user.department_id:
                # department=await db.select_db('department','department_name',department_id=department_id)
                # department=department[0][0]
                r = await db.update(
                    "user", {"department_id": department_id}, user_id=curr_user.user_id
                )
        if tel:
            if tel != curr_user.telephone:
                r = await db.update(
                    "user", {"telephone": tel}, user_id=curr_user.user_id
                )
        if r is None:
            flash(f"{curr_user.username}更新信息成功～")
            return redirect(url_for("user.profile", token=curr_token))


@user.get("/departments")
@user.input(TokenIn, location="query")
async def get_departments(data):
    curr_token = data.get("token")
    if curr_token:
        curr_user = await Employee.get_user_by_token(curr_token)
        if not curr_user.department_id or curr_user.department_id == "None":
            result = await db.select_db("department", "department_id,department_name")
            if result:
                return json.dumps(result)
        return ""


@user.get("/update_password")
@user.input(TokenIn, location="query")
async def update_password(data):
    return render_template("update_password.html")


@user.post("/update_password")
@user.input(PasswordIn, location="form")
@user.input(TokenIn, location="query")
async def password_update(data, query_data):
    curr_token = query_data["token"]
    curr_user = await Employee.get_user_by_token(query_data["token"])
    if curr_user.check_password(data["original_password"]):
        result = await curr_user.alter_password(data["new_password"])
        if not result:
            flash("密码修改成功～")
            return redirect(url_for("user.login_show", token=curr_token))
        else:
            flash("密码修改失败")
            assert "impossible"
    else:
        flash("原密码不正确，请重试")
        return render_template("update_password.html")
