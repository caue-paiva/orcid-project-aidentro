# ORCID Research Platform - Database Schema Design

## Overview

This document describes the database schema for the ORCID Research Platform, designed to support researcher identification, publication tracking, collaboration analysis, and research metrics computation.

## Core Design Principles

1. **ORCID-First Integration**: Built around ORCID identifiers as the primary researcher identification system
2. **Comprehensive Research Data**: Captures publications, affiliations, funding, and research metrics
3. **Collaboration Networks**: Enables analysis of research collaboration patterns
4. **Extensible Structure**: Designed to accommodate future research data types
5. **Performance Optimized**: Includes strategic indexes for common query patterns
6. **Privacy Aware**: Built-in privacy controls for user data visibility

## Entity Relationship Overview

```
Users (ORCID Integration)
    ├── Affiliations → Institutions
    ├── Works ← WorkAuthors (Many-to-Many with metadata)
    ├── Funding
    ├── UserResearchAreas → ResearchAreas
    ├── UserMetrics (1:1)
    ├── CollaborationNetworks (Many-to-Many self-reference)
    └── APIUsageLogs

Works
    ├── WorkAuthors → Users
    ├── Citations (self-referencing for citation relationships)
    └── Metrics integration

Supporting Entities
    ├── Institutions (with external identifiers)
    ├── ResearchAreas (hierarchical taxonomy)
    └── APIUsageLogs (system analytics)
```

## Entity Details

### 1. User Model
**Purpose**: Extended Django User model with ORCID integration and research profile data.

**Key Features**:
- UUID primary keys for better security and scalability
- ORCID ID validation with regex patterns
- Encrypted token storage for API access
- Privacy controls for profile visibility
- Comprehensive profile information

**Relationships**:
- One-to-Many: Affiliations, Works (through WorkAuthor), Funding, Research Areas
- One-to-One: UserMetrics
- Many-to-Many: CollaborationNetwork (self-referencing)

### 2. Institution Model
**Purpose**: Research institutions and organizations with external identifier support.

**Key Features**:
- Support for ROR, GRID, and Wikidata identifiers
- Institution type classification
- Geographic information
- Establishment year tracking

**External Integration**:
- Research Organization Registry (ROR)
- Global Research Identifier Database (GRID)
- Wikidata for additional metadata

### 3. Affiliation Model
**Purpose**: Links users to institutions with temporal and role information.

**Key Features**:
- Multiple affiliation types (employment, education, distinctions, etc.)
- Date ranges with current status tracking
- ORCID synchronization support
- Visibility controls

### 4. Work Model
**Purpose**: Research outputs including publications, datasets, software, etc.

**Key Features**:
- Comprehensive work type taxonomy
- Multiple external identifier support (DOI, PMID, ISBN, etc.)
- Full metadata including abstracts and keywords
- Citation tracking capabilities
- ORCID synchronization

**External Integration**:
- Digital Object Identifier (DOI) system
- PubMed integration
- arXiv support
- Custom URL handling

### 5. WorkAuthor Model
**Purpose**: Many-to-many relationship between Works and Users with authorship metadata.

**Key Features**:
- Author ordering and corresponding author designation
- CRediT taxonomy for contribution roles
- Support for non-registered authors
- ORCID ID tracking for external authors

### 6. Funding Model
**Purpose**: Research funding and grant information.

**Key Features**:
- Multiple funding types and sources
- Amount tracking with currency support
- Date ranges for funding periods
- Organization information

### 7. Research Areas Model
**Purpose**: Hierarchical taxonomy of research fields and disciplines.

**Key Features**:
- Self-referencing hierarchy support
- External classification scheme integration (OECD FOS, etc.)
- Flexible subject organization

### 8. Citation Model
**Purpose**: Citation relationships between works for impact analysis.

**Key Features**:
- Source attribution for citation data
- Citation context capture
- Multiple data source support (CrossRef, PubMed, etc.)
- Temporal tracking

### 9. UserMetrics Model
**Purpose**: Cached research metrics for performance optimization.

