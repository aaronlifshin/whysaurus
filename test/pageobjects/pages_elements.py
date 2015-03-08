import unittest
from pageobjects import remote_driver, css_locators, id_locators

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
#     PAGE ELEMENTS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class BasePageElement(object):    
  def __get__(self, obj, type=None):
    self.driver = remote_driver.driver
    if hasattr(self, 'css_selector'):
      return self.driver.find_element_by_css_selector(self.css_selector)  
    elif hasattr(self, 'id_selector'):
      return self.driver.find_element_by_id(self.id_selector)  
        
  def __set__(self, obj, val):
      pass
     
  def __delete__(self, obj):
      pass 

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
#     MAIN MENU ELEMENTS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class UserNameOrSignIn(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['main_menu.userNameOrSignIn']   
    
class LoginWithEmail(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['main_menu.loginWithEmail']
  
class LogoutMenu(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['main_menu.logout']   

class GoToPublicArea(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['main_menu.goToPublicArea']   

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
#     EMAIL SIGN IN DIALOG
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      
class Username(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['EmailSignInDialog.username']
    
  def __set__(self, obj, val):
    self.driver = remote_driver.driver    
    me = self.driver.find_element_by_id(self.id_selector)
    me.send_keys(val)
  
class Password(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['EmailSignInDialog.password']  
  
  def __set__(self, obj, val):
    self.driver = remote_driver.driver    
    me = self.driver.find_element_by_id(self.id_selector)
    me.send_keys(val)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
#     POINT DIALOG ELEMENTS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class PointDialogTitle(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['PointDialog.title'] 

class PointTitleInput(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['PointDialog.titleInput']
    
  def __set__(self, obj, val):
    self.driver = remote_driver.driver    
    me = self.driver.find_element_by_id(self.id_selector)
    me.send_keys(val)
    
class PointDialogSubmit(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['PointDialog.submit']

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
#     HOME PAGE ELEMENTS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
class NewPointTitle(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['HomePage.newPointTitle']
    
  def __set__(self, obj, val):
    self.driver = remote_driver.driver    
    me = self.driver.find_element_by_id(self.id_selector)
    me.send_keys(val)

class MainPageCall(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['HomePage.newPointcall']

class MainPagePublish(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['HomePage.mainPagePublish']
    
class MainPagePointList(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['HomePage.pointList']  
    
  def __get__(self, obj, type=None):
    self.driver = remote_driver.driver
    return self.driver.find_elements_by_css_selector(self.css_selector)
    
class AreaLine(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['HomePage.areaLine']

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
#     POINT PAGE ELEMENTS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class AgreeButton(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['PointPage.agreeButton']
    
class PointTitle(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['PointPage.mainPointTitle']

class AdminMenu(BasePageElement):
  def __init__(self):
    self.id_selector = id_locators['PointPage.adminMenu']

class DeleteButton(BasePageElement):    
  def __init__(self):  
    self.id_selector = id_locators['PointPage.delete']
    
class AddSupportingPoint(BasePageElement):
  def __init__(self):  
    self.id_selector1 = id_locators['PointPage.addSupportWhenZero']  
    self.id_selector2 = id_locators['PointPage.addSupportWhenNonZero']  
        
  def __get__(self, obj, type=None):
    self.driver = remote_driver.driver
    try: 
      button = self.driver.find_element_by_id(self.id_selector1)
      self.id_selector = self.id_selector1
      return button
    except NoSuchElementException:
      button = self.driver.find_element_by_id(self.id_selector2)
      self.id_selector = self.id_selector2
      return button 
      
class CreateNewSupportingPoint(BasePageElement):
  def __init__(self):    
    self.css_selector = css_locators['PointPage.addSupportingPoint']
    
    
  def __get__(self, obj, type=None):
    self.driver = remote_driver.driver
    
    # One of two menu items is visible
    elements = self.driver.find_elements_by_css_selector(self.css_selector)
    for e in elements:
      if e.is_displayed():
        return e
    return None
    
class SupportingPointsList(BasePageElement):
  def __init__(self):
    self.css_selector = css_locators['PointPage.supportingPointList']
  
  def __get__(self, obj, type=None):
    self.driver = remote_driver.driver
    return self.driver.find_elements_by_css_selector(self.css_selector)
      
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
#     PAGE OBJECTS, PAGE AREAS, DIALOGS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class BasePageObject(unittest.TestCase):
  pass

class EmailSignInDialog(BasePageObject):
  driver = None 
  username = Username()
  password = Password()
  
  def _init_(self):
    self.driver = remote_driver.driver

    # Check that the sign in dialog is open by looking for its title
    dlgTitle = self.driver.find_element_by_css_selector(css_locators['EmailSignInDialog.title'])
    assert "Sign In" in dlgTitle.text
        
  def submit(self):
    submitButton = remote_driver.driver.find_element_by_id(id_locators['EmailSignInDialog.submit'])
    submitButton.click()

  def login(self, username, password):   
    self.driver = remote_driver.driver
     
    self.username = username
    self.password = password
    self.submit()  
    try:
        WebDriverWait(self.driver, 7).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, css_locators['main_menu.userNameOrSignIn']), username))
    except TimeoutException:
      assert False
      
class PointDialog(BasePageObject):
  title = PointDialogTitle()
  newPointInput = PointTitleInput()
  submit = PointDialogSubmit()

  def _init_(self):
    self.driver = remote_driver.driver
    
    # Check that Create exists in the title of the dialog, for now
    # This will have to be changed when we start using it for edit    
    assert "Create " in self.title 
    
  def submitDialog(self):
    self.driver = remote_driver.driver
    
    self.submit.click()
    try:
        WebDriverWait(self.driver, 7).until(EC.invisibility_of_element_located((By.ID, "pointDialog")))
    except TimeoutException:
      assert False

# This is kind of like a page object but for the main menu
class PageAreaMainMenu(BasePageObject):
  userNameOrSignIn = UserNameOrSignIn()
  loginWithEmail = LoginWithEmail()
  logoutMenu = LogoutMenu()
  goToPublicAreaMenu = GoToPublicArea()
  
  def __init__(self):
    self.driver = remote_driver.driver
            
    # Check that the main menu is available by looking for the home navigation button
    homeText = self.driver.find_element_by_css_selector(css_locators['main_menu.homeButton'])
    assert "HOME" in homeText.text

  def goToPublicSpace(self):
    self.userNameOrSignIn.click()
    self.goToPublicAreaMenu.click()  
    self.driver.implicitly_wait(3)
            
  def login(self, username, password='a123123123'):          
    self.userNameOrSignIn.click()
    self.loginWithEmail.click()
    
    # Passing a harmless method as runTest, because we don't actually want to run a test case here,
    # but EmailSignInDialog inherits from unittest.TestCase in orde to be able to run assert
    esd = EmailSignInDialog("__str__")
    esd.login(username, password)
    
    assert username in self.userNameOrSignIn.text
      
  def loginToPublic(self, username, password='a123123123'):
    self.login(username, password)
    hp = HomePage() 
    
    # ensure we are in the public space
    if hp.currentPrivateArea() is not None:
      self.goToPublicSpace()
  
  def logout(self):
    self.userNameOrSignIn.click()
    self.logoutMenu.click()
    self.driver.implicitly_wait(3) 
    
  @property
  def is_logged_in(self):
    if self.userNameOrSignIn.text == 'SIGN IN':
      return False
    else:
      return True      
        
class HomePage(BasePageObject):
  newPointCall = MainPageCall()
  newPointTitle = NewPointTitle()
  mainPagePublish = MainPagePublish()
  pointList = MainPagePointList()
  areaLine = AreaLine()
  
  def __init__(self):
    self.driver = remote_driver.driver
            
    # Check that we are on the home page by looking for the main Call to Action
    newPointCallText = self.newPointCall.text
    assert "Make an Argument You Want to Prove" in newPointCallText
    
  def publish(self, title):
    self.newPointTitle = title
    self.mainPagePublish.click()
    try:
        WebDriverWait(self.driver, 7).until(EC.title_is(title))
        return self.driver.current_url
    except TimeoutException:
      assert False
    
  def findPoint(self, pointTitleToFind):
    for pointCard in self.pointList:
      pointTitle = pointCard.find_element_by_css_selector('.pointTitle a')
      if pointTitleToFind in pointTitle.text:
        return pointCard
    return None    
    
  def currentPrivateArea(self):
    try:
      return self.areaLine.text
    except NoSuchElementException:
      return None
      
  def goToPointInList(self, pointTitle):
    pointCard = self.findPoint(pointTitle)
    assert pointCard is not None # found the point in the list
    assert pointTitle in pointCard.find_element_by_css_selector('.pointTitle a').text
    
    pointCard.click()
    self.driver.implicitly_wait(3)
    
class PointPage(BasePageObject):
  pointTitle = PointTitle()
  agreeButton = AgreeButton()
  adminMenu = AdminMenu()
  deleteButton = DeleteButton()
  addSupportingMenu = AddSupportingPoint()
  createNewSupportingMenu = CreateNewSupportingPoint()
  supportingPointsList = SupportingPointsList()
  
  def __init__(self, *args, **kwargs):
    unittest.TestCase.__init__(self, *args, **kwargs)    
    self.driver = remote_driver.driver
            
    # Check that we are on the point page by looking for the agree button
    upVoteButtonText = self.agreeButton.text
    assert "Agree" in upVoteButtonText
    
  def confirmTitle(self, title):
    mainPointTitleText = self.pointTitle.text
    assert title in mainPointTitleText
    assert title in self.driver.title
    
  def addSupporting(self, title):
    self.addSupportingMenu.click()
    self.createNewSupportingMenu.click()
    
    pd = PointDialog("__str__") # __str__ is passed as a no-op test method
    assert "Create Supporting Point" in pd.title.text
    
    pd.newPointInput = title
    pd.submitDialog()
        
    # Find the last point and check its title
    pointCard = self.supportingPointsList[0]
    
    assert title in pointCard.text
    
    pointUrl = pointCard.find_element_by_css_selector('.pointTitle a').get_attribute("href")
    return pointUrl
  
  def delete(self):
    self.adminMenu.click()
    self.deleteButton.click()
    try:
        WebDriverWait(self.driver, 3).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')

        alert = self.driver.switch_to_alert()
        alert_text = alert.text
        assert "Deleted point" in alert_text 
        alert.accept()        
        print "alert accepted"
    except TimeoutException:
        assert False
    
    
    
    
    
    