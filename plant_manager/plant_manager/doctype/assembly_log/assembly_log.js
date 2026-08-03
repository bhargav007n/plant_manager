// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assembly Log", {
	before_cancel: function(frm) {
        return frm.call({
           doc: frm.doc,
           method: "delete_disp_entry",
           freeze: true,
           callback: (response) => {
               console.log(response.message);               
           },
       });
    },
    onload: function(frm) {
        frm.set_query('batch', 'acp', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                'filters': [
                    ['Production Work Order','comp_code', 'in', d.comp_id],
                ],
            };
        });
        frm.set_query('assembly_operation', function() {
            return {
                'filters': [
                    ['Process Operation','comp_code', 'in', frm.doc.comp_id],
                ],
            };
        });
    },
    asb_qty: function(frm) {
		return frm.call({
			doc: frm.doc,
			method: "load_bom",
			freeze: true,
			callback: (response) => {
                console.log(response.message);
			},
		});
 	},
    assembly_bom: function (frm) {
		frm.trigger("asb_qty");
	},
    refresh(frm) {
        frm.add_custom_button(__('Validate'), function() {
            return frm.call({
                doc: frm.doc,
                method: "external_validation",
                freeze: true,
                callback: (response) => {
                    console.log(response.message);
                    frappe.msgprint('Validation Successful.');
			},
		});
        });
    }
});
