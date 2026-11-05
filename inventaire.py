import requests
import os

DOCKER_API_URL = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")

session = requests.Session()

reponse = session.get( 
     f"{DOCKER_API_URL}/containers/json",
    params={"all": "true"},
    timeout=10,
)

reponse.raise_for_status()
conteneurs = reponse.json()


for conteneur in conteneurs:
    nom = conteneur["Names"][0].lstrip("/")
    image = conteneur["Image"]
    etat = conteneur["State"]
    print(nom, image, etat)