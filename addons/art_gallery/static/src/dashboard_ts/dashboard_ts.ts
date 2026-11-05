/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Artwork } from "./artwork.types";

export class ArtGalleryDashboardTs extends Component {
    static template = "art_gallery.DashboardTsTemplate";

    setup() {
        this.state = useState<{ artworks: Artwork[] }>({ artworks: [] });

        onWillStart(async () => {
            this.state.artworks = [
                { id: 1, name: "La noche estrellada", artist_name: "Vincent van Gogh", year: 1889, image: null },
                { id: 2, name: "El grito", artist_name: "Edvard Munch", year: 1893, image: null },
                { id: 3, name: "La persistencia de la memoria", artist_name: "Salvador Dalí", year: 1931, image: null },
            ];
        });
    }
}

registry.category("actions").add("art_gallery.dashboard_ts", ArtGalleryDashboardTs);