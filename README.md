# eval-devops-noa
Pour l'évaluation sur le cours DevOps

### Docker : 
**Dockerfile**
- Port 5000
- Image précise (python3.12-slim)
- Healthcheck sur /health, toutes les 30s
- Compte utilisateur appuser

**Docker Compose**
- Deux services : Python3.12 (source : dockerfile) et PostgreSQL (16-alpine)
- Port mappé (5000:5000)
- Deux healthckeck différents selon le service

### Workflow CI : 
**Lint (flake8)**
- Linting basique de l'application avec Flake8. Fichier de config disponible dans application/config/flake8-config.txt


**Test (pytest)**
- Test de l'application avec Pytest. (couverture du code et tests unitaire) 
- Installation de Postgre pour tester
- Mise en cache des dépendances Python.
- Upload le report avec l'action _upload-artifact_

Répond aux critères donnés dans l'eval (matrice sur plusieurs versions, installation de services, mise en cache)

**Build**
- Exécute le docker compose en buildant l'image 

### Workflow CD :
todo

### application : 
- fonctionnement
- mise en place en local (avec docker)

### Monitoring :
- prometheus / grafana
- dashboards