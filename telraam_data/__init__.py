import logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

from .version import __version__

# download_segments is not unit-tested and seems to malfunction at the moment
from .download import download_one_segment, list_segments, list_segments_by_coordinates
