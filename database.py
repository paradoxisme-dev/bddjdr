from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime


db_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = db_proxy
        legacy_table_names = False  # Use snake_case for table names


class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True, null=True)
    password_hash = CharField(null=True)
    is_admin = BooleanField(default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class OauthIdentity(BaseModel):
    service = CharField() # Discord, Google, etc.
    service_user_id = CharField() # The user ID from the OAuth provider
    user = ForeignKeyField(User, backref='oauth_identities') # Link to the User model


class Game(BaseModel):
    name = CharField(unique=True)
    description = TextField(null=True)


class GameProposal(BaseModel):
    name = CharField()
    description = TextField(null=True)
    proposer = ForeignKeyField(User, backref='proposed_games')
    created_at = DateTimeField(default=datetime.datetime.now)
    approved = BooleanField(default=False)  # Indique si la proposition a été approuvée par un admin
    approved_by = ForeignKeyField(User, backref='approved_games', null=True)  # Lien vers l'utilisateur qui a approuvé la proposition, si applicable
    approved_at = DateTimeField(null=True)  # Date d'approbation de la proposition, si applicable
    approved_version = ForeignKeyField(Game, backref='proposed_versions', null=True)  # Lien vers la version approuvée du jeu, si applicable


class UserGameLinkType(BaseModel):
    name = CharField(unique=True)  # 'player', 'gm', 'interested', 'possible', 'hate', 'like', etc.
    description = TextField(null=True)


class UserGame(BaseModel):
    user = ForeignKeyField(User, backref='games')
    game = ForeignKeyField(Game, backref='users')
    link_type = ForeignKeyField(UserGameLinkType, backref='user_games')
    details = TextField(null=True)  # Détails supplémentaires sur la relation (ex: "J'ai joué à ce jeu pendant 2 ans", "Je suis intéressé mais je n'ai jamais joué", etc.)


class Ressource(BaseModel):
    name = CharField(unique=True)
    description = TextField(null=True)
    url = CharField(null=True)  # URL de la ressource
    game = ForeignKeyField(Game, backref='resources', null=True)  # Lien vers le jeu associé, si applicable


class GameSessionLocation(BaseModel):
    name = CharField(unique=True)
    is_online = BooleanField(default=False)  # Indique si le lieu est en ligne ou physique
    referent_user = ForeignKeyField(User, backref='locations')  # User référent pour ce lieu
    details = TextField(null=True)  # Détails supplémentaires sur le lieu (adresse, lien de visioconférence, etc.)


class GameSessionPoll(BaseModel):
    game = ForeignKeyField(Game, backref='sessions')
    open_for_proposals = BooleanField(default=True)  # Indique si les propositions sont encore ouvertes
    end_date = DateTimeField()  # Date limite pour les propositions et les votes
    location = ForeignKeyField(GameSessionLocation, backref='sessions')  # Lieu de la session


class GameSessionPollUser(BaseModel):
    session = ForeignKeyField(GameSessionPoll, backref='participants')
    user = ForeignKeyField(User, backref='game_sessions')
    role = CharField()  # 'player' or 'gm' 


class GameSessionProposition(BaseModel):
    session = ForeignKeyField(GameSessionPoll, backref='elements')
    user = ForeignKeyField(User, backref='propositions')
    proposed_date = DateTimeField()
    proposed_time = TimeField() # durée de la session
    location = ForeignKeyField(GameSessionLocation, backref='propositions', null=True)


class GameSessionVote(BaseModel):
    session = ForeignKeyField(GameSessionProposition, backref='votes')
    user = ForeignKeyField(User, backref='votes')
    vote = IntegerField()  # 1 for upvote, -1 for downvote


class GameSession(BaseModel):
    session_poll = ForeignKeyField(GameSessionPoll, backref='final_session')
    scheduled_date = DateTimeField()
    scheduled_time = TimeField() # durée de la session


class GameSessionComment(BaseModel):
    session = ForeignKeyField(GameSession, backref='comments')
    user = ForeignKeyField(User, backref='game_sessions_final')
    role = CharField()  # 'player' or 'gm'
    comment = TextField()


tables = [
    User,
    OauthIdentity,
    Game,
    UserGameLinkType,
    UserGame,
    Ressource,
    GameSessionLocation,
    GameSessionPoll,
    GameSessionProposition,
    GameSessionVote,
    GameSession,
    GameSessionComment,
]


def initialize_database():
    db = SqliteDatabase('app.db')
    db_proxy.initialize(db)
    db.connect()
    db.create_tables(tables)


if __name__ == '__main__':
    initialize_database()
