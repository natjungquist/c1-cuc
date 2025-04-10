# TODO

class CallHandler:

  def __init__(self, name):
    self.UnityId = ""     # id in CUC
    self.Name = name
    self.Site = ""
    self.PilotIdentifierList = 0
    self.OperatorExtension = 0
    self.BusinessHoursWelcomeGreetingFilename = ""
    self.BusinessHoursMainMenuCustomPromptFilename = "" 
    self.BusinessHoursKeyMapping = ""                    
    self.BusinessHoursKeyMappingEnabled = ""                
    self.AfterHoursWelcomeGreetingFilename = ""             
    self.AfterHoursMainMenuCustomPromptFilename = ""        
    self.AfterHoursKeyMapping = ""                          
    self.AfterHoursKeyMappingEnabled = "" 

  def get_id(self):
    return self.UnityId
  
  def get_name(self):
    return self.Name