from flask_migrate import Migrate

from informatics_front.utils.services.internal_rmatics import InternalRmatics
from informatics_front.utils.tokenizer.tokenizer import Tokenizer
from informatics_front.utils.services.mailer import Gmail

internal_rmatics = InternalRmatics()
tokenizer = Tokenizer()
gmail = Gmail()
migrate = Migrate()
