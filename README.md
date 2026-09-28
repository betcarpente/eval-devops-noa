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
**Publish**
- Build de l'image et push sur le registry GHCR
- Trois tags : latest, SHA court du commit et semver (1.0.<run_number> par défaut)

**Deploy**
- Ne s'exécute que sur main ou via _workflow_dispatch_
- Déploiement réel sur la machine cible (runner self-hosted) via docker-compose, avec l'image du SHA
- Health check : curl sur /health 
- Si le healthcheck échoue, le job échoue et l'image précédente est pull (rollback)

### Runner GitHub Actions :
- Tourne en local (WSL / Ubuntu)
- nom : wsl-01

### Application : 
**Fonctionnement**
- Simple application avec bouton pour incrémentation / décrémentation
- Infos stockées dans la DB

### Monitoring :
- prometheus / grafana
- dashboards

### mise en place en local (avec docker)
```bash
cd application

python3 -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt

docker-compose up --build -d
```
L'application est disponible sur http://localhost:5000

Pour arrêter : `docker-compose down` (-v pour supprimer les données sql)
