*** Settings ***
Library         Selenium2Library  timeout=10  implicit_wait=0.5
Test Setup      Open Browser  http://localhost:11111/
Test Teardown   Close All Browsers


*** Test Cases ***
Front page
    Page Should Contain  about
    Page Should Contain  preferences

About page
    Click Element  link=about
    Page Should Contain  Why use Searx?
    Page Should Contain Element  link=search engines

Preferences page
    Click Element  link=preferences
    Page Should Contain  Preferences
    Page Should Contain  Default categories
    Page Should Contain  Currently used search engines
    Page Should Contain  dummy_dummy
    Page Should Contain  general_dummy

Switch category
    Go To  http://localhost:11111/preferences
    Page Should Contain Checkbox  category_general
    Page Should Contain Checkbox  category_dummy
    Click Element  xpath=//*[.="general"]
    Click Element  xpath=//*[.="dummy"]
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Checkbox Should Not Be Selected  category_general
    Checkbox Should Be Selected  category_dummy

Change locale
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Select From List  locale  hu
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Page Should Contain  rólunk
    Page Should Contain  beállítások

Change method
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Select From List  method  GET
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    List Selection Should Be  method  GET
    Select From List  method  POST
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    List Selection Should Be  method  POST

Change theme
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  theme  default
    Select From List  theme  oscar
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    List Selection Should Be  theme  oscar

Change safesearch
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  safesearch  Moderate
    Select From List  safesearch  Strict
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    List Selection Should Be  safesearch  Strict

Change image proxy
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  image_proxy  Disabled
    Select From List  image_proxy  Enabled
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    List Selection Should Be  image_proxy  Enabled

Change search language
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  language  Automatic
    Select From List  language  Turkish (Turkey) - tr_TR
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    List Selection Should Be  language  Turkish (Turkey) - tr_TR

Change autocomplete
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  autocomplete  -
    Select From List  autocomplete  google
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    List Selection Should Be  autocomplete  google

Change allowed/disabled engines
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Page Should Contain  Engine name
    Checkbox Should Not Be Selected  id=engine_general_general_dummy
    Checkbox Should Not Be Selected  id=engine_dummy_dummy_dummy
    Click Element  id=engine_general_general_dummy
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Page Should Contain  Engine name
    Checkbox Should Be Selected  id=engine_general_general_dummy
    Checkbox Should Not Be Selected  id=engine_dummy_dummy_dummy

Block a plugin
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  theme  default
    Select From List  theme  oscar
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    List Selection Should Be  theme  oscar
    Page Should Contain  Plugins
    Click Link  Plugins
    Click Element  xpath=//label[@for='plugin_HTTPS_rewrite']
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Go To  http://localhost:11111/preferences
    Page Should Contain  Plugins
    Click Link  Plugins
    Checkbox Should Be Selected  id=plugin_HTTPS_rewrite
