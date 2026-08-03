// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
	refresh: function(frm) {
        frm.add_custom_button(__("Sales Order"),()=>{
            if(frm.doc.customer) {
                // MultiSelectDialog for individual child selection
                new frappe.ui.form.MultiSelectDialog({
                    doctype: "Sales Order",
                    target: this.cur_frm,
                    setters: {
                        customer: frm.doc.customer,
                        customer_po_date:null,
                        status: "Open",
                    },
                    add_filters_group: 1,
                    date_field: "customer_po_date",
                    allow_child_item_selection: 1,
                    child_fieldname: "component_list", // child table fieldname, whose records will be shown & can be filtered
                    child_columns: ["component_code","pending_qty","delivery_date"], // child item columns to be displayed
                    get_query() {
                        return {
                            filters: { 
                                docstatus: ["=", 1],
                                status:["=","Open"],
                                customer:["=", frm.doc.customer],
                                pending_qty:[">",0]
                                //["PWO Process Table","p_qty",">", 0],
                                
                            },                       
                        }
                    },
                    action(selections, args) {
                        selections.forEach(function(so_id){
                            if(so_id){
                                frappe.call({
                                    method: 'frappe.client.get',
                                    args: {
                                        doctype: "Sales Order",
                                        filters: {
                                            name: so_id
                                        }
                                    },
                                    callback: function(r) {
                                        if (r.message) {                                                                         
                                            r.message.component_list.forEach(function(component_lists) {
                                                var so_comp = args.filtered_children;
                                                if(so_comp.length){
                                                    // frappe.msgprint("Item selected")
                                                    so_comp.forEach(function(so_comps){
                                                        if(so_comps == component_lists.name) {
                                                            frappe.msgprint("Selected Components are loaded",component_lists.name)
                                                            insert_items(frm, so_id, component_lists, r);                                                        
                                                        }                                                            
                                                    })
                                                } else{
                                                    frappe.msgprint("All operations loaded")
                                                    insert_items(frm, so_id, component_lists, r);
                                                }
                                                
                                            });
                                            frm.refresh_field('sales_item_list');
                                        }
                                    }
                                });                            
                            }
                        })
                        cur_dialog.hide();
                    }
                });
            } else{
                frappe.throw("Please select the customer");
            }
        }, __("Get Items from"));

        // frm.add_custom_button(__("RM Batch"),()=>{
        //     if(frm.doc.mot == "RM") {
        //         // MultiSelectDialog for individual child selection
        //         new frappe.ui.form.MultiSelectDialog({
        //             doctype: "RM Batch",
        //             target: this.cur_frm,
        //             setters: {
        //                 rm_id: null,
        //                 date: null,
        //                 rm_qty: null,
        //                 p_qty: null,
        //             },
        //             add_filters_group: 1,
        //             date_field: "date",
        //             get_query() {
        //                 return {
        //                     filters: { 
        //                         // docstatus: ["=", 1],
        //                         p_qty:[">",0],
        //                     }                       
        //                 }
        //             },
        //             action(selections, args) {
        //                 selections.forEach(function(rmb_id){
        //                     if(rmb_id){
        //                         frappe.call({
        //                             method: 'frappe.client.get',
        //                             args: {
        //                                 doctype: "RM Batch",
        //                                 filters: {
        //                                     name: rmb_id
        //                                 }
        //                             },
        //                             callback: function(r) {
        //                                 if (r.message) {  
        //                                     frappe.msgprint("Selected Raw Material & Batch are loaded")
        //                                     var child = frm.add_child('rm_table');
        //                                     child.component_code = r.message.rm_id;
        //                                     child.rm_batch = rmb_id;
        //                                     child.qty = r.message.p_qty;
        //                                     frm.refresh_field('rm_table');
        //                                 }
        //                             }
        //                         }
        //                     );
        //                     }
        //                 });                                 
        //                 cur_dialog.hide();
        //             }
        //         });
        //     } else{
        //         frappe.throw("Please select the Material Out Type RM");
        //     }
        // }, __("Get Items from"));
    
    },
    before_save: function(frm) {
        return frm.call({
           doc: frm.doc,
           method: "auto_load_pwo",
           freeze: true,
           callback: (response) => {
               console.log(response.message);
           },
       });
     },
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
    validate: function(frm, cdt, cdn) {
        cal_data(frm, cdt, cdn);
    },
});

function insert_items(frm, so_id, component_lists, r) {
    var child = frm.add_child('sales_item_list');
    child.component_code = component_lists.component_code;
    child.uom = component_lists.uom
    child.price = component_lists.selling_price;
    child.sales_order = so_id;
    child.sa_delivery_date = component_lists.delivery_date;
    child.qty = component_lists.pending_qty;
    child.sales_tax_percentage = component_lists.sales_tax_percentage;
}

frappe.ui.form.on('Sales Invoice Table', {
    qty: function (frm, cdt, cdn) {
        cal_data(frm, cdt, cdn);
    },
    price: function(frm, cdt, cdn) {
        cal_data(frm, cdt, cdn);
    },
   
});

function cal_data(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if(d.qty){
        frappe.model.set_value(cdt, cdn, 'b_t_line_total', d.qty*d.price);
        refresh_field("b_t_line_total");
        frappe.model.set_value(cdt, cdn, 'a_t_line_total', d.qty*d.price*(d.sales_tax_percentage+100)/100);
        refresh_field("a_t_line_total");
    }
    
    // calculate total qty,basic amt, total amount
    let total_qty = 0;
    let basic_total = 0;
    let tax_total = 0;
    let total_amount=0;
    frm.doc.sales_item_list.forEach(function(a) {
        a.b_t_line_total= a.qty*a.price;
        a.a_t_line_total= a.qty*a.price*(a.sales_tax_percentage+100)/100;
        total_qty += a.qty || 0;
        basic_total += (a.qty * a.price) || 0;
        tax_total += (a.sales_tax_percentage * a.price/100)*a.qty || 0;
        total_amount += ((a.sales_tax_percentage+100) * a.qty * a.price/100) || 0;
        frm.refresh_field('sales_item_list');
    });
    frm.set_value("total_qty", total_qty);
    refresh_field("total_qty");
    frm.set_value("basic_amount", basic_total);
    refresh_field("basic_amount");
    frm.set_value("tax_amount", tax_total);
    refresh_field("tax_amount");
    frm.set_value("total_amount", total_amount);
    refresh_field("total_amount");
}