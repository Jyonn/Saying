import random

from SmartDjango import models, E
from smartify import P


@E.register()
class SentenceError:
    CREATE_SENTENCE = E("创建句子错误")
    NO_MATCHED_SENTENCE = E("找不到匹配的句子")
    NOT_FOUND_SENTENCE = E("不存在的句子")
    NOT_FOUND_TAG = E("不存在的标签")
    CREATE_TAG = E("创建标签错误")
    NOT_BELONG = E("不是你的句子")


class Sentence(models.Model):
    sentence = models.CharField(
        max_length=255,
        unique=True,
    )
    author = models.CharField(
        max_length=32,
        default=None,
        null=True,
    )
    reference = models.CharField(
        max_length=64,
        default=None,
        null=True,
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

    @classmethod
    def create(cls, sentence, author, reference, tags, owner):
        cls.validator(locals())

        try:
            sentence = cls(
                sentence=sentence,
                author=author,
                reference=reference,
                owner=owner,
            )
            sentence.save()
            sentence.tags.add(*tags)
            sentence.save()
        except Exception as err:
            raise SentenceError.ERROR_CREATE_SENTENCE
        return sentence

    def _readable_tags(self):
        tags = self.tags.all()
        return [tag.d() for tag in tags]

    def d(self):
        return self.dictor('pk->sid', 'sentence', 'author', 'reference', 'tags')

    @classmethod
    def get_random_sentence(cls, author, reference, max_length, consider_author, tags):
        sentences = cls.objects.search(author=author, reference=reference)

        filtered_sentences = []
        for sentence in sentences:
            satisfied = True
            for tag in tags:
                if tag not in sentence.tags:
                    satisfied = False
                    break
            if not satisfied:
                continue
            if consider_author:
                if len(sentence.author) + len(sentence.sentence) < max_length or max_length == 0:
                    filtered_sentences.append(sentence)
            else:
                if len(sentence.sentence) < max_length or max_length == 0:
                    filtered_sentences.append(sentence)
        if not filtered_sentences:
            raise SentenceError.NO_MATCHED_SENTENCE
        index = random.randint(0, len(filtered_sentences) - 1)
        return filtered_sentences[index]

    @classmethod
    def get_sentence_by_id(cls, sid):
        try:
            sentence = cls.objects.get(pk=sid)
        except cls.DoesNotExist:
            raise SentenceError.NOT_FOUND_SENTENCE
        return sentence

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

    def d(self):
        return self.dictor('pk->tid', 'tag')

    @classmethod
    def get_tag_by_id(cls, tid):
        try:
            tag = Tag.objects.get(pk=tid)
        except cls.DoesNotExist:
            raise SentenceError.NOT_FOUND_TAG
        return tag

    @classmethod
    def create(cls, tag):
        cls.validator(locals())

        try:
            tag = cls(tag=tag)
            tag.save()
        except Exception as err:
            raise SentenceError.ERROR_CREATE_TAG
        return tag

    @classmethod
    def list_to_tag_list(cls, tags):
        tag_list = []
        if not isinstance(tags, list):
            return []
        for i, tid in tags:
            try:
                tag_list.append(cls.get_tag_by_id(tid))
            except Exception:
                pass
        return tag_list

    @classmethod
    def get_tags(cls, page, count):
        tags = Tag.objects.all()
        if page >= 0 and count > 0:
            start = page * count
            end = start + count
            tags = tags[start: end]
        return tags


class SentenceP:
    sentence, author, reference = Sentence.get_params(
        'sentence', 'author', 'reference')

    tags = P('tags', '链接列表').default([])
    tags.process(Tag.list_to_tag_list)
