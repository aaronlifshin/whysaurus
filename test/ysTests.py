import os
import sys
import httplib
import base64
import json
import new
import unittest
import sauceclient
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from sauceclient import SauceClient
from pageobjects import current_driver, use_sauce, css_locators, id_locators
from pageobjects.pages_elements import PageAreaMainMenu, HomePage, PointPage

browsers = [{"platform": "Mac OS X 10.9",
             "browserName": "chrome",
             "version": "31"}]

USERNAME = os.environ.get('SAUCE_USERNAME')
ACCESS_KEY = os.environ.get('SAUCE_ACCESS_KEY')

if USERNAME == None:
    print 'SAUCE_USERNAME environment var needs to be set'
    exit()

if ACCESS_KEY == None:
    print 'SAUCE_ACCESS_KEY environment var needs to be set'
    exit()
    
sauce = SauceClient(USERNAME, ACCESS_KEY)

def on_platforms(platforms):
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = "%s_%s" % (base_class.__name__, i + 1)
            module[name] = new.classobj(name, (base_class,), d)
    return decorator

@on_platforms(browsers)
class SauceSampleTest(unittest.TestCase):  
  pointUrlsToDelete = []
  def setUp(self):
    self.desired_capabilities['name'] = self.id()

    self.driver = current_driver.connect(USERNAME, ACCESS_KEY, self.desired_capabilities)    
    self.driver.get('http://whysaurustest.appspot.com/')
    assert "Whysaurus" in self.driver.title
       
    mainMenu = PageAreaMainMenu()     
    mainMenu.loginToPublic('user2')
      
  def test_addPoint(self):
    #generate a new point title
    newTitle = 'RobotTestPoint ' + str(datetime.now())
    
    url = HomePage().publish(newTitle)    
    
    # should be on the point page after publish    
    PointPage("__str__").confirmTitle(newTitle) # __str__ is passed as a no-op test method
    
    self.pointUrlsToDelete.append(url)
       
  def test_logOut(self):
    mainMenu = PageAreaMainMenu() 
    mainMenu.logout()    
    
    assert "SIGN IN" in  mainMenu.userNameOrSignIn.text
    
  def test_createWithSupporting(self):
    newThesis = 'Robot Thesis ' + str(datetime.now())
    newSupport = 'Robot Support ' + str(datetime.now())
    
    url = HomePage().publish(newThesis)    
    self.pointUrlsToDelete.append(url)
        
    # Now we are on the point page.  Add Support    
    supportingUrl = PointPage("__str__").addSupporting(newSupport)    
    self.pointUrlsToDelete.append(supportingUrl)

  def tearDown(self):
    if self.pointUrlsToDelete:
      mm = PageAreaMainMenu()
      if mm.is_logged_in:       
        mm.logout()
      mm.loginToPublic('adminuser')
    
    for url in self.pointUrlsToDelete:
      print "Trying to delete URL: " + url
      try:

        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, id_locators['PointPage.agreeButton'])))
        print "POINT PAGE DELETE"
        
        PointPage("__str__").delete()
        print "Finished deleting that one" 
      except:
        print "Could not delete that one"
      
    try:
      if use_sauce:
        print("Link to your job: https://saucelabs.com/jobs/%s" % self.driver.session_id)
      
        if sys.exc_info() == (None, None, None):
            sauce.jobs.update_job(self.driver.session_id, passed=True)
        else:
            sauce.jobs.update_job(self.driver.session_id, passed=False)
            
    finally:
        self.driver.quit()
