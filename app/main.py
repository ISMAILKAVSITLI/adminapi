from fastapi import FastAPI, HTTPException
import requests
import os
import json

DOCKER_API_URL = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
session = requests.Session()

app = FastAPI(title="API d'administration de conteneurs")


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/containers")
def get_containers():
    reponse = session.get( 
            f"{DOCKER_API_URL}/containers/json",
            params={"all": "true", "filters": json.dumps({"label": ["adminapi.managed=true"]})},
            timeout=10,
        )
    
    reponse.raise_for_status()
    conteneurs = reponse.json()
    resultats = []
    for conteneur in conteneurs:
        nom = conteneur["Names"][0].lstrip("/")
        image = conteneur["Image"]
        etat = conteneur["State"]
        info = {"id": conteneur["Id"], "name": nom, "image": image, "state": etat}
        resultats.append(info)
    return resultats

@app.get("/containers/{identifiant}")
def lire(identifiant: str):
    reponse = session.get(
        f"{DOCKER_API_URL}/containers/{identifiant}/json",
        timeout=10,
    )
    if reponse.status_code == 404:
        raise HTTPException(status_code=404, detail="Conteneur inconnu ou non géré par l'API")
    reponse.raise_for_status()
    conteneur = reponse.json()
    labels = conteneur["Config"]["Labels"] or {}
    if labels.get("adminapi.managed") != "true":
        raise HTTPException(status_code=404, detail="Conteneur non géré par l'API")
    nom = conteneur["Name"].lstrip("/")
    image = conteneur["Config"]["Image"]
    etat = conteneur["State"]["Status"]
    info = {"id": conteneur["Id"], "name": nom, "image": image, "state": etat}
    return info
