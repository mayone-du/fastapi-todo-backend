import graphene
from database.database import db_session
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay.node.node import from_global_id
from libs.auth import get_current_custom_user
from libs.decorators import login_required
from models.task import TaskModel
from pydantic.main import BaseModel

# class TaskSchema(BaseModel):
#     class Config:
#         orm_mode=True

class TaskNode(SQLAlchemyObjectType):
    class Meta:
        model = TaskModel
        interfaces = (graphene.relay.Node,)

# class TaskConnections(graphene.relay.Connection):
#     class Meta:
#         node = TaskNode



# タスクの作成
class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=False)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        try:
            # 完了フラグはデフォルトでFalseに設定
            db_task = TaskModel(title=kwargs.get('title'),
                                    content=kwargs.get('content'),
                                    task_creator_ulid=get_current_custom_user(info).ulid,
                                    is_done=False)
            db_session.add(db_task)
            db_session.commit()
            ok = True
            return CreateTask(ok=ok)
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()


# タスクの更新
class UpdateTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        is_done = graphene.Boolean(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # idから取得したtaskを更新
            current_task: TaskModel = TaskNode.get_query(info).filter(TaskModel.id==from_global_id(kwargs.get('id'))[1]).first()
            # TODO: リファクタリング
            current_task.title=kwargs.get('title')
            current_task.content=kwargs.get('content')
            current_task.is_done=kwargs.get('is_done')
            db_session.commit()
            ok = True
            return UpdateTask(ok=ok)
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()


# タスクの削除
class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            task: TaskNode= TaskNode.get_query(info).filter(TaskModel.id==from_global_id(kwargs.get('id'))[1]).first()
            db_session.delete(task)
            db_session.commit()
            ok = True
            return DeleteTask(ok=ok)
        except:
            raise
        finally:
            pass

