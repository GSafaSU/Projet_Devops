*** Settings ***
Documentation     Tests d'acceptation de l'API du TP : on la teste de l'extérieur, comme un utilisateur.
Library           RequestsLibrary
Library           String
Suite Setup       Attendre que l'API soit prête


*** Variables ***
# Adresse par défaut : le Service de l'API dans le cluster Kind
${ADRESSE}        http://localhost:30080


*** Test Cases ***
L'API est vivante
    ${reponse}=    GET    ${ADRESSE}/health    expected_status=200
    Should Be Equal    ${reponse.json()}[status]    ok

L'API est prête et joint sa base
    ${reponse}=    GET    ${ADRESSE}/ready    expected_status=200
    Should Be Equal    ${reponse.json()}[status]    ready

Une tâche créée apparaît dans la liste
    ${suffixe}=    Generate Random String    8
    ${titre}=    Set Variable    Test Robot ${suffixe}
    ${corps}=    Create Dictionary    title=${titre}
    ${reponse}=    POST    ${ADRESSE}/tasks    json=${corps}    expected_status=201
    Should Be Equal    ${reponse.json()}[title]    ${titre}
    ${liste}=    GET    ${ADRESSE}/tasks    expected_status=200
    Should Contain    ${liste.text}    ${titre}

Les mesures sont publiées pour Prometheus
    ${reponse}=    GET    ${ADRESSE}/metrics    expected_status=200
    Should Contain    ${reponse.text}    http_requests_total

Une tâche sans titre est refusée
    ${corps}=    Create Dictionary
    POST    ${ADRESSE}/tasks    json=${corps}    expected_status=422


*** Keywords ***
Attendre que l'API soit prête
    Wait Until Keyword Succeeds    60s    2s    GET    ${ADRESSE}/ready    expected_status=200