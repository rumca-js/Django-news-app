from pathlib import Path
from .threads import *
from .basictypes import *

__version__ = "0.0.1"


class Configuration(object):
   obj = None

   def __init__(self):
       self.directory = Path(".").resolve()
       self.links_directory = self.directory / "link_files"
       self.version = __version__
       self.server_log_file = self.directory / "server_log_file.txt"

       self.enable_logging()

   def get_object():
       if not Configuration.obj:
           Configuration.obj = Configuration()
       return Configuration.obj

   def enable_logging(self):
       logging.shutdown()

       self.server_log_file.unlink(True)

       logging.basicConfig(level=logging.INFO, filename=self.server_log_file)
