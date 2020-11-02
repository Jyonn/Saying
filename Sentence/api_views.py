from SmartDjango import Analyse, P
from django.views import View

from Agent.models import Agent
from Base.auth import Auth
from Sentence.models import Sentence, Tag, SentenceP, SentenceError


class SentenceView(View):
    @staticmethod
    @Analyse.r(q=[
        P('max_length', '最大长度').default(0).process(int),
        P('consider_author', '长度考虑作者名').default(0).process(bool),
        SentenceP.tags,
        SentenceP.author,
        SentenceP.reference,
    ])
    def get(request):
        Agent.get_or_create(request.META['HTTP_USER_AGENT'])
        sentence = Sentence.get_random_sentence(**request.d.dict())
        return sentence.d()

    @staticmethod
    @Analyse.r(b=[
        SentenceP.author,
        SentenceP.reference,
        P('sentences', '句子列表').process(list),
        SentenceP.tags,
    ])
    @Auth.require_login
    def post(request):
        author = request.d.author
        reference = request.d.reference
        sentences = request.d.sentences
        tags = request.d.tags
        user = request.user

        failure_list = []
        success_list = []
        failure_num = 0
        success_num = 0
        for sentence in sentences:
            try:
                sentence = Sentence.create(sentence, author, reference, tags, user)
                success_list.append(sentence.d())
                success_num += 1
            except Exception:
                failure_list.append(sentence)
                failure_num += 1
        return dict(
            failure_num=failure_num,
            success_num=success_num,
            failure_list=failure_list,
            success_list=success_list,
        )

    @staticmethod
    @Analyse.r(b=[P('sid', '句子ID'), SentenceP.tags])
    @Auth.require_login
    def put(request):
        sid = request.d.sid
        tags = request.d.tags
        user = request.d.user

        sentence = Sentence.get_sentence_by_id(sid)
        if sentence.owner != user:
            raise SentenceError.NOT_BELONG('无法添加标签')
        sentence.union_tags(tags)


class TagView(View):
    @staticmethod
    @Analyse.r(q=[
        P('page', '页码').default(0).process(int),
        P('count', '每页数目').default(0).process(int)
    ])
    def get(request):
        tags = Tag.get_tags(**request.d.dict('page', 'count'))
        return [o_tag.d() for o_tag in tags]

    @staticmethod
    @Analyse.r(b=[P('tags', '标签列表').process(list)])
    @Auth.require_login
    def post(request):
        tags = request.d.tags

        failure_list = []
        success_list = []
        failure_num = 0
        success_num = 0
        for tag in tags:
            try:
                tag = Tag.create(tag)
                success_num += 1
                success_list.append(tag.d())
            except Exception:
                failure_num += 1
                failure_list.append(tag)

        return dict(
            failure_num=failure_num,
            success_num=success_num,
            failure_list=failure_list,
            success_list=success_list,
        )
