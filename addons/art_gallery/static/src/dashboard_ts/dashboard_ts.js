/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
export class ArtGalleryDashboardTs extends Component {
    setup() {
        this.state = useState({ artworks: [] });
        onWillStart(async () => {
            this.state.artworks = [
                { id: 1, name: "La noche estrellada", artist_name: "Vincent van Gogh", year: 1889, image: null },
                { id: 2, name: "El grito", artist_name: "Edvard Munch", year: 1893, image: null },
                { id: 3, name: "La persistencia de la memoria", artist_name: "Salvador Dalí", year: 1931, image: null },
            ];
        });
    }
}
ArtGalleryDashboardTs.template = "art_gallery.DashboardTsTemplate";
registry.category("actions").add("art_gallery.dashboard_ts", ArtGalleryDashboardTs);
