// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Process Operation Sequence", {
	refresh: function(frm) {
        frm.set_query("operation_code", "pos", function(doc, cdt, cdn) {
            return {
                "filters": {
                    "comp_code": frm.doc.component_code
                }
            };
        });
    },
});
