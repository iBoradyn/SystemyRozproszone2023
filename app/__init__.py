from dotenv import load_dotenv
from flask import Flask


def create_app():
    load_dotenv()

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import competition
    app.register_blueprint(competition.bp)
    app.add_url_rule('/', endpoint='index')

    return app
