import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .models import Ticket as TicketModel


class Ticket(SQLAlchemyObjectType):
    class Meta:
        model = TicketModel
        interfaces = (relay.Node, )


class TicketConnection(relay.Connection):
    class Meta:
        node = Ticket


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    all_tickets = SQLAlchemyConnectionField(TicketConnection)

schema = graphene.Schema(query=Query)