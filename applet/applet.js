const Applet = imports.ui.applet;
const Main = imports.ui.main;
const Settings = imports.ui.settings;
const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;
const Util = imports.misc.util;

class EtaMenu extends Applet.TextIconApplet {
    constructor(metadata, orientation, panel_height, instance_id) {
        super(orientation, panel_height, instance_id);

        this.settings = new Settings.AppletSettings(this, metadata.uuid, instance_id);

        this.settings.bindProperty(
            Settings.BindingDirection.IN,
            "appletLabel",
            "appletLabel",
            this._applyAppearance.bind(this),
            null
        );

        this.settings.bindProperty(
            Settings.BindingDirection.IN,
            "appletIcon",
            "appletIcon",
            this._applyAppearance.bind(this),
            null
        );

        this.settings.bindProperty(
            Settings.BindingDirection.IN,
            "iconSize",
            "iconSize",
            this._applyAppearance.bind(this),
            null
        );

        this._applyAppearance();
        this._registerHotkeys();
    }

    on_applet_clicked(event) {
        this._openMenu();
    }

    _openMenu() {
        try {
            let appInfo = Gio.DesktopAppInfo.new("tr.org.pardus.eta-menu.desktop");
            if (appInfo) {
                let context = global.create_app_launch_context(0, -1);
                appInfo.launch([], context);
                return;
            }
        } catch (e) {
            global.logError(e);
        }

        Util.spawnCommandLine("systemd-run --user eta-menu");
    }

    _applyAppearance() {
        const lbl = (this.appletLabel || " P A R D U S ");
        this.set_applet_label(lbl);

        const icon = (this.appletIcon && this.appletIcon.length > 0) ? this.appletIcon : "eta-menu";

        if (icon.indexOf("/") !== -1) {
            this.set_applet_icon_path(icon);
        } else {
            this.set_applet_icon_name(icon);
        }

        const size = parseInt(this.iconSize, 10);
        if (this._applet_icon && Number.isFinite(size) && size > 0) {
            this._applet_icon.set_icon_size(size);
        }
    }

    _registerHotkeys() {
        this._unregisterHotkeys();

        // Hardcoded: Super_L and Super_R
        try {
            Main.keybindingManager.addHotKey(
                "eta-menu-hotkey-left",
                "Super_L",
                () => this._openMenu()
            );
        } catch (e) {
            global.logError(e);
        }

        try {
            Main.keybindingManager.addHotKey(
                "eta-menu-hotkey-right",
                "Super_R",
                () => this._openMenu()
            );
        } catch (e) {
            global.logError(e);
        }
    }

    _unregisterHotkeys() {
        try { Main.keybindingManager.removeHotKey("eta-menu-hotkey-left"); } catch (e) {}
        try { Main.keybindingManager.removeHotKey("eta-menu-hotkey-right"); } catch (e) {}
    }

    on_applet_removed_from_panel() {
        this._unregisterHotkeys();

        if (this.settings) {
            this.settings.finalize();
        }
    }
}

function main(metadata, orientation, panel_height, instance_id) {
    return new EtaMenu(metadata, orientation, panel_height, instance_id);
}
