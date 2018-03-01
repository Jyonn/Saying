""" Adel Liu 180228

用户类
"""
import re
import string

from django.db import models
from django.utils.crypto import get_random_string

from Base.common import deprint
from Base.decorator import field_validator
from Base.error import Error
from Base.response import Ret


class User(models.Model):
    """
    用户类
    根超级用户id=1
    """
    ROOT_ID = 1
    L = {
        'username': 32,
        'password': 32,
        'salt': 10,
        'nickname': 10,
        'avatar': 1024,
        'phone': 20,
    }
    MIN_L = {
        'username': 3,
        'password': 6,
    }
    username = models.CharField(
        max_length=L['username'],
        unique=True,
        blank=True,
        null=True,
        default=None,
    )
    password = models.CharField(
        max_length=L['password'],
    )
    salt = models.CharField(
        max_length=L['salt'],
        default=None,
    )
    pwd_change_time = models.FloatField(
        null=True,
        blank=True,
        default=0,
    )
    FIELD_LIST = ['username', 'password']

    @staticmethod
    def _valid_username(username):
        """验证用户名合法"""
        if username[0] not in string.ascii_lowercase + string.ascii_uppercase:
            return Ret(Error.INVALID_USERNAME_FIRST)
        valid_chars = '^[A-Za-z0-9_]{3,32}$'
        if re.match(valid_chars, username) is None:
            return Ret(Error.INVALID_USERNAME)
        return Ret()

    @staticmethod
    def _valid_password(password):
        """验证密码合法"""
        valid_chars = '^[A-Za-z0-9!@#$%^&*()_+-=,.?;:]{6,16}$'
        if re.match(valid_chars, password) is None:
            return Ret(Error.INVALID_PASSWORD)
        return Ret()

    @classmethod
    def _validate(cls, dict_):
        """验证传入参数是否合法"""
        return field_validator(dict_, cls)

    @staticmethod
    def hash_password(raw_password, salt=None):
        if not salt:
            salt = get_random_string(length=6)
        hash_password = User._hash(raw_password+salt)
        return salt, hash_password

    @classmethod
    def create(cls, username, password):
        """ 创建用户

        :param username: 用户名
        :param password: 密码
        :return: Ret对象，错误返回错误代码，成功返回用户对象
        """
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        salt, hashed_password = User.hash_password(password)
        ret = User.get_user_by_username(username)
        if ret.error is Error.OK:
            return Ret(Error.USERNAME_EXIST)
        try:
            o_user = cls(
                username=username,
                password=hashed_password,
                salt=salt,
            )
            o_user.save()
        except ValueError as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_USER)
        return Ret(o_user)

    def change_password(self, password, old_password):
        """修改密码"""
        ret = self._validate(locals())
        if ret.error is not Error.OK:
            return ret
        if self.password != User._hash(old_password):
            return Ret(Error.ERROR_PASSWORD)
        self.salt, self.password = User.hash_password(password)
        import datetime
        self.pwd_change_time = datetime.datetime.now().timestamp()
        self.save()
        return Ret()

    @staticmethod
    def _hash(s):
        from Base.common import md5
        return md5(s)

    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户对象"""
        try:
            o_user = User.objects.get(username=username)
        except User.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        return Ret(o_user)

    @staticmethod
    def get_user_by_id(user_id):
        """根据用户ID获取用户对象"""
        try:
            o_user = User.objects.get(pk=user_id)
        except User.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        return Ret(o_user)

    @staticmethod
    def authenticate(username, password):
        """验证用户名和密码是否匹配"""
        ret = User._validate(locals())
        if ret.error is not Error.OK:
            return ret
        try:
            o_user = User.objects.get(username=username)
        except User.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_USER)
        salt, hashed_password = User.hash_password(password, o_user.salt)
        if hashed_password == o_user.password:
            return Ret(o_user)
        return Ret(Error.ERROR_PASSWORD)

    def to_dict(self):
        return dict(
            uid=self.pk,
            username=self.username,
        )
