# Class that represents the CallHandler object. 
# This contains all of the information need to build one handler.
# The information is populated by the customer data.

class CallHandler:

  def __init__(self, data=None):
    if data is None:
      data = {}

    # from customer data
    self.Name = data.get('Name', '')
    self.Site = data.get('Site', '')
    self.PilotIdentifierList = data.get('PilotIdentifierList', '')
    self.OperatorExtension = data.get('OperatorExtension', '')
    self.BusinessHoursWelcomeGreetingFilename = data.get('BusinessHoursWelcomeGreetingFilename', '')
    self.BusinessHoursMainMenuCustomPromptFilename = data.get('BusinessHoursMainMenuCustomPromptFilename', '')
    self.BusinessHoursKeyMapping = data.get('BusinessHoursKeyMapping', '')
    self.AfterHoursWelcomeGreetingFilename = data.get('AfterHoursWelcomeGreetingFilename', '')
    self.AfterHoursMainMenuCustomPromptFilename = data.get('AfterHoursMainMenuCustomPromptFilename', '')
    self.AfterHoursKeyMapping = data.get('AfterHoursKeyMapping', '')
                        
    # other
    self.UnityId = ''     # id in CUC
    self.prefix = self.Name[0:3] if self.Name else ''
    self.transfer_rule_extension = ''

  def get_id(self):
    return self.UnityId
  
  def set_transfer_rule_extension(self, extension):
    self.transfer_rule_extension = extension