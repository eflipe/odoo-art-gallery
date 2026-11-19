/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ArtAppLauncherHomeSystray extends Component {
    static template = "art_app_launcher.HomeSystray";

    setup() {
        this.action = useService("action");
    }

    openLauncher() {
        this.action.doAction("art_app_launcher.action_art_app_launcher");
    }
}

registry.category("systray").add("art_app_launcher.home", {
    Component: ArtAppLauncherHomeSystray,
    isDisplayed: () => true,
    sequence: 0,
});

