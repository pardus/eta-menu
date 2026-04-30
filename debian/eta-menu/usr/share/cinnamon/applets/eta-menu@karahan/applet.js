const Applet = imports.ui.applet;
const Settings = imports.ui.settings;
const Main = imports.ui.main;
const GLib = imports.gi.GLib;

const St = imports.gi.St;
const Gio = imports.gi.Gio;


class EtaMenuApplet extends Applet.TextIconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);

        this.settings = new Settings.AppletSettings(this, metadata.uuid, instanceId);

        this.settings.bind("menu-command", "menuCommand");
        this.settings.bind("use-icon", "useIcon", this._updateAppearance.bind(this));
        this.settings.bind("use-label", "useLabel", this._updateAppearance.bind(this));
        this.settings.bind("icon-name", "iconName", this._updateAppearance.bind(this));
        this.settings.bind("label-text", "labelText", this._updateAppearance.bind(this));
        this.settings.bind("overlay-key", "overlayKey", this._updateKeybinding);
       this.settings.bind("icon-size", "menuIconSize", this._updateAppearance.bind(this));


        this.set_applet_tooltip("Eta Menu");

        this._updateAppearance();
 this._updateKeybinding();

    }

_updateKeybinding() {
        global.logError("tuşa basıldı boş!");
    if (this._hotkeyId)
        Main.keybindingManager.removeHotKey(this._hotkeyId);

    this._hotkeyId = Main.keybindingManager.addHotKey(
        "eta-menu-overlay-" + this.instance_id,
        this.overlayKey,
        () => {
            this.on_applet_clicked();
        }
    );
}

_updateAppearance() {
    // Label fallback
    let text = (this.useLabel && this.labelText && this.labelText.length > 0) 
                ? this.labelText 
                : (this.useLabel ? "Menu" : "");

    // 1️⃣ Sadece metin
    if (!this.useIcon && this.useLabel) {
        this._applet_icon_box.hide();
        this.set_applet_label(text);
    } 
    // 2️⃣ Sadece ikon
    else if (this.useIcon && !this.useLabel) {
        this.set_applet_label("");
        this._applet_icon_box.show();
		let iconToUse = (this.iconName && this.iconName.includes("-symbolic"))
				        ? this.iconName
				        : "eta-menu-symbolic";

		this.set_applet_icon_symbolic_name(iconToUse);


        // Boyutu uygula
        if (this._applet_icon_box.get_children().length > 0) {
            this._applet_icon_box.get_children()[0].set_icon_size(this.menuIconSize);
        }
    } 
    // 3️⃣ İkon + metin
    else if (this.useIcon && this.useLabel) {
        this._applet_icon_box.show();
        this.set_applet_label(text);

        let iconToUse = (this.iconName && this.iconName.includes("-symbolic"))
                        ? this.iconName
                        : "eta-menu-symbolic";

        this.set_applet_icon_symbolic_name(iconToUse);

        // Boyutu uygula
        if (this._applet_icon_box.get_children().length > 0) {
            this._applet_icon_box.get_children()[0].set_icon_size(this.menuIconSize);
        }
    } 
    // 4️⃣ Ne ikon ne metin seçili → fallback ikon
    else {
        this._applet_icon_box.show();
        this.set_applet_icon_symbolic_name("eta-menu-symbolic");
        this.set_applet_label("");

        if (this._applet_icon_box.get_children().length > 0) {
            this._applet_icon_box.get_children()[0].set_icon_size(this.menuIconSize);
        }
        let fullIcon = new St.Icon({
    gicon: Gio.icon_new_for_string(this.path + "/icons/eta-menu.svg"),
    icon_size: this.menuIconSize
});
this._applet_icon_box.add_child(fullIcon);

    }

    // Tooltip
    this.set_applet_tooltip(text);
}


    on_applet_clicked() {
        if (!this.menuCommand) {
            global.logError("menuCommand boş!");
            return;
        }
        GLib.spawn_command_line_async(this.menuCommand);
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new EtaMenuApplet(metadata, orientation, panelHeight, instanceId);
}

