""" Adel Liu 180228

用户API处理函数
"""
from django.views import View

from Base.decorator import require_json, require_post, require_login, require_get, require_delete, \
    require_put, require_root
from Base.error import Error
from Base.jtoken import jwt_e
from Base.response import response, error_response

from User.models import User


class UserView(View):
    @staticmethod
    def get_token_info(o_user):
        ret = jwt_e(dict(user_id=o_user.pk))
        if ret.error is not Error.OK:
            return error_response(ret)
        token, dict_ = ret.body
        dict_['token'] = token
        dict_['avatar'] = o_user.get_avatar_url()
        return dict_

    @staticmethod
    @require_get()
    @require_login
    def get(request):
        """ GET /api/user/

        获取我的信息
        """
        o_user = request.user
        return UsernameView.get(request, o_user.username)

    @staticmethod
    @require_json
    @require_post(['username', 'password'])
    def post(request):
        """ POST /api/user/

        创建用户
        """
        username = request.d.username
        password = request.d.password

        ret = User.create(username, password)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_user = ret.body
        if not isinstance(o_user, User):
            return error_response(Error.STRANGE)

        return response(body=UserView.get_token_info(o_user))

    @staticmethod
    @require_json
    @require_put(
        [
            ('password', None, None),
            ('old_password', None, None),
            ('nickname', None, None)
        ]
    )
    @require_login
    def put(request):
        """ PUT /api/user/

        修改用户信息
        """
        o_user = request.user
        if not isinstance(o_user, User):
            return error_response(Error.STRANGE)

        password = request.d.password
        nickname = request.d.nickname
        old_password = request.d.old_password
        if password is not None:
            ret = o_user.change_password(password, old_password)
            if ret.error is not Error.OK:
                return error_response(ret)
        o_user.modify_info(nickname)
        return response(body=o_user.to_dict())


class UsernameView(View):
    @staticmethod
    @require_get()
    def get(request, username):
        """ GET /api/user/@:username

        获取用户信息
        """
        ret = User.get_user_by_username(username)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_user = ret.body
        if not isinstance(o_user, User):
            return error_response(Error.STRANGE)
        return response(body=o_user.to_dict())

    @staticmethod
    @require_delete()
    @require_root
    def delete(request, username):
        """ DELETE /api/user/@:username

        删除用户
        """
        o_user = request.user
        if not isinstance(o_user, User):
            return error_response(Error.STRANGE)

        ret = User.get_user_by_username(username)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_user = ret.body
        if not isinstance(o_user, User):
            return error_response(Error.STRANGE)
        o_user.delete()
        return response()


class TokenView(View):
    @staticmethod
    @require_json
    @require_post(['username', 'password'])
    def get(request):
        """ GET /api/user/token

        登录获取token
        """
        username = request.d.username
        password = request.d.password

        ret = User.authenticate(username, password)
        if ret.error != Error.OK:
            return error_response(ret)
        o_user = ret.body
        if not isinstance(o_user, User):
            return error_response(Error.STRANGE)

        return response(body=UserView.get_token_info(o_user))
