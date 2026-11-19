# Odoo Art Gallery & Marketplace

![Odoo Version](https://img.shields.io/badge/Odoo-19.0-purple?style=for-the-badge&logo=odoo)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=for-the-badge&logo=typescript)
![License](https://img.shields.io/badge/License-LGPL--3-green?style=for-the-badge)

Una solución completa de gestión y venta de obras de arte construida sobre **Odoo 19**. Este proyecto integra una galería visual con TypeScript, un sistema de tickets de compra, facturación automática, un portal web público para clientes y un lanzador de aplicaciones personalizado.

## 📋 Características Principales

*   **Módulo `art_gallery`:** Importación automática de obras desde la API del Art Institute of Chicago, con dashboard interactivo en TypeScript.
*   **Módulo `art_marketplace`:** Gestión de ventas, control de disponibilidad (evita ventas duplicadas), flujo de tickets (New -> Contacted -> Won) y generación automática de facturas en Contabilidad.
*   **Módulo `art_app_launcher`:** Un reemplazo nativo del menú de aplicaciones. Incluye un Client Action (OWL) que muestra todas las apps instaladas con sus iconos, accesible mediante un botón personalizado (🏠) en el Systray.
*   **Portal Web Público:** Catálogo de obras publicadas y formulario de solicitud de compra con validación de teléfono.
*   **Integración Contable:** Creación automática de facturas de cliente (`account.move`) al confirmar una venta.

## 🛠️ Requisitos Previos

*   **Docker** y **Docker Compose** instalados.
*   **Git** para clonar el repositorio.
*   **Node.js** (opcional, solo si deseas recompilar el dashboard en TypeScript).

## 🚀 Instalación y Ejecución

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/TU-USUARIO/odoo-art-marketplace.git
    cd odoo-art-marketplace