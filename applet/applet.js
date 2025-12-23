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

        this.settings.bindProperty(
            Settings.BindingDirection.IN,
            "keyOpen",
            "keyOpen",
            this._onKeybindingChanged.bind(this),
            null
        );

        this._applyAppearance();
        this._onKeybindingChanged();
    }

    on_applet_clicked(event) {
        this._openMenu();
    }

    _openMenu() {
        GLib.spawn_command_line_async("eta-menu");
    }

    _applyAppearance() {
        const lbl = (this.appletLabel || "Pardus").trim();
        this.set_applet_label(" " + lbl);

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

    _onKeybindingChanged() {
        try {
            Main.keybindingManager.removeHotKey("eta-menu-hotkey");
        } catch (e) {}

        if (this.keyOpen && this.keyOpen.length > 0) {
            Main.keybindingManager.addHotKey(
                "eta-menu-hotkey",
                this.keyOpen,
                () => this._openMenu()
            );
        }
    }

    on_applet_removed_from_panel() {
        try {
            Main.keybindingManager.removeHotKey("eta-menu-hotkey");
        } catch (e) {}

        if (this.settings) {
            this.settings.finalize();
        }
    }
}

function main(metadata, orientation, panel_height, instance_id) {
    return new EtaMenu(metadata, orientation, panel_height, instance_id);
}
