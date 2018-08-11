from flask import Blueprint
from scheduler.schema import schema
from flask_graphql import GraphQLView
from flask_jwt_extended import (
    jwt_required,
)
from flask_cors import CORS

graphql_bp = Blueprint('graphql', __name__, url_prefix='/graphql')
CORS(graphql_bp)

def graphql_view():
    view = GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
    return jwt_required(view)


graphql_bp.add_url_rule('/',
    view_func=graphql_view()
)