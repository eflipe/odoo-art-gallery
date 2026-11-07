/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Artwork } from "./artwork.types";

export class ArtGalleryDashboardTs extends Component {
    static template = "art_gallery.DashboardTsTemplate";

    setup() {
        this.orm = useService("orm");
        this.state = useState<{ artworks: Artwork[] }>({ artworks: [] });

        onWillStart(async () => {
            await this.loadArtworks();
        });
    }

    async loadArtworks() {
        const data = await this.orm.call(
            "art_gallery.artwork",
            "get_dashboard_data",
            []
        );
        this.state.artworks = data as Artwork[];
    }
}

registry.category("actions").add("art_gallery.dashboard_ts", ArtGalleryDashboardTs);