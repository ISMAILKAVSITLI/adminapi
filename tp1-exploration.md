# TP1 : Exploration des API

## Étape 1 : Lancement des conteneurs

```bash
docker run -d --name web1 --label adminapi.managed=true nginx:alpine
docker run -d --name intrus nginx:alpine
```

`web1` porte le label `adminapi.managed=true`, `intrus` n'en a pas.

## Étape 2 : API Docker en lecture (GET)

### Version de Docker

```bash
curl -i "http://127.0.0.1:2375/version"
```

Code obtenu : **200 OK**

### Liste des conteneurs en marche

```bash
curl -i "http://127.0.0.1:2375/containers/json"
```

Code obtenu : **200 OK**

### Liste de tous les conteneurs (arrêtés compris)

```bash
curl -i "http://127.0.0.1:2375/containers/json?all=true"
```

Code obtenu : **200 OK**

### Conteneurs portant le label adminapi.managed=true

```bash
curl -i -G "http://127.0.0.1:2375/containers/json" --data-urlencode 'filters={"label":["adminapi.managed=true"]}'
```

Code obtenu : **200 OK** (seul `web1` est renvoyé)

### Détail du conteneur web1

```bash
curl -i "http://127.0.0.1:2375/containers/web1/json"
```

Code obtenu : **200 OK**
## Étape 3 : Actions et codes de statut

### Arrêt de web1 (premier appel)

```bash
curl -i -X POST "http://127.0.0.1:2375/containers/web1/stop"
```

Code obtenu : **204 No Content** (le conteneur est arrêté, pas de corps de réponse)

### Arrêt de web1 (deuxième appel)

```bash
curl -i -X POST "http://127.0.0.1:2375/containers/web1/stop"
```

Code obtenu : **304 Not Modified** (déjà arrêté : l'opération est idempotente)

### Conteneur inexistant

```bash
curl -i "http://127.0.0.1:2375/containers/jesaispas/json"
```

Code obtenu : **404 Not Found**, avec le message `{"message":"No such container: jesaispas"}`

## Étape 4 : NetBox, obtention d'un token

Interface : http://127.0.0.1:8080
Documentation Swagger : http://127.0.0.1:8080/api/schema/swagger-ui/

### Obtention d'un token (route non authentifiée)

```bash
curl -i -X POST "http://127.0.0.1:8080/api/users/tokens/provision/" -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}'
```

Code obtenu : **201 Created** (un token v2 est créé)

Le token est rangé dans `.env` sous la forme `NETBOX_TOKEN=nbt_<key>.<token>`. Ce fichier est ignoré par Git.

### Vérification du token

```bash
source .env
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $NETBOX_TOKEN" "http://127.0.0.1:8080/api/users/tokens/"
```

Code obtenu : **200 OK**

## Étape 5 : Création du type de cluster et du cluster

### Type de cluster Docker

```bash
curl -i -X POST "http://127.0.0.1:8080/api/virtualization/cluster-types/" -H "Authorization: Bearer $NETBOX_TOKEN" -H "Content-Type: application/json" -d '{"name":"Docker","slug":"docker"}'
```

Code obtenu : **201 Created** (id du type : 1)

### Cluster docker-local

```bash
curl -i -X POST "http://127.0.0.1:8080/api/virtualization/clusters/" -H "Authorization: Bearer $NETBOX_TOKEN" -H "Content-Type: application/json" -d '{"name":"docker-local","type":1}'
```

Code obtenu : **201 Created**