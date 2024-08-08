frappe.ui.keys.add_shortcut({
    description:"Open Ctrl + Shift + S Report",
    shortcut:"shift+ctrl+s",
    action:()=>{
        frappe.open_in_new_tab = true;
        frappe.set_route("query-report","Ctrl + Shift + S")
    }
})