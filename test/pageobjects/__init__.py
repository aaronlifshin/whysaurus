from pageobjects.webdrivers import RemoteDriver, LocalChromeDriver

use_sauce = False
if use_sauce:
  current_driver = RemoteDriver()
else:
  current_driver = LocalChromeDriver()


css_locators = {}
css_locators['main_menu.userNameOrSignIn'] = '.userMenuArea > .dropdown-toggle'
css_locators['main_menu.loginWithEmail'] = '.userMenuArea .loginWithEmail'
css_locators['main_menu.logout'] = '#userMenuSignedIn li:last-child a'
css_locators['main_menu.homeButton'] = '#homeNav span'
css_locators['main_menu.goToPublicArea'] = '[data-area="public"]'
css_locators['EmailSignInDialog.title'] = '#frm_emailLoginDialog .modal-header h3'
css_locators['PointDialog.title'] = '#pointDialog .modal-header h3'

css_locators['PointPage.mainPointTitle'] = '.mainPointTitleText'
css_locators['PointPage.addSupportingPoint'] = '[name="createLinked"][data-linktype="supporting"]'
css_locators['PointPage.supportingPointList'] = '#supporting_nonzeroPoints > .pointCard'

css_locators['HomePage.pointList'] = '#recentActivityArea > div'
css_locators['HomePage.newPointcall'] =  '.newPointCallTitle'

id_locators = {}
id_locators['EmailSignInDialog.username'] = 'login_userEmail'
id_locators['EmailSignInDialog.password'] = 'login_userPassword'
id_locators['EmailSignInDialog.submit'] =  'submit_emailLoginDialog'
id_locators['HomePage.newPointTitle'] = 'newPointTitle'
id_locators['HomePage.mainPagePublish'] = 'mainPagePublish'
id_locators['HomePage.areaLine'] = 'areaLine'
id_locators['PointPage.agreeButton'] = 'upVote'
id_locators['PointPage.adminMenu'] = 'pointAdminMenu'
id_locators['PointPage.delete'] = 'deletePoint'
id_locators['PointPage.addSupportWhenNonZero'] = 'supporting_addPointWhenNonZero'
id_locators['PointPage.addSupportWhenZero'] = 'supporting_addPointWhenZero'

id_locators['PointDialog.titleInput'] = 'title_pointDialog'
id_locators['PointDialog.submit'] = 'submit_pointDialog'





