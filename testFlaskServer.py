from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
from flask_cors import CORS
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define your database model
class TaskModel(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)

# Define the GraphQL object type using SQLAlchemyObjectType
class Task(SQLAlchemyObjectType):
    class Meta:
        model = TaskModel

class Query(graphene.ObjectType):
    all_tasks = graphene.List(Task)

    def resolve_all_tasks(self, info):
        # Querying all tasks using SQLAlchemy query
        return TaskModel.query.all()

class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String()

    task = graphene.Field(Task)

    def mutate(self, info, title):
        new_task = TaskModel(title=title, completed=False)
        db.session.add(new_task)
        db.session.commit()
        return CreateTask(task=new_task)

class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        task = TaskModel.query.get(id)
        if task is not None:
            db.session.delete(task)
            db.session.commit()
            return DeleteTask(success=True)
        return DeleteTask(success=False)

class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    delete_task = DeleteTask.Field()  # Add this line to include delete mutation

schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the tables if they don't already exist
    app.run(host='0.0.0.0', port=5000, debug=False)
