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