from django.db import models

from Base.common import deprint
from Base.decorator import field_validator
from Base.error import Error
from Base.response import Ret


class Sentence(models.Model):
    L = {
        'sentence': 512,
        'author': 32,
        'reference': 64,
    }
    sentence = models.CharField(
        max_length=L['sentence'],
    )
    author = models.CharField(
        max_length=L['author'],
    )
    reference = models.CharField(
        max_length=L['reference'],
    )
    tags = models.ManyToManyField(
        'Tag',
        default=None,
    )
    owner = models.ForeignKey(
        'User.User',
        on_delete=models.SET_NULL,
    )

    @classmethod
    def _validate(cls, d):
        return field_validator(d, cls)

    @classmethod
    def create(cls, sentence, author, reference, tags, owner):
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret
        try:
            o_sentence = cls(
                sentence=sentence,
                author=author,
                reference=reference,
                tags=tags,
                owner=owner,
            )
            o_sentence.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_SENTENCE)
        return Ret(o_sentence)

    def to_dict(self):
        tags = self.tags.all()
        tag_list = [o_tag.to_dict() for o_tag in tags]
        return dict(
            sid=self.pk,
            sentence=self.sentence,
            author=self.author,
            reference=self.reference,
            tags=tag_list,
            owner=self.owner.to_dict() if self.owner else None
        )


class Tag(models.Model):
    """标签类，句子的情感标签"""
    L = {
        'tag': 10,
    }
    tag = models.CharField(
        max_length=L['tag'],
        unique=True,
    )

    def to_dict(self):
        return dict(
            tid=self.pk,
            tag=self.tag,
        )

    @classmethod
    def get_tag_by_id(cls, tid):
        try:
            o_tag = Tag.objects.get(pk=tid)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_TAG)
        return Ret(o_tag)

    @classmethod
    def create(cls, tag):
        try:
            o_tag = cls(tag=tag)
            o_tag.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_TAG)
        return Ret(o_tag)
