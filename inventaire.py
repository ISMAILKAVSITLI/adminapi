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
    if etat == "running":
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