# Docker Setup for Business Impact Assessment Tool

This directory contains Docker configuration files to run the BIA Tool in containerized environments. You can use Docker for both development and production deployments.

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (for cloning the repository)

### Development Setup (SQLite)

1. **Navigate to the docker directory:**
```bash
cd docker
```

2. Start the application:
```bash
docker-compose up --build
```
3. **Access the application:**
- Open your browser and go to: http://localhost:5001
    - Login with default credentials:
    - Email: admin@example.com
    - Password: aVerySecurePasswordSh0uldBeUsedH3r3!
4. **Stop the application:**
```bash
docker-compose down
```
# Configuration Options
## Environment Variables
Create a .env.docker.local file in the docker directory based on .env.docker template:
``` bash
cp .env.docker .env.docker.local
```

Edit the file with your specific settings:
```bash
# Application settings
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Admin user credentials
ADMIN_EMAIL=your-admin@example.com
ADMIN_PASSWORD=YourSecurePassword123!

# Database type (sqlite or mariadb)
DATABASE_TYPE=sqlite

# For MariaDB (uncomment if needed)
# DATABASE_TYPE=mariadb
# DB_HOST=mariadb
# DB_PORT=3306
# DB_NAME=bia_tool
# DB_USER=bia_user
# DB_PASSWORD=secure_password
# DB_ROOT_PASSWORD=secure_root_password
```
# Deployment Scenarios
1. **Development with SQLite (Default)**
**Start application:**
```bash
docker-compose up --build
```
**Start in background:**
```bash
docker-compose up -d --build
```
**View logs:**
```bash
docker-compose logs -f bia-app
```
2. **Development with MariaDB**
**Start with database:**
```bash
docker-compose --profile mariadb up --build
```
**Start only MariaDB (for external development):**
```bash
docker-compose --profile mariadb up mariadb-dev -d
```
**3. Production Deployment**
**Using production compose file:**
```bash
# Create production environment file
cp .env.docker .env.prod

# Edit .env.prod with production settings
nano .env.prod

# Start production stack
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```
**Production environment example:**
``` bash
FLASK_ENV=production
SECRET_KEY=very-secure-production-key
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=VerySecureProductionPassword123!
DATABASE_TYPE=mariadb
DB_HOST=mariadb
DB_PORT=3306
DB_NAME=bia_tool
DB_USER=bia_user
DB_PASSWORD=secure_production_password
DB_ROOT_PASSWORD=secure_root_password
```
# Helper Scripts
Use the provided scripts in the `../scripts/` directory for easier management:

## Development Scripts
```bash
# Start development environment
../scripts/docker-dev.sh start

# Start in background
../scripts/docker-dev.sh start-bg

# Start with MariaDB
../scripts/docker-dev.sh start-with-db

# Stop all services
../scripts/docker-dev.sh stop

# View logs
../scripts/docker-dev.sh logs

# Clean up (removes containers and volumes)
../scripts/docker-dev.sh clean
```
## Production Scripts
```bash
# Deploy production environment
../scripts/docker-prod.sh deploy

# Stop production environment
../scripts/docker-prod.sh stop

# Update production deployment
../scripts/docker-prod.sh update

# Backup production data
../scripts/docker-prod.sh backup

# View production logs
../scripts/docker-prod.sh logs
```
# Data Persistence
## SQLite Mode
- Database file is stored in `../instance/bia_tool.db`
- Data persists between container restarts
- Suitable for development and small deployments
## MariaDB Mode
- Database data is stored in Docker volumes
- Production data in `mariadb_prod_data` volume
- Development data in `mariadb_dev_data` volume
## Backup and Restore
**SQLite Backup**:
```bash
# Copy database file
docker-compose exec bia-app cp /app/instance/bia_tool.db /app/backup_$(date +%Y%m%d_%H%M%S).db
```
**MariaDB Backup:**
```bash
# Create database dump
docker-compose exec mariadb mysqldump -u root -p bia_tool > backup_$(date +%Y%m%d_%H%M%S).sql
```
**MariaDB Restore:**
```bash
# Restore from dump
docker-compose exec -T mariadb mysql -u root -p bia_tool < backup_file.sql
```
# Troubleshooting
## Common Issues
1. Port already in use:
``` bash
# Check what's using port 5001
lsof -i :5001

# Or change port in docker-compose.yml
ports:
  - "5002:5001"  # Use port 5002 instead
```
2. **Database connection issues:**
```bash
# Check database logs
docker-compose logs mariadb

# Restart database service
docker-compose restart mariadb
```
3. **Permission issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER ../instance
```
4. **Container won't start:**
```bash
# Check container logs
docker-compose logs bia-app

# Rebuild without cache
docker-compose build --no-cache
docker-compose up
```
# Health Checks
The application includes health checks that monitor:
- Application responsiveness on port 5001
- Database connectivity (for MariaDB setups)
**Check health status:**
```bash
docker-compose ps
```
**Manual health check:**
```bash
curl -f http://localhost:5001/
```
# Development Workflow
## Live Development with Docker
For active development, you can mount your source code:
```bash
# Add to docker-compose.yml under bia-app service
volumes:
  - ../app:/app/app
  - ../static:/app/static
  - ../instance:/app/instance
```
This allows you to edit code on your host machine and see changes reflected in the container.

# Database Migrations
**Run migrations in container:**
```bash
# Access container shell
docker-compose exec bia-app bash

# Run Flask commands
flask db migrate -m "Your migration message"
flask db upgrade
```
# Debugging
**Access container shell:**
```bash
docker-compose exec bia-app bash
```
**View application logs:**
```bash
docker-compose logs -f bia-app
```
**Python debugging:**
```bash
# Add to your Python code
import pdb; pdb.set_trace()

# Then attach to container
docker-compose exec bia-app python -c "import pdb; pdb.set_trace()"
```
# Security Considerations
## Production Security
1. Change default passwords:
- Update ADMIN_PASSWORD
- Update DB_PASSWORD and DB_ROOT_PASSWORD
2. Use strong secret keys:
- Generate secure SECRET_KEY
- Use environment-specific keys
3. Network security:
- Don't expose database ports in production
- Use reverse proxy (nginx) for HTTPS
- Implement firewall rules
4. Container security:
- Regularly update base images
- Scan for vulnerabilities
- Use non-root user (already implemented)
# Environment File Security
**Never commit sensitive `.env` files to version control!**
```bash
# Add to .gitignore
.env.docker.local
.env.prod
*.env.local
```
# Performance Optimization
## Production Optimizations
1. Use multi-stage builds:
- Separate build and runtime stages
- Minimize final image size
2. Resource limits:
```bash 
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```
3. Database optimization:
- Configure MariaDB for production workloads
- Set appropriate buffer sizes
- Enable query caching
# Monitoring and Logging
## Log Management
View logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs bia-app

# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```
# Log rotation:
```yml
# Add to docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```
# Monitoring
## Resource usage:
```bash
# Container stats
docker stats

# Compose services stats
docker-compose top
```
# Support
For issues related to Docker setup:
1. Check the troubleshooting section above
2. Review container logs
3. Verify environment configuration
4. Check Docker and Docker Compose versions
For application-specific issues, refer to the main project documentation.