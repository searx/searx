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

Change language
    Page Should Contain  about
    Page Should Contain  preferences
    Go To  http://localhost:11111/preferences
    Select From List  locale  hu
    Submit Form  id=search_form
    Location Should Be  http://localhost:11111/
    Page Should Contain  rólunk
    Page Should Contain  beállítások
