# FraudSight - Tax Evasion Network Detection System

A multi-agent AI system for detecting tax evasion networks using graph analytics and machine learning.

## Architecture

### Backend Structure
```
backend/
├── main.py                 # FastAPI application entry point
├── database.py            # SQLite database models and connection
├── models.py              # Pydantic models for API requests/responses
├── agents/                # Multi-agent fraud detection pipeline
│   ├── base_agent.py      # Abstract base class for all agents
│   ├── collection_agent.py # Data collection from various sources
│   ├── processing_agent.py # Data cleaning and normalization
│   ├── privacy_agent.py   # PII anonymization and compliance
│   ├── linking_agent.py   # Graph relationship building
│   └── fraud_agent.py     # Fraud detection and risk scoring
├── routes/                # API route handlers
│   ├── dashboard_routes.py
│   ├── graph_routes.py
│   ├── logs_routes.py
│   ├── settings_routes.py
│   └── agents_routes.py
├── services/              # Business logic services
│   ├── graph_service.py   # NetworkX graph analytics
│   ├── fraud_service.py   # Fraud detection algorithms
│   └── log_service.py     # Privacy compliance logging
└── data/
    └── demo_dataset.json  # Sample dataset for demonstration
```

## Multi-Agent Pipeline

The system uses a sequential agent pipeline:

1. **Collection Agent** - Loads data from JSON/CSV sources
2. **Processing Agent** - Cleans and normalizes transaction data
3. **Privacy Agent** - Anonymizes sensitive PII fields
4. **Linking Agent** - Builds graph relationships using NetworkX
5. **Fraud Agent** - Detects suspicious patterns and calculates risk scores

## API Endpoints

### Analysis
- `POST /api/run-analysis` - Execute full fraud detection pipeline

### Dashboard
- `GET /api/dashboard` - Get dashboard metrics and high-risk entities
- `GET /api/high-risk` - Get detailed high-risk entity list

### Graph Visualization
- `GET /api/graph` - Get graph data for D3.js visualization

### Privacy & Compliance
- `GET /api/privacy-logs` - Get audit logs with filtering options
- `GET /api/logs/export` - Export logs in CSV/JSON format

### Settings
- `GET /api/settings` - Get system configuration
- `POST /api/settings` - Update system settings

### Agent Monitoring
- `GET /api/agents-status` - Get status of all agents
- `GET /api/agents/{agent_name}/status` - Get specific agent status

## Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Access the Application**
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Key Features

### Graph Analytics
- **NetworkX Integration** - Advanced graph algorithms for fraud detection
- **Centrality Measures** - Degree, betweenness, and closeness centrality
- **Community Detection** - Identify fraud clusters and networks
- **Circular Pattern Detection** - Find suspicious transaction cycles

### Privacy Compliance
- **PII Anonymization** - Hash-based anonymization of sensitive fields
- **Audit Logging** - Complete compliance audit trail
- **Access Control** - Granular data access logging

### Fraud Detection
- **Risk Scoring** - Multi-factor risk assessment
- **Pattern Recognition** - Statistical and graph-based anomaly detection
- **Real-time Analysis** - Streaming data processing capabilities

### Interactive Visualization
- **D3.js Integration** - Force-directed graph visualization
- **Real-time Updates** - Live dashboard with WebSocket support
- **Multi-layer Filtering** - Risk-based and relationship-based filtering

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Data Processing**: Pandas, NetworkX
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript, D3.js
- **Deployment**: Docker, Kubernetes ready

## Security Features

- **Data Anonymization** - Automatic PII masking
- **Access Logging** - Complete audit trail
- **Input Validation** - Pydantic model validation
- **CORS Protection** - Configurable cross-origin policies
- **Rate Limiting** - Built-in request throttling

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black backend/
isort backend/
```

### API Documentation
Automatic OpenAPI/Swagger documentation available at `/docs`

## License

This project is licensed under the MIT License - see the LICENSE file for details.