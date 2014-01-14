*** Settings ***
Library         Selenium2Library  timeout=10  implicit_wait=0.5
Test Setup      Open Browser  http://localhost:11111/
Test Teardown   Close All Browsers


*** Test Cases ***
Front page
    Page Should Contain  about
    Page Should Contain  preferences

