import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

from .version import __version__

from .download import *
