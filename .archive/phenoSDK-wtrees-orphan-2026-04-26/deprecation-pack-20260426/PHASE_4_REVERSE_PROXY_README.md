# Phase 4: Reverse Proxy & Fallback Experience - Implementation Complete

## Overview

Phase 4 of the KInfra transformation implements sophisticated reverse proxy and fallback experience features, building upon the resource coordination from Phase 3. This phase focuses on project-specific routing, fallback configuration, health monitoring, and production-ready deployment patterns.

## Key Features Implemented

### 1. Project Routing Templates ✅
- **Domain + Base Path Mapping**: Intelligent routing with project-specific domains and path prefixes
- **Service Discovery**: Automatic service registration and health check integration
- **Route Management**: Add, remove, and update routes with metadata tracking
- **Configuration Export/Import**: JSON and YAML support for routing configurations

### 2. Fallback Configuration API/CLI ✅
- **Page Customization**: Customize loading, error, and maintenance pages
- **Maintenance Mode**: Enable/disable maintenance mode with custom messages
- **Template Management**: Custom HTML templates with CSS/JS support
- **Project-Specific Configs**: Isolated fallback configurations per project

### 3. Health Monitoring with Project Metadata ✅
- **Service Health Tracking**: Real-time health status for all services
- **Project Aggregation**: Overall project health based on service status
- **Dependency Monitoring**: Track service dependencies and health chains
- **Dashboard Generation**: Rich dashboard data for status visualization

### 4. Sample Compose Files ✅
- **Shared Proxy Setup**: Docker Compose example with shared reverse proxy
- **Multi-Service Architecture**: Multiple projects sharing infrastructure
- **Nginx Configuration**: Production-ready nginx config with project routing
- **Health Check Integration**: Comprehensive health monitoring setup

## Architecture

```
Phase 4: Reverse Proxy & Fallback Experience
├── ProjectRoutingManager
│   ├── ProjectRoute (domain + path mapping)
│   ├── ProjectRoutingConfig (project-specific routing)
│   ├── Route Discovery & Management
│   └── Configuration Export/Import
├── FallbackConfigManager
│   ├── FallbackPageConfig (page customization)
│   ├── MaintenanceConfig (maintenance mode)
│   ├── Template Management
│   └── Project-Specific Configs
├── HealthDashboard
│   ├── ServiceHealth (service status tracking)
│   ├── ProjectHealth (project aggregation)
│   ├── Health Checkers
│   └── Dashboard Generation
└── Docker Compose Integration
    ├── Shared Proxy Setup
    ├── Multi-Service Architecture
    ├── Nginx Configuration
    └── Health Check Integration
```

## Usage Examples

### Project Routing Templates

```python
from pheno.infra.proxy_gateway.project_routing import ProjectRoutingManager

# Create routing manager
routing_manager = ProjectRoutingManager()

# Create default config for a project
config = routing_manager.create_default_config(
    project_name="api-project",
    domain="api.example.com",
    base_path="/api/v1",
    services=[
        {"name": "users", "port": 8001, "health_check_path": "/health"},
        {"name": "orders", "port": 8002, "health_check_path": "/health"},
    ]
)

# Add additional routes
routing_manager.add_route(
    project_name="api-project",
    service_name="analytics",
    port=8004,
    path_prefix="/api/v1/analytics",
    health_check_path="/health",
)

# Find routes by path
route = routing_manager.get_route_by_path("/api/v1/users")
if route:
    print(f"Service: {route.service_name}, Port: {route.port}")

# Export configuration
config_json = routing_manager.export_config("api-project", "json")
```

### Fallback Configuration

```python
from pheno.infra.fallback_site.config_manager import FallbackConfigManager, FallbackPageConfig

# Create config manager
config_manager = FallbackConfigManager()

# Create project configuration
project_config = config_manager.create_project_config("demo-project")

# Update fallback pages
loading_page = FallbackPageConfig(
    page_type="loading",
    service_name="demo-project",
    title="Demo Project - Starting Up",
    message="Demo project is currently starting up...",
    refresh_interval=3,
    custom_css="body { background: linear-gradient(45deg, #667eea, #764ba2); }",
)

config_manager.update_fallback_page("demo-project", "loading", loading_page)

# Enable maintenance mode
config_manager.enable_maintenance(
    project_name="demo-project",
    message="Demo project is under maintenance",
    estimated_duration="1 hour",
    contact_info="support@example.com",
)

# Set custom template
custom_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{service_name}} - {{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner"></div>
        <h1>{{service_name}}</h1>
        <p>{{message}}</p>
    </div>
</body>
</html>
"""

config_manager.set_custom_template("demo-project", "loading", custom_template)
```

### Health Monitoring

```python
from pheno.infra.proxy_gateway.health_dashboard import HealthDashboard

# Create health dashboard
health_dashboard = HealthDashboard()
await health_dashboard.initialize()

# Register health checkers
async def api_health_check():
    # Your health check logic
    return True

health_dashboard.register_health_checker("api-service", api_health_check)

# Update service health
health_dashboard.update_service_health(
    project_name="api-project",
    service_name="api-service",
    status="healthy",
    port=8001,
    metadata={"version": "1.0.0", "environment": "production"},
    dependencies=["redis", "postgres"],
)

# Get project health
api_health = health_dashboard.get_project_health("api-project")
print(f"Status: {api_health.overall_status}")
print(f"Services: {len(api_health.services)}")

# Get dashboard data
dashboard_data = health_dashboard.get_dashboard_data()
```

