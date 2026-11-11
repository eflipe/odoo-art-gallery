/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
export class ArtGalleryDashboardTs extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            artworks: [],
            yearFrom: null,
            yearTo: null,
            isLoading: false,
            errorMsg: null
        });
        onWillStart(async () => {
            await this.loadArtworks();
        });
    }
    async loadArtworks() {
        // 1. Limpiamos errores previos y activamos el cargando
        this.state.errorMsg = null;
        // 2. Validación de datos
        if (this.state.yearFrom !== null && this.state.yearFrom < 0) {
            this.state.errorMsg = "El año 'Desde' no puede ser negativo.";
            return;
        }
        if (this.state.yearTo !== null && this.state.yearTo < 0) {
            this.state.errorMsg = "El año 'Hasta' no puede ser negativo.";
            return;
        }
        if (this.state.yearFrom !== null && this.state.yearTo !== null && this.state.yearFrom > this.state.yearTo) {
            this.state.errorMsg = "El año 'Desde' no puede ser mayor que el año 'Hasta'.";
            return;
        }
        this.state.isLoading = true;
        try {
            const data = await this.orm.call("art_gallery.artwork", "get_dashboard_data", [], {
                year_from: this.state.yearFrom,
                year_to: this.state.yearTo
            });
            this.state.artworks = data;
        }
        catch (error) {
            console.error("Error loading artworks", error);
            this.state.errorMsg = "Ocurrió un error al conectar con el servidor.";
        }
        finally {
            this.state.isLoading = false;
        }
    }
    async onApplyFilter() {
        await this.loadArtworks();
    }
    async onClearFilter() {
        this.state.yearFrom = null;
        this.state.yearTo = null;
        await this.loadArtworks();
    }
}
ArtGalleryDashboardTs.template = "art_gallery.DashboardTsTemplate";
registry.category("actions").add("art_gallery.dashboard_ts", ArtGalleryDashboardTs);
