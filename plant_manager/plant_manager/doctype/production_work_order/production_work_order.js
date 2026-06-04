// Copyright (c) 2024, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Production Work Order", {
 	pos: function(frm) {
		return frm.call({
			doc: frm.doc,
			method: "load_operation",
			freeze: true,
			callback: (response) => {
                console.log(response.message);
			},
		});
 	},

    pwo_qty: function (frm) {
		frm.trigger("pos");
	},

	after_save:function(frm) {
		if (frm.doc.docstatus === 1) {
			return frm.call({
				doc: frm.doc,
				method: "before_save_trigger",
				freeze: true,
				callback: (response) => {
					console.log(response.message);
					console.log("before save triggered");
				},
			});
		}
 	},
 });

 frappe.ui.form.on('PWO SSL', {
	qty: function(frm) {
		console.log("calculation triggered by qty");
        return frm.call({
			doc: frm.doc,
            method: "before_save_trigger",
            freeze: true,
            callback:  (r) => {
                console.log(r.message);
            },
        });
    },
	process_id: function (frm) {
		console.log("calculation triggered by processid");
        return frm.call({
			doc: frm.doc,
            method: "before_save_trigger",
            freeze: true,
            callback:  (r) => {
                console.log(r.message);
            },
        });
	},
 }
);