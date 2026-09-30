# eval-devops-noa
Pour l'évaluation sur le cours DevOps

### Docker : 
**Dockerfile**
- Port 5000
- Image précise (python3.12-slim)
- Healthcheck sur /health, toutes les 30s
- Compte utilisateur appuser

**Docker Compose**
- Quatre services : Python3.12 (source : dockerfile), PostgreSQL (16-alpine), Prometheus et Grafana
- Ports mappés (5000:5000, 9090:9090, 3000:3000)
- Healthcheck spécifique à chaque service

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
**Endpoint `/metrics`** (format texte Prometheus, exposé par l'application)
- `http_requests_total` : compteur des requêtes reçues, labels `endpoint` et `code` (statut HTTP)
- `request_duration_seconds` : histogramme de latence par route, sert au calcul des percentiles (p95, p99)
- `app_build_info` : jauge à 1 portant les labels `version` et `commit` (SHA déployé, injecté par le CD)

**Prometheus** — http://localhost:9090
- Scrape `app:5000/metrics` toutes les 15s, rétention 7 jours
- Règles d'alerte dans `monitoring/alert-rules.yml`

**Grafana** — http://localhost:3000 (`admin` / `admin` par défaut)
- Datasource et dashboard provisionnés automatiquement (`monitoring/grafana/provisioning`)
- Dashboard *Counter App - Overview* : version déployée, taux d'erreurs 5xx, p95,
  requêtes par endpoint, requêtes par code HTTP, latence p95/p99 par route

**Alertes**
| Alerte | Condition | `for` | Sévérité |
|---|---|---|---|
| `HighErrorRate` | ratio 5xx / total > 5% sur 5 min glissantes | 2m | critical |
| `HighLatencyP95` | p95 (issu de l'histogramme) > 500 ms sur 5 min glissantes | 5m | warning |

Justification des seuils : au-delà de 5% d'erreurs serveur l'impact utilisateur n'est plus marginal,
et `for: 2m` (deux évaluations consécutives) évite de déclencher sur un pic isolé lors d'un déploiement.
Pour la latence, 500 ms au p95 correspond à une dégradation perceptible ; `for: 5m` est plus long car
la latence est plus bruitée que le taux d'erreurs et on attend une tendance stable.

Un endpoint `/test-error` (500) permet de déclencher des erreurs pour valider les alertes.

### mise en place en local (avec docker)
```bash
cd application

python3 -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt

docker-compose up --build -d
```
| Service | URL |
|---|---|
| Application | http://localhost:5000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Pour arrêter : `docker-compose down` (-v pour supprimer les données sql)
