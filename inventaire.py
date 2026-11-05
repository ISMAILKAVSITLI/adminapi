import requests
import os
import json
from datetime import datetime

DOCKER_API_URL = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")

session = requests.Session()

reponse = session.get( 
     f"{DOCKER_API_URL}/containers/json",
    params={"all": "true"},
    timeout=10,
)

reponse.raise_for_status()
conteneurs = reponse.json()

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
        reponse_stats = session.get(
            f"{DOCKER_API_URL}/containers/{conteneur['Id']}/stats",
            params={"stream": "false"},
            timeout=10,
        )
        reponse_stats.raise_for_status()
        stats = reponse_stats.json()
        cpu, avant = stats["cpu_stats"], stats["precpu_stats"]
        delta_cpu = cpu["cpu_usage"]["total_usage"] - avant["cpu_usage"]["total_usage"]
        delta_systeme = cpu["system_cpu_usage"] - avant.get("system_cpu_usage", 0)
        pourcent = delta_cpu / delta_systeme * cpu["online_cpus"] * 100 if delta_systeme else 0.0
        memoire_mo = stats["memory_stats"]["usage"] / 1024 / 1024
        print("   CPU :", round(pourcent, 2), "% | Mémoire :", round(memoire_mo, 2), "Mo")
        info["cpu_pourcent"] = round(pourcent, 2)
        info["memoire_mo"] = round(memoire_mo, 2)
    resultats.append(info)

donnees = {
    "date": datetime.now().isoformat(),
    "conteneurs": resultats,
}

with open("inventaire.json", "w", encoding="utf-8") as fichier:
    json.dump(donnees, fichier, indent=2, ensure_ascii=False)
    
print(f"{len(resultats)} conteneurs, dont {demarres} démarrés")
print("Inventaire écrit dans inventaire.json")
