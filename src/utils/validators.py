import re
from datetime import datetime

class validators:

    def date_validator(date):
        try:
            
            if (date == None or len(date) == 0):
                return True
            
            regex = re.compile(r"^(\d{2})[/](\d{2})[/-](\d{4})$")
            match = regex.match(date)
            
            if not match:
                return False

            dia, mes, anio = map(int, match.groups())
            
            datetime(anio, mes, dia)
            return True  

        except Exception as e:
            return False