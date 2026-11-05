import requests
import sys
import os
import json
from datetime import datetime

DOCKER_API_URL = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
NETBOX_URL = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
NETBOX_TOKEN = os.environ["NETBOX_TOKEN"]
ENTETES_NETBOX = {"Authorization": f"Bearer {NETBOX_TOKEN}"}

session = requests.Session()

try:
    reponse = session.get( 
        f"{DOCKER_API_URL}/containers/json",
        params={"all": "true"},
        timeout=10,
    )

    reponse.raise_for_status()
    conteneurs = reponse.json()
except requests.RequestException as erreur:
    sys.exit(f"Erreur : l'API Docker ne répond pas sur {DOCKER_API_URL}. Est elle démarrée ? ({erreur})")

resultats = []
demarres = 0

for conteneur in conteneurs:
    nom = conteneur["Names"][0].lstrip("/")
    image = conteneur["Image"]
    etat = conteneur["State"]
    print(nom, image, etat)
    info = {"nom": nom, "image": image, "etat": etat}

    if etat == "running":
        demarres += 1
        try:
            reponse_stats = session.get(
                f"{DOCKER_API_URL}/containers/{conteneur['Id']}/stats",
                params={"stream": "false"},
                timeout=10,
            )
            reponse_stats.raise_for_status()
            stats = reponse_stats.json()
        except requests.RequestException as erreur:
            sys.exit(f"Erreur : l'API Docker ne répond pas sur {DOCKER_API_URL}. Est elle démarrée ? ({erreur})")
        cpu, avant = stats["cpu_stats"], stats["precpu_stats"]
        delta_cpu = cpu["cpu_usage"]["total_usage"] - avant["cpu_usage"]["total_usage"]
        delta_systeme = cpu["system_cpu_usage"] - avant.get("system_cpu_usage", 0)
        pourcent = delta_cpu / delta_systeme * cpu["online_cpus"] * 100 if delta_systeme else 0.0
        memoire_mo = stats["memory_stats"]["usage"] / 1024 / 1024
        print("   CPU :", round(pourcent, 2), "% | Mémoire :", round(memoire_mo, 2), "Mo")
        info["cpu_pourcent"] = round(pourcent, 2)
        info["memoire_mo"] = round(memoire_mo, 2)
    resultats.append(info)

reponse_status = session.get(
    f"{NETBOX_URL}/api/status/",
    headers=ENTETES_NETBOX,
    timeout=10,
)
reponse_status.raise_for_status()
version_netbox = reponse_status.json()["netbox-version"]
print(f"NetBox version {version_netbox}")

url_types = f"{NETBOX_URL}/api/core/object-types/?limit=50"
nb_types = 0

while url_types:
    reponse_types = session.get(url_types, headers=ENTETES_NETBOX, timeout=10)
    reponse_types.raise_for_status()
    page = reponse_types.json()
    nb_types += len(page["results"])
    total_annonce = page["count"]
    url_types = page["next"]

print(f"Types d'objets : {nb_types} comptés, {total_annonce} annoncés par NetBox")

donnees = {
    "date": datetime.now().isoformat(),
    "conteneurs": resultats,
    "netbox": {
        "version": version_netbox,
        "types_objets": nb_types,
    },
}

with open("inventaire.json", "w", encoding="utf-8") as fichier:
    json.dump(donnees, fichier, indent=2, ensure_ascii=False)
    
print(f"{len(resultats)} conteneurs, dont {demarres} démarrés")
print("Inventaire écrit dans inventaire.json")
