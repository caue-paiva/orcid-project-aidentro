# Back-end

## Setup

### Requirements

1) Python and the dependencies specified in requirements.txt

2) Docker 


### Database

Run the following shell command to setup the postgres docker container

```bash
docker run -d --name {DB_NAME} -e POSTGRES_DB={DB_NAME} -e POSTGRES_USER={DB_USER} -e POSTGRES_PASSWORD={DB_PASSWORD} -p 5432:5432 postgres:15
```