**Key Features**:
- Publication and citation counts
- H-index and i10-index calculation
- Career span metrics
- Collaboration statistics
- Versioned calculation tracking

### 10. CollaborationNetwork Model
**Purpose**: Research collaboration relationships between users.

**Key Features**:
- Collaboration strength measurement
- Temporal collaboration tracking
- Shared work references
- Network analysis support

### 11. APIUsageLog Model
**Purpose**: API usage tracking for analytics and rate limiting.

**Key Features**:
- Request/response monitoring
- Performance tracking
- Rate limiting support
- User behavior analytics

## Database Configuration

### PostgreSQL Production Setup
```python
# Production database configuration
DATABASES = {
    "default": dj_database_url.parse(os.environ.get("DATABASE_URL"))
}
```

### Key Indexes

**Performance-Critical Indexes**:
- `users.orcid_id` - Primary researcher lookup
- `works.doi` - Publication identification
- `works.publication_year` - Temporal queries
- `affiliations.user_id + affiliation_type` - User affiliation queries
- `citations.cited_work_id` - Citation impact analysis
- `api_usage_logs.timestamp + endpoint` - API analytics

### Data Types and Constraints

**UUID Primary Keys**: Used throughout for better security and distributed system support

**ORCID ID Validation**: 
```python
RegexValidator(
    regex=r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$',
    message='Invalid ORCID ID format'
)
```

**JSON Fields**: Used for flexible metadata storage (keywords, contribution roles)

**Foreign Key Constraints**: Proper cascading deletes and references

## Migration Strategy

### Initial Migration
1. Create all base tables with UUID primary keys
2. Set up custom User model with ORCID integration
3. Create indexes for performance
4. Set up admin interface

### Data Population Strategy
1. Import institution data from ROR/GRID
2. Set up research area taxonomy
3. Create initial ORCID user accounts
4. Import publication data via ORCID API
5. Calculate initial metrics

### Future Migrations
- Add new work types as needed
- Extend research area taxonomy
- Add new external identifier fields
- Performance optimization indexes

## Security Considerations

### Data Protection
- Encrypted storage for ORCID access tokens
- UUID primary keys to prevent enumeration attacks
- Privacy controls for all user data
- API rate limiting and usage tracking

### GDPR Compliance
- User data export capabilities
- Data deletion workflows
- Privacy setting controls
- Audit logging

## Performance Optimization

### Query Optimization
- Strategic indexing on common query patterns
- Cached metrics for expensive calculations
- Efficient many-to-many relationships
- Optimized admin interfaces

### Scalability Features
- UUID primary keys for horizontal scaling
- Separate tables for high-volume data (citations, API logs)
- Efficient pagination support
- Connection pooling ready

## Future Enhancements

### Planned Extensions
1. **Peer Review Tracking**: Add peer review activity models
2. **Research Resource Management**: Equipment, datasets, software tools
3. **Impact Metrics**: Alternative metrics (Altmetrics) integration
4. **Social Features**: Following, bookmarking, recommendations
5. **Analytics Dashboard**: Research trend analysis
6. **Collaboration Matching**: AI-powered collaboration suggestions

### External API Integrations
- Microsoft Academic Graph
- Semantic Scholar API
- Google Scholar (where possible)
- OpenAlex database
- Scopus API integration

## Maintenance and Monitoring

### Regular Tasks
- Citation data updates
- Metrics recalculation
- ORCID synchronization
- Performance monitoring
- Backup and recovery testing

### Monitoring Metrics
- Database performance
- API response times
- User engagement
- Data quality metrics
- System resource usage

## Conclusion

This database schema provides a robust foundation for a comprehensive ORCID-integrated research platform. The design balances flexibility with performance, ensuring the system can scale while maintaining data integrity and user privacy. The modular structure allows for future enhancements while maintaining backward compatibility.

The schema supports the core use cases of researcher identification, publication tracking, collaboration analysis, and research impact measurement, while providing the foundation for advanced features like recommendation systems and research analytics. 