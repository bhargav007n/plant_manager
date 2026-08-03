// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Conversion Log", {
	onload: function(frm) {
        // frm.set_query('from_batch', function() {
        //     return {
        //         filters: [
        //             ['Production Work Order', 'pwo_status', '=', 'Open'],
        //        ]
        //     };
        // });
        frm.set_query('from_operation_id', function() {
            return {
                filters: [
                    ['Process Operation', 'comp_code', '=', frm.doc.from_component_id],
               ]
            };
        });

        frm.set_query('fos', function() {
            return {
                filters: [
                    ['Operation Status', 'operation_status', 'in', 'Pending, Vendor, Rework, Rejected'],
               ]
            };
        });
        frm.set_query('to_operation_id', function() {
            return {
                filters: [
                    ['Process Operation', 'comp_code', '=', frm.doc.to_component_id],
               ]
            };
        });
        frm.set_query('tos', function() {
            return {
                filters: [
                    ['Operation Status', 'operation_status', 'in', 'Pending, Vendor, Rework, Rejected, Completed'],
               ]
            };
        });
    },
});
