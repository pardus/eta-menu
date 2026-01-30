const Applet = imports.ui.applet;
const Main = imports.ui.main;
const Settings = imports.ui.settings;
const GLib = imports.gi.GLib;

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
        GLib.spawn_command_line_async("eta-menu");
    }

    _applyAppearance() {
        const lbl = (this.appletLabel || " P A R D U S ");
        this.set_applet_label(lbl);

        const icon = (this.appletIcon && this.appletIcon.length > 0) ? this.appletIcon : "eta-start";

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
