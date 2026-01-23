// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cutting Tool", {
	onload: function(frm) {
        frm.set_query("prefix", function() {
        return {
           "filters": {
                "cutting_tool_type":frm.doc.cutting_tool_type,
            }
        };
    });
    },
    cutting_tool_type:function(frm) {
        frm.set_value('prefix', '');
    }

});
