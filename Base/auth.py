from functools import wraps

from SmartDjango import E, Hc

from Base.jtoken import JWT
from User.models import User


@E.register()
class AuthError:
    REQUIRE_LOGIN = E("需要登录", hc=Hc.Unauthorized)
    TOKEN_MISS_PARAM = E("认证口令缺少参数{0}", hc=Hc.Forbidden)
    REQUIRE_ROOT = E("需要root权限")


class Auth:
    @staticmethod
    def validate_token(request):
        # jwt_str = request.META.get('HTTP_TOKEN')
        jwt_str = request.COOKIES['token']
        if not jwt_str:
            raise AuthError.REQUIRE_LOGIN

        return JWT.decrypt(jwt_str)

    @staticmethod
    def get_login_token(user: User):
        token, _dict = JWT.encrypt(dict(
            user_id=user.pk,
        ))
        _dict['token'] = token
        _dict['user'] = user.d()
        return _dict

    @classmethod
    def _extract_user(cls, r):
        r.user = None

        dict_ = cls.validate_token(r)
        user_id = dict_.get('user_id')
        if not user_id:
            raise AuthError.TOKEN_MISS_PARAM('user_id')

        from User.models import User
        r.user = User.get_user_by_id(user_id)

    @classmethod
    def require_login(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            cls._extract_user(r)
            return func(r, *args, **kwargs)
        return wrapper

    @classmethod
    def require_root(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            cls._extract_user(r)
            if r.user.pk != User.ROOT_ID:
                raise AuthError.REQUIRE_ROOT
            return func(r, *args, **kwargs)

        return wrapper
