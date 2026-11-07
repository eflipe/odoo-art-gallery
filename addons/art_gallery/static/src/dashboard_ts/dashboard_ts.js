/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ArtGalleryDashboardTs extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({ artworks: [] });
        onWillStart(async () => {
            await this.loadArtworks();
        });
    }
    async loadArtworks() {
        const data = await this.orm.call("art_gallery.artwork", "get_dashboard_data", []);
        this.state.artworks = data;
    }
}
ArtGalleryDashboardTs.template = "art_gallery.DashboardTsTemplate";
registry.category("actions").add("art_gallery.dashboard_ts", ArtGalleryDashboardTs);
