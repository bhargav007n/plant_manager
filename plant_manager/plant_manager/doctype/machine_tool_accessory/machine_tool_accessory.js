// Copyright (c) 2026, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Machine Tool Accessory", {
	onload: function(frm) {
        frm.set_query("prefix", function() {
        return {
           "filters": {
                "accessory_type":frm.doc.accessory_type,
            }
        };
    });
    },
    accessory_type:function(frm) {
        frm.set_value('prefix', '');
    }

	});
