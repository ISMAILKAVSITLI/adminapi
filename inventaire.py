import requests

session = requests.Session()

reponse = session.get( 
    "http://127.0.0.1:2375/containers/json",
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