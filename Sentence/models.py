import random

from django.db import models

from Base.common import deprint
from Base.decorator import field_validator
from Base.error import Error
from Base.response import Ret


class Sentence(models.Model):
    L = {
        'sentence': 255,
        'author': 32,
        'reference': 64,
    }
    sentence = models.CharField(
        max_length=L['sentence'],
        unique=True,
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
        null=True,
    )
    FIELD_LIST = ['sentence', 'author', 'reference', 'tags', 'owner']

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
                owner=owner,
            )
            o_sentence.save()
            o_sentence.tags.add(*tags)
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
        )

    @classmethod
    def get_random_photo(cls):
        sentences = cls.objects.all()
        index = random.randint(0, len(sentences) - 1)
        return sentences[index].to_dict()

    @classmethod
    def get_sentence_by_id(cls, sid):
        try:
            o_sentence = cls.objects.get(pk=sid)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_SENTENCE)
        return Ret(o_sentence)

    def union_tags(self, tags):
        self.tags.add(*tags)


class Tag(models.Model):
    """标签类，句子的情感标签"""
    L = {
        'tag': 10,
    }
    MIN_L = {
        'tag': 1,
    }
    tag = models.CharField(
        max_length=L['tag'],
        unique=True,
    )
    FIELD_LIST = ['tag']

    @classmethod
    def _validate(cls, d):
        return field_validator(d, cls)

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
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret
        try:
            o_tag = cls(tag=tag)
            o_tag.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_TAG)
        return Ret(o_tag)

    @classmethod
    def list_to_o_tag_list(cls, tags):
        tag_list = []
        if not isinstance(tags, list):
            return []
        for i, tid in tags:
            ret = cls.get_tag_by_id(tid)
            if ret.body is not Error.OK:
                continue
            tag_list.append(ret.body)
        return tag_list

    @classmethod
    def get_tags(cls, page, count):
        tags = Tag.objects.all()
        if page >= 0 and count > 0:
            start = page * count
            end = start + count
            tags = tags[start: end]
        return Ret(tags)
