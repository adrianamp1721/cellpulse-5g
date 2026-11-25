# CellPulse 5G — Enterprise NOC & Inteligencia Geoespacial 5G NR

![Cloud Native](https://img.shields.io/badge/Architecture-Cloud--Native%20CNCF-0284c7?style=for-the-badge&logo=kubernetes&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20Python%203.11-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Azure](https://img.shields.io/badge/Deploy-Azure%20Static%20Web%20Apps-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Docker](https://img.shields.io/badge/Containers-Docker%20%26%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

**CellPulse 5G** es una plataforma B2B SaaS de grado empresarial diseñada para el monitoreo geoespacial, auditoría de Calidad de Servicio (**QoS / SLA**) y simulación de inversiones (**CAPEX What-If**) en redes **5G NR (Banda Media 3.5 GHz n78)** sobre el área metropolitana de **Bogotá D.C. y la Sabana de Occidente/Norte**.

**Aplicación en Producción (Azure):** [https://proud-field-073a24510.4.azurestaticapps.net](https://proud-field-073a24510.4.azurestaticapps.net)

---

## Características Principales

* **Topología Geoespacial Metropolitana (20 Macro-Celdas gNodeB + 2 Nodos CAPEX):** Visualización interactiva mediante **Leaflet** y capas duales de **Esri ArcGIS** (*Vista NOC Oscura* y *Calles & Vías*), con radios de cobertura realistas (2.9 km – 3.8 km) y solapamiento controlado (*Zero-Interruption Handover*).
* **Telemetría RF Detallada por Antena:** Inspección en vivo por nodo con mediciones de **EIRP** (61–65 dBm), **RSRP** (-76 a -86 dBm), **SINR** (17.2–25.0 dB), **Latencia E2E** (ms) y **Throughput** (Mbps), acompañada de gráficas dinámicas en **Chart.js** y buscador en tiempo real.
* **Simulador de Inversión CAPEX (What-If):** Evaluación de impacto financiero y operativo mediante el despliegue virtual de estaciones base en sectores críticos (Ciudad Bolívar y Autopista Sur Bosa/Soacha), calculando el retorno de inversión (**ROI**) y la mitigación del riesgo operativo en flotas logísticas ($2,150 USD/hr $\rightarrow$ $0 USD/hr).
* **Modelo Comercial B2B & Auditoría Ejecutiva PDF:** Flujo de suscripción corporativa para desbloqueo de la red metropolitana (*Enterprise Pro*) y generador de **Informes Ejecutivos QoS** membreteados con matriz completa de mediciones por estación base.
* **Backend Cloud-Native de Alto Rendimiento:** Microservicio en **FastAPI** con motor físico de propagación en espacio libre (**FSPL 3GPP n78**), transmisión en tiempo real vía **WebSockets**, caché distribuida en **Redis (< 5 ms)** y soporte geoespacial con **PostgreSQL + PostGIS**.

---

## Arquitectura Cloud-Native (5 Capas)

```text
+-----------------------------------------------------------------------------------+
|                        CAPA 1: PRESENTACIÓN & TELEMETRÍA UI                       |
|   Azure Static Web Apps (CDN Global) | HTML5 + TailwindCSS + Leaflet (Esri GIS)   |
|   Chart.js (Tráfico en Vivo) | Simulador CAPEX | Generador PDF QoS Membreteado    |
+-----------------------------------------+-----------------------------------------+
                                          | HTTPS (REST API) / WSS (WebSockets)
                                          v
+-----------------------------------------------------------------------------------+
|                    CAPA 2: ORQUESTACIÓN & AUTOESCALADO (K8S)                      |
|   Kubernetes Cluster (Namespace: cellpulse-5g) | LoadBalancer Service             |
|   Horizontal Pod Autoscaler (HPA: Min 2 - Max 6 Pods @ 70% CPU) | Liveness Probes |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                   CAPA 3: LÓGICA DE NEGOCIO & MOTOR RF (BACKEND)                  |
|   FastAPI (Python 3.11 / Uvicorn ASGI) | Documentación OpenAPI Swagger (/docs)    |
|   Motor Físico 3GPP n78 (Cálculo FSPL, EIRP, RSRP, SINR) | Gestión Suscripciones  |
+-----------------------+-----------------------------------+-----------------------+
                        |                                   |
                        v                                   v
+---------------------------------------+   +---------------------------------------+
|    CAPA 4A: CACHÉ DE ALTA VELOCIDAD   |   |   CAPA 4B: PERSISTENCIA GEOESPACIAL   |
|   Redis 7 Alpine (In-Memory Store)    |   |   PostgreSQL 16 + PostGIS 3.4         |
|   Latencia < 5 ms | TTL 30s           |   |   Almacenamiento Nodos, SLA & Rutas   |
+---------------------------------------+   +---------------------------------------+

+-----------------------------------------------------------------------------------+
|                 CAPA 5: DEVOPS, CALIDAD Y DESPLIEGUE CONTINUO (CI/CD)             |
|   GitHub Repository -> GitHub Actions Pipeline:                                   |
|   [1. Pytest RF Suite] ---> [2. Docker Image Build] ---> [3. Azure SWA Deploy]    |
+-----------------------------------------------------------------------------------+
