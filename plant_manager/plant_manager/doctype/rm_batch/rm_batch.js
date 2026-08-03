// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("RM Batch", {
	refresh(frm) {
        frm.set_query("component_id", "rm_consumtion", function(doc, cdt, cdn) {
            return {
                "filters": {
                    "is_disabled": 0
                }
            };
        });

	},
});
