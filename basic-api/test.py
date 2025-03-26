import requests

orcid_id = "0000-0003-1574-0784" 
url = f"https://pub.orcid.org/v3.0/{orcid_id}"

headers = {
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    nome = data['person']['name']['given-names']['value']
    sobrenome = data['person']['name']['family-name']['value']
    print(f"Nome completo: {nome} {sobrenome}")
else:
    print(f"Erro na requisição: {response.status_code}")