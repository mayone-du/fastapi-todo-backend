import graphene
from database.database import Base, db, engine
from fastapi import HTTPException, status
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField
from graphql_relay import from_global_id
from jose import JWTError, jwt
from models.custom_user import CustomUserModel
from settings.envs import ALGORITHM, SECRET_KEY

from .custom_user import CreateCustomUser, CustomUserNode
from .task import CreateTask, DeleteTask, TaskNode, UpdateTask
from .token import CreateAccessToken, CreateRefreshToken


class Query(graphene.ObjectType):
    current_user = graphene.Field(CustomUserNode)
    user = graphene.Field(CustomUserNode, id=graphene.NonNull(graphene.ID))
    all_users = SQLAlchemyConnectionField(CustomUserNode)
    all_tasks = SQLAlchemyConnectionField(TaskNode)

    def resolve_current_user(self, info):
        try:
            # headersのauthorizationからjwtを取得
            headers = dict(info.context['request']['headers'])
            token = headers[b'authorization'].decode()[
                7:]  # Bearer の文字列を半角空白含めて削除
            # トークンの内容を取得
            payload: dict = jwt.decode(token,
                                       SECRET_KEY,
                                       algorithms=[ALGORITHM])
            ulid = payload.get('ulid')
            # ulidに紐づくユーザーを返却
            return CustomUserNode.get_query(info).filter(
                CustomUserModel.ulid == ulid).first()
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # idからユーザーを取得
    def resolve_user(self, info, id):
        query = CustomUserNode.get_query(info)
        # 受け取ったidと一致するUserオブジェクトを返却
        return query.filter(CustomUserModel.id == from_global_id(id)[1]).first()

    # すべてのユーザーを取得
    def resolve_all_users(self, info):
        query = CustomUserNode.get_query(info)
        return query.all()

    # すべてのタスクを取得
    def resolve_all_tasks(self, info):
        query = TaskNode.get_query(info)
        return query.all()


class Mutation(graphene.ObjectType):
    create_user = CreateCustomUser.Field()
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()

    # auth
    create_access_token = CreateAccessToken.Field()
    create_refresh_token = CreateRefreshToken.Field()
    # get_access_token =
