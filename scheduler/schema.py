import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .models import Ticket as TicketModel
from .models import User as UserModel


# models
class Ticket(SQLAlchemyObjectType):
    class Meta:
        model = TicketModel
        interfaces = (relay.Node, )


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )


# connections
class TicketConnection(relay.Connection):
    class Meta:
        node = Ticket


class UserConnection(relay.Connection):
    class Meta:
        node = User


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    all_tickets = SQLAlchemyConnectionField(TicketConnection)
    all_users = SQLAlchemyConnectionField(UserConnection)

schema = graphene.Schema(query=Query)