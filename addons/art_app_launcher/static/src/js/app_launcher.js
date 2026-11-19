/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AppLauncher extends Component {
    static template = "art_app_launcher.AppLauncher";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            apps: [],
            loading: true,
        });

        onWillStart(async () => {
            this.state.apps = await this.orm.call("ir.ui.menu", "get_app_launcher_data", []);
            this.state.loading = false;
        });
    }

    getIconUrl(icon) {
        if (!icon) {
            return false;
        }

        // Si ya viene con el prefijo de datos (base64), lo devolvemos tal cual
        if (icon.startsWith("data:image")) {
            return icon;
        }

        if (icon.startsWith("/")) {
            return icon;
        }

        // Common format: "module,static/...".
        if (icon.includes(",")) {
            const [moduleName, relPath] = icon.split(",", 2);
            if (moduleName && relPath) {
                return `/${moduleName}/${relPath}`;
            }
        }

        return icon;
    }

    openApp(app) {
        if (!app || !app.action) {
            return;
        }
        this.action.doAction(app.action);
    }
}

registry.category("actions").add("art_app_launcher", AppLauncher);

