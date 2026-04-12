import configparser
import inspect

config = None

class MyError():

  def __init__(self, et):
    self.config = configparser.RawConfigParser()
    self.config.read('ErrorMessages.properties')
    self.errorType = et

  def newError(self, koption, key, line=None, column=None, **data):
    message = ''
  
    if(koption):
      return key
    else:
      if(line != None and column != None):
        message = message + f"Erro[{line}][{column}]: "
      if(key):
        message = message + self.config.get(self.errorType, key)
      if(data):
        extras = ", ".join([f"{k}: {v}" for k, v in data.items()])
        message += f" {extras}"

    # print(message)
      return message

