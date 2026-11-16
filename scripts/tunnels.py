"""Ouvre les interfaces de la supervision sur le PC, et les garde ouvertes.

Usage : python3 scripts/tunnels.py   (Ctrl+C ferme tous les tunnels)
"""
import subprocess
import time

# Nom affiché : (Service du namespace monitoring, port du PC:port du Service)
TUNNELS = {
    "Prometheus": ("svc/monitoring-kube-prometheus-prometheus", "9090:9090"),
    "Grafana": ("svc/monitoring-grafana", "3000:80"),
    "Alertmanager": ("svc/monitoring-kube-prometheus-alertmanager", "9093:9093"),
}

def ouvrir(service, ports):
    """Lance kubectl port-forward en arrière-plan ; seules ses erreurs s'affichent."""
    return subprocess.Popen(
        ["kubectl", "port-forward", "-n", "monitoring", service, ports],
        stdout=subprocess.DEVNULL,
    )

def main():
    processus = {}
    for nom, (service, ports) in TUNNELS.items():
        processus[nom] = ouvrir(service, ports)
        print(f"{nom} : http://localhost:{ports.split(':')[0]}")
    print("Tunnels ouverts. Ctrl+C pour tout fermer.")
    try:
        while True:
            time.sleep(2)
            for nom, p in processus.items():
                if p.poll() is not None: # ce tunnel s'est arrêté : on le rouvre
                     print(f"{nom} : tunnel coupé, réouverture")
                     processus[nom] = ouvrir(*TUNNELS[nom])
    except KeyboardInterrupt:
        print("Fermeture des tunnels")
    finally:
        for p in processus.values():
            p.terminate()

if __name__ =="__main__":
    main()