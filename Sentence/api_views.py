from django.views import View

from Base.decorator import require_post, require_json, require_login, require_put, require_get
from Base.error import Error
from Base.response import response, error_response
from Sentence.models import Sentence, Tag


class SentenceView(View):
    @staticmethod
    @require_get([{
        "value": 'max_length',
        "default": True,
        "default_value": 0,
        "process": int,
    }, {
        "value": 'consider_author',
        "default": True,
        "default_value": 0,
        "process": bool,
    }, {
        "value": 'tags',
        "default": True,
        "default_value": [],
        "process": Tag.list_to_o_tag_list,
    }])
    def get(request):
        max_length = request.d.max_length
        consider_author = request.d.consider_author
        tags = request.d.tags
        ret = Sentence.get_random_sentence(max_length, consider_author, tags)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_sentence = ret.body
        if not isinstance(o_sentence, Sentence):
            return error_response(Error.STRANGE)
        return response(body=o_sentence.to_dict())

    @staticmethod
    @require_json
    @require_post([
        ('author', None, ''),
        ('reference', None, ''),
        {
            "value": 'sentences',
            "process": list
        }, {
            "value": 'tags',
            "default": True,
            "default_value": [],
            "process": Tag.list_to_o_tag_list
        }])
    @require_login
    def post(request):
        author = request.d.author
        reference = request.d.reference
        sentences = request.d.sentences
        tags = request.d.tags
        o_user = request.user

        failure_list = []
        success_list = []
        failure_num = 0
        success_num = 0
        for sentence in sentences:
            ret = Sentence.create(sentence, author, reference, tags, o_user)
            if ret.error is not Error.OK:
                failure_list.append(sentence)
                failure_num += 1
            else:
                o_sentence = ret.body
                if not isinstance(o_sentence, Sentence):
                    return error_response(Error.STRANGE)
                success_list.append(o_sentence.to_dict())
                success_num += 1
        return response(body=dict(
            failure_num=failure_num,
            success_num=success_num,
            failure_list=failure_list,
            success_list=success_list,
        ))

    @staticmethod
    @require_json
    @require_put(['sid', {"value": 'tags', "process": Tag.list_to_o_tag_list}])
    @require_login
    def put(request):
        sid = request.d.sid
        tags = request.d.tags
        o_user = request.d.user

        ret = Sentence.get_sentence_by_id(sid)
        if ret.error is not Error.OK:
            return error_response(ret)
        o_sentence = ret.body
        if not isinstance(o_sentence, Sentence):
            return error_response(Error.STRANGE)

        if o_sentence.owner != o_user:
            return error_response(Error.NOT_BELONG, append_msg='，无法添加标签')
        o_sentence.union_tags(tags)

        return response()


class TagView(View):
    @staticmethod
    @require_get([{
        "value": 'page',
        "default": True,
        "default_value": 0,
        "process": int,
    }, {
        "value": 'count',
        "default": True,
        "default_value": 0,
        "process": int,
    }])
    def get(request):
        page = request.d.page
        count = request.d.count
        ret = Tag.get_tags(page, count)
        if ret.error is not Error.OK:
            return error_response(ret)
        tags = ret.body
        tag_list = [o_tag.to_dict() for o_tag in tags]
        return response(body=tag_list)

    @staticmethod
    @require_post([{"value": 'tags', "process": list}])
    @require_login
    def post(request):
        tags = request.d.tags

        failure_list = []
        success_list = []
        failure_num = 0
        success_num = 0
        for tag in tags:
            ret = Tag.create(tag)
            if ret.error is not Error.OK:
                failure_num += 1
                failure_list.append(tag)
            else:
                o_tag = ret.body
                if not isinstance(o_tag, Tag):
                    return error_response(Error.STRANGE)
                success_num += 1
                success_list.append(o_tag.to_dict())

        return response(body=dict(
            failure_num=failure_num,
            success_num=success_num,
            failure_list=failure_list,
            success_list=success_list,
        ))
