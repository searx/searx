*** Settings ***
Library         Selenium2Library  timeout=10  implicit_wait=0.5
Test Setup      Open Browser  http://localhost:11111/
Test Teardown   Close All Browsers


*** Keywords ***
Submit Preferences
    Set Selenium Speed  2 seconds
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Set Selenium Speed  0 seconds


*** Test Cases ***
Front page
    Page Should Contain  about
    Page Should Contain  preferences

404 page
    Go To  http://localhost:11111/no-such-page
    Page Should Contain  Page not found
    Page Should Contain  Go to search page

About page
    Click Element  link=about
    Page Should Contain  Why use searx?
    Page Should Contain Element  link=search engines

Preferences page
    Click Element  link=preferences
    Page Should Contain  Preferences
    Page Should Contain  Default categories
    Page Should Contain  Currently used search engines
    Page Should Contain  dummy dummy
    Page Should Contain  general dummy

Switch category
    Go To  http://localhost:11111/preferences
    Page Should Contain Checkbox  category_general
    Page Should Contain Checkbox  category_dummy
    Click Element  xpath=//*[.="general"]
    Click Element  xpath=//*[.="dummy"]
    Submit Preferences
    Checkbox Should Not Be Selected  category_general
    Checkbox Should Be Selected  category_dummy

Change language
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Select From List  locale  hu
    Submit Preferences
    Page Should Contain  rólunk
    Page Should Contain  beállítások

Change method
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Select From List  method  GET
    Submit Preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  method  GET
    Select From List  method  POST
    Submit Preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  method  POST

Change theme
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  theme  legacy
    Select From List  theme  oscar
    Submit Preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  theme  oscar

Change safesearch
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  safesearch  None
    Select From List  safesearch  Strict
    Submit Preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  safesearch  Strict

Change image proxy
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  image_proxy  Disabled
    Select From List  image_proxy  Enabled
    Submit Preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  image_proxy  Enabled

Change search language
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  language  Default language
    Select From List  language  Türkçe (Türkiye) - tr-TR
    Submit Preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  language  Türkçe (Türkiye) - tr-TR

Change autocomplete
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  autocomplete  -
    Select From List  autocomplete  google
    Submit Preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  autocomplete  google

Change allowed/disabled engines
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Page Should Contain  Engine name
    Element Should Contain  xpath=//label[@class="deny"][@for='engine_dummy_dummy_dummy']  Block
    Element Should Contain  xpath=//label[@class="deny"][@for='engine_general_general_dummy']  Block
    Click Element  xpath=//label[@class="deny"][@for='engine_general_general_dummy']
    Submit Preferences
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Page Should Contain  Engine name
    Element Should Contain  xpath=//label[@class="deny"][@for='engine_dummy_dummy_dummy']  Block
    Element Should Contain  xpath=//label[@class="deny"][@for='engine_general_general_dummy']  \

Block a plugin
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  theme  legacy
    Select From List  theme  oscar
    Submit Preferences
    Go To  http://localhost:11111/preferences
    List Selection Should Be  theme  oscar
    Page Should Contain  Plugins
    Click Link  Plugins
    Checkbox Should Not Be Selected  id=plugin_HTTPS_rewrite
    Click Element  xpath=//label[@for='plugin_HTTPS_rewrite']
    Submit Preferences
    Go To  http://localhost:11111/preferences
    Page Should Contain  Plugins
    Click Link  Plugins
    Checkbox Should Be Selected  id=plugin_HTTPS_rewrite
