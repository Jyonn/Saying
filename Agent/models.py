import hashlib

from SmartDjango import models, E


@E.register(id_processor=E.idp_cls_prefix())
class AgentError:
    NOT_FOUND = E("找不到代理")
    CREATE = E("新建代理失败")


class Agent(models.Model):
    agent = models.CharField(
        max_length=1024,
        null=False,
    )

    agent_key = models.CharField(
        max_length=64,
        unique=True,
        null=False,
    )

    visit_times = models.IntegerField()

    @classmethod
    def get(cls, agent_key):
        try:
            agent = cls.objects.get(agent_key=agent_key)
            agent.visit_times += 1
            agent.save()
            return agent
        except cls.DoesNotExist:
            raise AgentError.NOT_FOUND

    @classmethod
    def get_or_create(cls, agent: str):
        md5 = hashlib.md5()
        md5.update(agent.encode('utf-8'))
        agent_key = md5.hexdigest()

        try:
            return cls.get(agent_key=agent_key)
        except E as e:
            if not e.eis(AgentError.NOT_FOUND):
                raise e

        try:
            agent = cls.objects.create(
                agent_key=agent_key,
                agent=agent,
                visit_times=1,
            ).save()
            return agent
        except Exception:
            raise AgentError.CREATE
