const Applet = imports.ui.applet;
const Lang = imports.lang;
const Main = imports.ui.main;
const Settings = imports.ui.settings;
const GLib = imports.gi.GLib;

class EtaMenu extends Applet.TextIconApplet {
    constructor(metadata, orientation, panel_height, instance_id) {
        super(orientation, panel_height, instance_id);

        try {
            this.set_applet_icon_symbolic_name("eta-menu-panel");
            this.set_applet_label("Pardus");


        }
        catch (e) {
            global.logError(e);
        }
    }

    on_applet_clicked(event) {
        GLib.spawn_command_line_async('eta-menu');
    }

}

function main(metadata, orientation, panel_height, instance_id) {
    return new EtaMenu(metadata, orientation, panel_height, instance_id);
}
