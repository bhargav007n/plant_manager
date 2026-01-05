// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset", {
	refresh(frm) {
        if (frm.doc.type_of_consumption == "Single-use") {
            frm.fields_dict["usage_log"].grid.toggle_enable("consumed_qty", true);
        } else {
            frm.fields_dict["usage_log"].grid.toggle_enable("consumed_qty", false);
        }
        frm.refresh_field("usage_log");
	},
});
