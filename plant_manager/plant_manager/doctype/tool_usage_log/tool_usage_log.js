// Copyright (c) 2026, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tool Usage Log", "onload", function(frm) {
	
});

frappe.ui.form.on("Tool Usage Log", {
    onload: function(frm) {
        frm.set_query("returned_against", function() {
        return {
           "filters": {
                // ['Process Operation','tool_name', 'in', frm.doc.tool_name],
                "tool_name":frm.doc.tool_name,
                "returned_transaction": "",
                "transaction_type":"issue"

            }
        };
    });
    },

    //refresh fields
    tool_type: function(frm) {
        frm.set_value('tool_name', '');
        frm.set_value('returned_against', '');
        frm.set_value('transaction_type', '');
        },

    tool_name:function(frm) {
        frm.set_value('returned_against', '');
        }
});