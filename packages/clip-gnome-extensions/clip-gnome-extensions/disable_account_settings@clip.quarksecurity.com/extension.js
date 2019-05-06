const St = imports.gi.St;
const Main = imports.ui.main;

function init() {
}

function enable() {
  var menuItems = Main.panel.statusArea.aggregateMenu._system._switchUserSubMenu.menu._getMenuItems();
  menuItems[menuItems.length -1].destroy();  
}

function disable() {
}
