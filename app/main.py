from fastapi import FastAPI
import requests
import os
import json

DOCKER_API_URL = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
session = requests.Session()

app = FastAPI(title="API d'administration de conteneurs")


@app.get("/health")
def health_check():
    return {"status": "healthy"}

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