### CLI Usage

```bash
# Initialize fallback configuration
pheno fallback init-project demo-project --default-page-type loading

# Set fallback page
pheno fallback set-page demo-project loading \
  --service-name demo-project \
  --title "Demo Project - Starting Up" \
  --message "Demo project is currently starting up..." \
  --refresh-interval 3

# Enable maintenance mode
pheno fallback enable-maintenance demo-project \
  --message "Demo project is under maintenance" \
  --duration "1 hour" \
  --contact "support@example.com"

# Set custom template
pheno fallback set-template demo-project loading loading-template.html

# Show configuration
pheno fallback show-config demo-project --format json

# List projects
pheno fallback list-projects

# List pages
pheno fallback list-pages demo-project
```

## Docker Compose Integration

### Sample Compose File

```yaml
version: '3.8'

services:
  # Shared reverse proxy
  proxy:
    image: nginx:alpine
    ports:
      - "9100:80"
      - "9000:9000"  # Fallback server
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./fallback-templates:/usr/share/nginx/html/templates:ro
    networks:
      - kinfra-network

  # Project A - API Service
  api-service:
    build: ./api-service
    ports:
      - "8001:8000"
    environment:
      - PROJECT_NAME=api-service
      - SERVICE_PORT=8000
      - HEALTH_CHECK_PATH=/health
    networks:
      - kinfra-network
    depends_on:
      - redis
      - postgres

  # Project B - Web Service
  web-service:
    build: ./web-service
    ports:
      - "8002:8000"
    environment:
      - PROJECT_NAME=web-service
      - SERVICE_PORT=8000
      - HEALTH_CHECK_PATH=/health
    networks:
      - kinfra-network
    depends_on:
      - redis

  # Shared Redis (Global Resource)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - kinfra-network

  # Shared PostgreSQL (Global Resource)
  postgres:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=kinfra
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=secret
    networks:
      - kinfra-network

networks:
  kinfra-network:
    driver: bridge
```

### Nginx Configuration

```nginx
events {
    worker_connections 1024;
}

http {
    # Project A - API Service Routes
    location /api/ {
        add_header X-Project "api-service" always;
        add_header X-Service "api" always;
        
        location /api/health {
            proxy_pass http://api_service/health;
        }
        
        proxy_pass http://api_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Project B - Web Service Routes
    location /web/ {
        add_header X-Project "web-service" always;
        add_header X-Service "web" always;
        
        location /web/health {
            proxy_pass http://web_service/health;
        }
        
        proxy_pass http://web_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Fallback server
    location / {
        try_files $uri @fallback;
    }
    
    location @fallback {
        proxy_pass http://127.0.0.1:9000/;
    }
}
```

## Key Benefits

### 1. **Project-Specific Routing**
- Clean separation of concerns with project-specific domains and paths
- Automatic service discovery and health check integration
- Flexible route management with metadata tracking

### 2. **Sophisticated Fallback Experience**
- Customizable loading, error, and maintenance pages
- Project-specific fallback configurations
- Template management with CSS/JS support

### 3. **Comprehensive Health Monitoring**
- Real-time service health tracking
- Project-level health aggregation
- Dependency monitoring and health chains

### 4. **Production-Ready Deployment**
- Docker Compose examples for shared proxy setups
- Nginx configuration with project routing
- Health check integration and monitoring

### 5. **Developer Experience**
- Rich CLI commands for configuration management
- JSON/YAML import/export support
- Comprehensive examples and documentation

## File Structure

```
pheno-sdk/src/pheno/infra/
├── proxy_gateway/
│   ├── project_routing.py      # Project routing templates
│   └── health_dashboard.py     # Health monitoring
├── fallback_site/
│   └── config_manager.py       # Fallback configuration
├── cli/
│   └── fallback_cli.py         # Fallback CLI commands
└── examples/
    ├── phase4_reverse_proxy_example.py  # Comprehensive examples
    ├── docker-compose-shared-proxy.yml  # Sample compose file
    └── nginx.conf                       # Nginx configuration
```

## Integration with Previous Phases

Phase 4 builds upon the foundation from previous phases:

- **Phase 2 (Project Context)**: Uses `ProjectInfraContext` for project-scoped infrastructure
- **Phase 3 (Resource Coordination)**: Integrates with `ResourceCoordinator` for resource management
- **Phase 4 (Reverse Proxy)**: Adds sophisticated routing and fallback experience

## Testing

Run the comprehensive example to see Phase 4 in action:

```bash
cd pheno-sdk
python examples/phase4_reverse_proxy_example.py
```

This demonstrates all the key features of Phase 4 reverse proxy and fallback experience.

## Next Steps (Phase 5)

Phase 4 provides the foundation for Phase 5 (Process & Tunnel Governance), which will focus on:

1. **Process Naming & Cleanup**: Tighten process management using project metadata
2. **Tunnel Lifecycle**: Improve tunnel management and credential sharing
3. **Cleanup Policies**: Configurable cleanup strategies
4. **Service Status**: Enhanced fallback pages with service/tunnel status

## Conclusion

Phase 4 successfully implements sophisticated reverse proxy and fallback experience features, providing project-specific routing, comprehensive fallback configuration, health monitoring with project metadata, and production-ready deployment patterns. The implementation enables complex multi-service architectures with shared infrastructure while maintaining project isolation and providing excellent developer experience.

The reverse proxy and fallback experience layer makes it easy to deploy and manage multiple projects with shared resources, providing a solid foundation for production deployments and complex service architectures.