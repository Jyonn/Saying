""" Adel Liu 180228

用户API处理函数
"""
from SmartDjango import Analyse
from django.views import View
from smartify import P

from Base.auth import Auth
from User.models import User, UserP


class UserView(View):
    @staticmethod
    @Auth.require_login
    def get(request):
        """ GET /api/user/

        获取我的信息
        """
        user = request.user
        return UsernameView.get(request, user.username)

    @staticmethod
    @Analyse.r(b=[UserP.username, UserP.password])
    def post(request):
        """ POST /api/user/

        创建用户
        """
        user = User.create(**request.d.dict())

        return Auth.get_login_token(user)

    @staticmethod
    @Analyse.r(b={
        UserP.password.clone().default(None),
        UserP.password.clone().rename('old_password').default(None),
        P('nickname', '昵称').default(None)  # 教学示范
    })
    @Auth.require_login
    def put(request):
        """ PUT /api/user/

        修改用户信息
        """
        user = request.user

        password = request.d.password
        nickname = request.d.nickname
        old_password = request.d.old_password

        if password is not None:
            user.change_password(password, old_password)
        else:
            user.modify_info(nickname)
        return user.d()


class UsernameView(View):
    @staticmethod
    @Analyse.r(a=[UserP.username])
    def get(request):
        """ GET /api/user/@:username

        获取用户信息
        """
        username = request.r.username
        user = User.get_user_by_username(username)
        return user.d()

    @staticmethod
    @Analyse.r(a=[UserP.username])
    @Auth.require_root
    def delete(request):
        """ DELETE /api/user/@:username

        删除用户
        """
        username = request.r.username
        user = User.get_user_by_username(username)
        user.delete()


class TokenView(View):
    @staticmethod
    @Analyse.r(b=[UserP.username, UserP.password])
    def post(request):
        """ POST /api/user/token

        登录获取token
        """
        user = User.authenticate(**request.d.dict())
        return Auth.get_login_token(user)
