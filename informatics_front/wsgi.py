import os

from informatics_front import create_app

ENV = os.getenv('FLASK_ENV', 'informatics_front.config.DevConfig')
application = create_app(ENV)

if __name__ == '__main__':
    application.run()
