import configparser
import os


class MyError:

    def __init__(self, et):
        self.config = configparser.RawConfigParser()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        prop_path = os.path.join(base_dir, "ErrorMessages.properties")

        read_files = self.config.read(prop_path, encoding="utf-8")
        if not read_files:
            self.config.read("ErrorMessages.properties", encoding="utf-8")

        self.errorType = et

    def newError(self, koption, key, line=None, column=None, **data):
        if koption:
            return key

        message = ""

        if line is not None and column is not None:
            message += f"Erro[{line}][{column}]: "

        try:
            template = self.config.get(self.errorType, key)
        except Exception:
            template = key

        # Se a mensagem tem {}, usa format.
        if "{}" in template:
            if key == "ERR-SEM-FUNC-RET-TYPE-ERROR":
                values = [data.get("valor"), data.get("para"), data.get("de")]
            elif key == "WAR-SEM-VAR-DECL-PREV":
                values = [data.get("valor"), data.get("tipo")]
            elif key == "WAR-SEM-IMP-COERC-OF-VAR":
                values = [data.get("valor"), data.get("de"), data.get("para"), data.get("valor")]
            elif key == "WAR-SEM-ATR-DIFF-TYPES-IMP-COERC-OF-FUNC-ARG":
                values = [data.get("valor"), data.get("de"), data.get("para")]
            else:
                values = list(data.values())

            values = [v for v in values if v is not None]

            try:
                message += template.format(*values)
            except Exception:
                message += template

        # Se não tem {}, mantém comportamento antigo: adiciona "valor: ..."
        else:
            message += template

            if data:
                for data_key, value in data.items():
                    message += f" {data_key}: {value}"

                # Compatibilidade com os .out antigos:
                # o myerror antigo cortava o último caractere.
                message = message[:-1]

        return message