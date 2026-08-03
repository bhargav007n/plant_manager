// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order", {
        

    after_save: function(frm) {
        return frm.call({
           doc: frm.doc,
           method: "update_pending_qty",
           freeze: true,
           callback: (response) => {
               console.log(response.message);
           },
       });
     },
     validate: function(frm, cdt, cdn) {
        cal_data(frm, cdt, cdn);
    },

});

frappe.ui.form.on('Sales Order Items', {
    qty: function (frm, cdt, cdn) {
        cal_data(frm, cdt, cdn);
    },
    selling_price: function(frm, cdt, cdn) {
        cal_data(frm, cdt, cdn);
    },
});
    

function cal_data(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if(d.qty){
        frappe.model.set_value(cdt, cdn, 'pending_qty', d.qty);
        refresh_field("pending_qty");
    }
    
    // calculate total qty,basic amt, total amount
    let total_qty = 0;
    let basic_total = 0;
    let tax_total = 0;
    frm.doc.component_list.forEach(function(a) {
        total_qty += a.qty || 0;
        basic_total += (a.qty * a.selling_price) || 0;
        tax_total += ((a.sales_tax_percentage+100) * a.qty * a.selling_price/100) || 0;
    });
    frm.set_value("total_order_qty", total_qty);
    refresh_field("total_order_qty");
    frm.set_value("basic_amount", basic_total);
    refresh_field("basic_amount");
    frm.set_value("total_amount", tax_total);
    refresh_field("total_amount");
}