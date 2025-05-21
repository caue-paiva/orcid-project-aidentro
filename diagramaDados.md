erDiagram
    PERSON {
      varchar orcid_id PK "required"
      varchar full_name      "required"
      varchar credit_name    "required"
      text    biography
    }
    ADDRESS {
      int     id PK
      varchar orcid_id FK "references PERSON(orcid_id)"
      varchar country         "required"
      varchar region          "required"
      varchar address_type
    }
    EMAIL {
      int     id PK
      varchar orcid_id FK "references PERSON(orcid_id)"
      varchar email_address   "required"
      varchar domain
    }
    EXTERNAL_IDENTIFIER {
      int     id PK
      varchar orcid_id FK "references PERSON(orcid_id)"
      varchar identifier_type  "required"
      varchar identifier_value "required"
      varchar relationship
    }
    OTHER_NAME {
      int     id PK
      varchar orcid_id FK "references PERSON(orcid_id)"
      varchar other_name      "required"
      varchar name_type
    }
    RESEARCHER_URL {
      int     id PK
      varchar orcid_id FK "references PERSON(orcid_id)"
      varchar url             "required"
      varchar description
    }
    KEYWORD {
      int     id PK
      varchar orcid_id FK "references PERSON(orcid_id)"
      varchar keyword         "required"
    }
    EDUCATION {
      int       id PK
      varchar   orcid_id FK         "references PERSON(orcid_id)"
      varchar   organization         "required"
      varchar   city                 "required"
      varchar   country              "required"
      varchar   department
      varchar   role
      date      start_date
      date      end_date
      varchar   link
      datetime  added_date           "required"
      datetime  last_modified_date   "required"
      varchar   source               "required"
    }
    EMPLOYMENT {
      int       id PK
      varchar   orcid_id FK         "references PERSON(orcid_id)"
      varchar   organization         "required"
      varchar   city                 "required"
      varchar   country              "required"
      varchar   department
      varchar   title
      date      start_date
      date      end_date
      varchar   source               "required"
      varchar   link
    }
    PEER_REVIEW {
      int       id PK
      varchar   orcid_id FK         "references PERSON(orcid_id)"
      varchar   role                 "required"
      varchar   review_type          "required"
      date      review_date          "required"
      varchar   organization         "required"
      varchar   subject
      varchar   source               "required"
      varchar   link
    }
    WORK {
      int       id PK
      varchar   orcid_id FK         "references PERSON(orcid_id)"
      varchar   type                 "required"
      varchar   title                "required"
      varchar   institution
      date      publication_date
      varchar   link
      text      citation
      varchar   language
      varchar   doi
      varchar   source               "required"
      text      contributors
      varchar   url
      text      description
      datetime  added_date           "required"
      datetime  last_modified_date   "required"
    }
    METRIC {
      int       id PK
      int       work_id FK         "references WORK(id)"
      varchar   name                 "required"
      int       value                "required"
      datetime  timestamp            "required"
    }
    EXPORT_JOB {
      int       id PK
      int       work_id FK         "references WORK(id)"
      datetime  timestamp            "required"
      varchar   format               "required"
      varchar   status               "required"
    }

