from buildsrht.types import JobStatus, OAuthToken, User
from flask import session
from srht.config import cfg
from srht.database import DbSession
from srht.flask import SrhtFlask
from srht.oauth import AbstractOAuthService, DelegatedScope

db = DbSession(cfg("builds.sr.ht", "connection-string"))
db.init()

client_id = cfg("builds.sr.ht", "oauth-client-id")
client_secret = cfg("builds.sr.ht", "oauth-client-secret")

class BuildOAuthService(AbstractOAuthService):
    def __init__(self):
        super().__init__(client_id, client_secret, delegated_scopes=[
            DelegatedScope("jobs", "build jobs", True),
        ], user_class=User, token_class=OAuthToken)

class BuildApp(SrhtFlask):
    def __init__(self):
        super().__init__("builds.sr.ht", __name__,
                oauth_service=BuildOAuthService())

        from buildsrht.blueprints.api import api
        from buildsrht.blueprints.jobs import jobs
        from buildsrht.blueprints.secrets import secrets

        self.register_blueprint(api)
        self.register_blueprint(jobs)
        self.register_blueprint(secrets)

        @self.context_processor
        def inject():
            return { "JobStatus": JobStatus }

app = BuildApp()
