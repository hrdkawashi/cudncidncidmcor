from functions.base import TelethonFunction
from functions.flood import Flood

class FloodFunc(TelethonFunction):
    """Спам"""

    def execute(self):
        flood = Flood(self.storage, self.settings)

        flood.ask()
        flood.start_processes()

