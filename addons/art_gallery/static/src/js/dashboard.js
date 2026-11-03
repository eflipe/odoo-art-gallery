/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Pager } from "@web/core/pager/pager"; // <-- Importa el Pager

export class ArtGalleryDashboard extends Component {
    static template = "art_gallery.Dashboard";
    static components = { Pager }; // <-- Regístralo para usarlo en la plantilla

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            artworks: [],
            total: 0,
            offset: 0,
            limit: 10,
            loading: true,
        });

        onWillStart(async () => {
            await this.loadArtworks();
        });
    }

    async loadArtworks() {
        this.state.loading = true;
        const result = await this.orm.call(
            "art_gallery.artwork",
            "get_gallery_data",
            [],
            { offset: this.state.offset, limit: this.state.limit }
        );
        this.state.artworks = result.artworks;
        this.state.total = result.total;
        this.state.loading = false;
    }

    async onPagerUpdate(newState) {
        this.state.offset = newState.offset;
        this.state.limit = newState.limit;
        await this.loadArtworks();
    }
}

registry.category("actions").add("art_gallery.dashboard", ArtGalleryDashboard);