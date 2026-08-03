// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rejection Log", {
	refresh:function(frm) {
        frm.set_value('created_by', frappe.session.user);
        refresh_field('created_by');
    },
	onload: function(frm) {
        frm.set_query('opt_id', 'rej_lst', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                'filters': [
                    ['Process Operation','comp_code', 'in', d.comp_code],
                ],
            };
        });
        frm.set_query('rej_frm', 'rej_lst', function() {
            return {
                'filters': [
                    ['Operation Status', 'operation_status', 'in', 'Completed, Rework'],
                    ],
            };
        });
        frm.set_query('batch', 'rej_lst', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                'filters': [
                    ['Production Work Order', 'comp_code', 'in', d.comp_code],
                    ],
            };
        });
    },
    before_cancel: function(frm) {
        return frm.call({
           doc: frm.doc,
           method: "delete_ssl_entry",
           freeze: true,
           callback: (response) => {
               console.log(response.message);
               console.log("delete_ssl_entry");
           },
       });
    },
});

frappe.ui.form.on('Rejection Table', {
         
    rwk_lst_add(frm, cdt, cdn) {
        frappe.db.get_single_value('Master Settings', 'default_production_warehouse')
        .then(r_wh => {
            frappe.model.set_value(cdt, cdn, 'f_wh', r_wh);
            refresh_field('f_wh');
        });

        frappe.db.get_single_value('Master Settings', 'default_rejected_warehouse')
        .then(p_wh => {
            frappe.model.set_value(cdt, cdn, 't_wh', p_wh);
            refresh_field('t_wh');
        });              
    },
});