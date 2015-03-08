from selenium import webdriver
from sauceclient import SauceClient
    
class RemoteDriver(object):
    # singleton
    _instance = None
    driver = None
    
    #
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RemoteDriver, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    #
    def connect(self, username, access_key, desired_capabilities):
      
      self.desired_capabilites = desired_capabilities
                             
      sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
      self.driver = webdriver.Remote(
          desired_capabilities=desired_capabilities,
          command_executor=sauce_url % (username, access_key)
      )
      self.driver.implicitly_wait(30)

      return self.driver


