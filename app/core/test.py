import datetime
from zipfile import Path

from conf.settings import settings

BASE_URL = settings.BASE_URL

print(f"{BASE_URL}/campaigns/{2}/donation")
