# CellPulse 5G - High-Precision Cellular Coverage Analytics Platform

## 1. Executive Summary & Business Case Modelo de Negocio
**CellPulse 5G** es una plataforma nativa de la nube (*Cloud-Native*) diseñada para la recolección, procesamiento y visualización en tiempo real de cobertura de redes móviles (4G/5G) y torres celulares.

A diferencia de portales puramente informativos, **CellPulse 5G** opera bajo un modelo de negocio SaaS (Software as a Service) monetizable mediante:
- **API B2B para Operadores de Telecomunicaciones:** Venta de telemetría crowdsourced sobre puntos ciegos y calidad de red (QoS) para optimizar inversiones en infraestructura.
- **Servicios de Mapas para Empresas de IoT y Logística:** Garantía de conectividad continua en rutas críticas de transporte.
- **Acceso Freemium/Pro:** Herramientas avanzadas de auditoría de red para usuarios corporativos.

---

## 2. Cloud-Native Reference Architecture (Azure & CNCF Principles)
El sistema ha sido diseñado aplicando las directrices de la **Cloud Native Computing Foundation (CNCF)**, garantizando un entorno agnóstico, escalable y altamente disponible sobre **Microsoft Azure**.

- **Microservices Design:**
  - `Frontend-Service`: Interfaz interactiva de mapas basada en Leaflet.js.
  - `Telemetry-Ingest-Service`: Servicio de recepción masiva de lecturas de señal de antenas.
  - `Spatial-Analytics-Service`: Procesamiento y renderizado de coordenadas geoespaciales.
- **Serverless Computing:** Implementación de **Azure Functions** para la ingesta de telemetría bajo demanda, reduciendo costos operativos al procesar millones de eventos por segundo solo cuando ocurren.
- **Containerization & Orchestration:** Empaquetamiento de servicios mediante **Docker** y definición de manifiestos de **Kubernetes** para escalado horizontal automático (HPA) y tolerancia a fallos.
- **DevOps & CI/CD Pipeline:** Automatización continua de compilación, pruebas y despliegue usando **GitHub Actions**.

---

## 3. Estructura del Repositorio
```text
├── .github/
│   └── workflows/
│       └── deploy.yml          # Pipeline de CI/CD para GitHub Actions
├── frontend/
│   ├── index.html              # Aplicación Web / Mapa Interactivo
│   └── Dockerfile              # Contenedor Nginx para el Frontend
├── k8s/
│   ├── deployment.yaml         # Configuración de Deployments y Pods en Kubernetes
│   └── service.yaml            # Configuración de LoadBalancer y Networking
├── README.md                   # Documentación principal del caso de negocio