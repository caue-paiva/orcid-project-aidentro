# API do ORCID

## O que é uma API?

API (Application Programming Interface), ou Interface de Programação de Aplicações, é um conjunto de regras e endpoints que permitem que diferentes sistemas ou aplicações se comuniquem entre si. 

APIs facilitam o consumo de dados ou serviços de terceiros sem que seja necessário conhecer a estrutura interna do sistema, apenas enviando requisições e recebendo respostas via protocolos como HTTP.

Na prática, APIs são utilizadas para:
- Acessar dados de plataformas externas (ex: dados de redes sociais, clima, bancos).
- Automatizar integrações entre aplicações.
- Construir serviços que se comunicam com sistemas externos de forma padronizada.

## Como fazer uma requisição na API pública do ORCID?

### Endpoint Base

https://pub.orcid.org/v3.0/


### Exemplos de Requisições GET

Usando `curl` (linha de comando):

```bash
curl -H "Accept: application/json" https://pub.orcid.org/v3.0/0000-0003-1574-0784
```

Usando `javascript` (node):

```javascript
const orcidId = "0000-0003-1574-0784";
const url = `https://pub.orcid.org/v3.0/${orcidId}`;

fetch(url, {
    method: 'GET',
    headers: {
        'Accept': 'application/json'
    }
})
.then(response => {
    if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
    }
    return response.json();
})
.then(data => {
    const nome = data.person.name['given-names'].value;
    const sobrenome = data.person.name['family-name'].value;
    console.log(`Nome completo: ${nome} ${sobrenome}`);
})
.catch(error => {
    console.error('Erro ao buscar dados do ORCID:', error);
});
```

Usando `python`:

```python
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
```

Caso queira executar os códigos, eles estão também na pasta `/basic-api`.

## Tutoriais

Veja tutoriais completos [aqui](https://info.orcid.org/documentation/api-tutorials/).