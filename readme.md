# 🎨 Odoo Art Gallery & Marketplace

![Odoo Version](https://img.shields.io/badge/Odoo-19.0-purple?style=for-the-badge&logo=odoo)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=for-the-badge&logo=typescript)
![License](https://img.shields.io/badge/License-LGPL--3-green?style=for-the-badge)

Una solución ERP/E-commerce completa para la gestión y venta de obras de arte, construida sobre **Odoo 19**. Este proyecto implementa la lógica real de negocio de una galería de arte, incluyendo la gestión de artistas como entidades, el reparto de comisiones (Split), la doble facturación (Cliente/Artista) y un portal web público para recibir solicitudes de compra.

## 🚀 Características Principales

*   **Gestión de Artistas y Obras (`art_gallery`):** Importación automática desde la API del Art Institute of Chicago. Los artistas son entidades reales con biografía, comisión y contacto (`res.partner`) asociado.
*   **Flujo de Venta Real (`art_marketplace`):** Publicación de obras, control de disponibilidad, y cálculo automático de la comisión del artista (Split) en tiempo real.
*   **Contabilidad de Doble Partida:** Al concretar una venta, el sistema genera automáticamente dos facturas en Odoo: una **Factura de Cliente** por el 100% del valor (Ingreso) y una **Factura de Proveedor** por la comisión del artista (Costo/Pasivo).
*   **Gestión de Tickets (Leads):** Un portal web público permite a los clientes mostrar interés. El galerista gestiona estos tickets (New -> Contacted -> Won) y evita la duplicación de contactos.
*   **App Launcher Personalizado (`art_app_launcher`):** Un reemplazo nativo del menú de aplicaciones, con una grilla visual (OWL) de todas las apps instaladas, accesible desde el systray (botón 🏠).
*   **Dashboards Interactivos:** Dashboards en JavaScript y TypeScript para filtrar y visualizar el catálogo de obras.

## 🛠️ Requisitos Previos

*   **Docker** y **Docker Compose** instalados.
*   **Git** para clonar el repositorio.
*   **Node.js** (opcional, solo si deseas recompilar el dashboard en TypeScript).

## 📦 Instalación y Ejecución

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/TU-USUARIO/odoo-art-marketplace.git
    cd odoo-art-marketplace