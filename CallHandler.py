# TODO

class CallHandler:

  def __init__(self, data):
    
    # from config file
    self.Name = data['Name']
    self.Site = data['Site']
    self.PilotIdentifierList = data['PilotIdentifierList']
    self.OperatorExtension = data['OperatorExtension']
    self.BusinessHoursWelcomeGreetingFilename = data['BusinessHoursWelcomeGreetingFilename']
    self.BusinessHoursMainMenuCustomPromptFilename = data['BusinessHoursMainMenuCustomPromptFilename']
    self.BusinessHoursKeyMapping = data['BusinessHoursKeyMapping']         
    self.BusinessHoursKeyMappingEnabled = True if data['BusinessHoursKeyMappingEnabled'] else False        
    self.AfterHoursWelcomeGreetingFilename = data['AfterHoursWelcomeGreetingFilename']     
    self.AfterHoursMainMenuCustomPromptFilename = data['AfterHoursMainMenuCustomPromptFilename']
    self.AfterHoursKeyMapping = data['AfterHoursKeyMapping']                         
    self.AfterHoursKeyMappingEnabled = True if data['AfterHoursKeyMappingEnabled'] else False

    # other
    self.UnityId = ""     # id in CUC
    self.prefix = self.Name[0:3]
    self.transfer_rule_extension = ""

  def get_id(self):
    return self.UnityId
  
  def get_name(self):
    return self.Name
  
  def set_transfer_rule_extension(self, extension):
    self.transfer_rule_extension = extension