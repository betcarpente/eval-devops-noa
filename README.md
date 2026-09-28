# eval-devops-noa
Pour l'évaluation sur le cours DevOps

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
- Build l'image docker de l'application (cf. application/Dockerfile)

### docker : 
- dockerfile
- docker compose

### application : 
- fonctionnement
- mise en place en local (avec docker)

###monitoring :
- prometheus / grafana
- dashboards