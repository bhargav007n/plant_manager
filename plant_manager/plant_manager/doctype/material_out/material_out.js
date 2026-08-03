// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material Out", {
    refresh: function(frm) {
        frm.add_custom_button(__("Production Work Order"),()=>{
            if(frm.doc.vdr) {
                //frm.clear_table('component_table');
                //frappe.msgprint("Vendor Selected");  

                // MultiSelectDialog for individual child selection
                new frappe.ui.form.MultiSelectDialog({
                    doctype: "Production Work Order",
                    target: this.cur_frm,
                    setters: {
                        comp_code: null,
                        pos:null,
                        pwo_date: null,
                        // osd: {
                        //     opt_name: null,
                        // },
                    },
                    add_filters_group: 1,
                    date_field: "pwo_date",
                    allow_child_item_selection: 1,
                    child_fieldname: "osd", // child table fieldname, whose records will be shown & can be filtered
                    child_columns: ["opt_id","p_qty","moved_to_vendor","o_rwk_qty", "o_comp_qty"], // child item columns to be displayed
                    get_query() {
                        return {
                            filters: { 
                                docstatus: ["=", 1],
                                //["PWO Process Table","p_qty",">", 0],
                                pwo_status:["=","Open"]
                            }                       
                        }
                    },
                    action(selections, args) {
                        //console.log(selections);
                        //console.log(args.filtered_children); // list of selected item names
                        selections.forEach(function(pwo_id){
                            if(pwo_id){
                                frappe.call({
                                    method: 'frappe.client.get',
                                    args: {
                                        doctype: "Production Work Order",
                                        filters: {
                                            name: pwo_id
                                        }
                                    },
                                    callback: function(r) {
                                        if (r.message) {                                                                         
                                            r.message.osd.forEach(function(osds) {
                                                var pwo_opt = args.filtered_children;
                                                if(pwo_opt.length){
                                                    // frappe.msgprint("Item selected")
                                                    pwo_opt.forEach(function(pwo_opts){
                                                        if(pwo_opts == osds.name) {
                                                            frappe.msgprint("Selected Components & Operations are loaded",osds.name)
                                                            insert_items(frm, pwo_id, osds, r);                                                        
                                                        }                                                            
                                                    })
                                                } else{
                                                    frappe.msgprint("All operations loaded")
                                                    insert_items(frm, pwo_id, osds, r);
                                                }
                                                
                                            });
                                            frm.refresh_field('component_table');
                                        }
                                    }
                                });                            
                            }
                        })
                        cur_dialog.hide();
                    }
                });
            } else{
                frappe.throw("Please select the Vendor");
            }
        }, __("Get Item with operation from"));

        frm.add_custom_button(__("RM Batch"),()=>{
            if(frm.doc.mot == "RM") {
                // MultiSelectDialog for individual child selection
                new frappe.ui.form.MultiSelectDialog({
                    doctype: "RM Batch",
                    target: this.cur_frm,
                    setters: {
                        rm_id: null,
                        date: null,
                        rm_qty: null,
                        p_qty: null,
                    },
                    add_filters_group: 1,
                    date_field: "date",
                    get_query() {
                        return {
                            filters: { 
                                // docstatus: ["=", 1],
                                p_qty:[">",0],
                            }                       
                        }
                    },
                    action(selections, args) {
                        selections.forEach(function(rmb_id){
                            if(rmb_id){
                                frappe.call({
                                    method: 'frappe.client.get',
                                    args: {
                                        doctype: "RM Batch",
                                        filters: {
                                            name: rmb_id
                                        }
                                    },
                                    callback: function(r) {
                                        if (r.message) {  
                                            frappe.msgprint("Selected Raw Material & Batch are loaded")
                                            var child = frm.add_child('rm_table');
                                            child.component_code = r.message.rm_id;
                                            child.rm_batch = rmb_id;
                                            child.qty = r.message.p_qty;
                                            frm.refresh_field('rm_table');
                                        }
                                    }
                                }
                            );
                            }
                        });                                 
                        cur_dialog.hide();
                    }
                });
            } else{
                frappe.throw("Please select the Material Out Type RM");
            }
        }, __("Get Item with operation from"));
    
    }
});

function insert_items(frm, pwo_id, osds, r) {
    var child = frm.add_child('component_table');
    //console.log(pwo_id.comp_code);
    child.comp_code = r.message.comp_code;
    child.component_name = r.message.comp_name;
    child.batch = pwo_id;
    child.qty = osds.p_qty;
    child.for_process = osds.opt_id;
}

frappe.ui.form.on("Material Out", { 
    validate: function(frm) {
        //Asset
        let grand_total = 0;
        let total = 0;
        let ast_qty = 0;
        let comp_qty = 0;
        let rm_qty = 0;
        frm.doc.asset_table.forEach(function(a) {
            a.total_cost = a.qty * a.cost_per_uom ;
            grand_total += a.total_cost;
            ast_qty=ast_qty+a.qty;
        });
        frm.set_value("asset_total", grand_total);
        refresh_field("asset_total");
        frm.set_value("basic_total", frm.doc.component_total+frm.doc.asset_total+frm.doc.rm_total);
        refresh_field("basic_total");

        //Component
        grand_total = 0;
        total = 0;
        let grand_total_weight = 0;
        frm.doc.component_table.forEach(function(b) {
            b.total_cost = b.qty * b.cost_per_unit ;
            b.total_weight = b.qty * b.weight_per_unit;
            grand_total += b.total_cost ;
            grand_total_weight += b.total_weight ;
            comp_qty=comp_qty+b.qty;
        });
        frm.set_value("component_total", grand_total);
        refresh_field("component_total");
        frm.set_value("component_total__weight", grand_total_weight);
        refresh_field("component_total__weight");
        frm.set_value("basic_total", frm.doc.component_total+frm.doc.asset_total+frm.doc.rm_total);
        refresh_field("basic_total");

        //RM
        grand_total = 0;
        total = 0;
        frm.doc.rm_table.forEach(function(c) {
            c.total_cost = c.qty * c.cost_per_uom ;
            grand_total += c.total_cost ;
            rm_qty=rm_qty+c.qty;
        });
        frm.set_value("rm_total", grand_total);
        refresh_field("rm_total");
        frm.set_value("basic_total", frm.doc.component_total+frm.doc.asset_total+frm.doc.rm_total);
        refresh_field("basic_total");
        //console.log(frm.doc.component_total+frm.doc.asset_total+frm.doc.rm_total)
        frm.set_value("total_qty", ast_qty+comp_qty+rm_qty);
        refresh_field("total_qty");
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
    onload: function(frm) {
        frm.set_query('opt_stat', 'component_table', function() {
            return {
                'filters': [
                    ['Operation Status', 'operation_status', 'in', 'Vendor, Rework'],
                    ],
            };
        });
        
        
        frm.set_query('for_process', 'component_table', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                'filters': [
                    ['Process Operation','comp_code', 'in', d.comp_code],
                ],
            };
        });

        frm.set_query('batch', 'component_table', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                'filters': [
                    ['Production Work Order','comp_code', 'in', d.comp_code],
                ],
            };
        });

        frm.set_query('component_code', 'rm_table', function() {
            return {
                'filters': [
                    ['Component', 'is_rm', 'in', '1'],
                    ],
            };
        });
        frm.set_query('fg_component', 'rm_table', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                'filters': [
                    ['Component', 'rm_component', 'in', d.component_code],
                    ],
            };
        });
        frm.set_query('rm_batch', 'rm_table', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                'filters': [
                    ['RM Batch', 'rm_id', 'in', d.component_code],
                    ],
            };
        });

    },   
    d_from_warehouse:function(frm) {
        //console.log("wh triggered");
        //RM
        frm.doc.rm_table.forEach(function(a) {
            a.from_warehouse = frm.doc.d_from_warehouse;
            a.to_warehouse = frm.doc.d_to_warehouse;
        });
        refresh_field('rm_table_add')
        //Component
        frm.doc.component_table.forEach(function(b) {
            b.f_wh = frm.doc.d_from_warehouse;
            b.t_wh = frm.doc.d_to_warehouse;
        });
        refresh_field('component_table')
        //Asset
        frm.doc.asset_table.forEach(function(c) {
            c.from_warehouse = frm.doc.d_from_warehouse;
            c.to_warehouse = frm.doc.d_to_warehouse;
        });
        refresh_field('asset_table')
    },
    d_to_warehouse: function(frm) {
        frm.trigger("d_from_warehouse");
    },
});

frappe.ui.form.on('Material Out RM', {
    qty: function (frm, cdt, cdn) {
        cost_rm(frm, cdt, cdn);
    },
    cost_per_uom: function(frm, cdt, cdn) {
        cost_rm(frm, cdt, cdn);
    },
    rm_table_add(frm, cdt, cdn) {
        //console.log("wh triggered");
        frappe.model.set_value(cdt, cdn, 'from_warehouse', frm.doc.d_from_warehouse);
        frappe.model.set_value(cdt, cdn, 'to_warehouse', frm.doc.d_to_warehouse);
        refresh_field('rm_table_add')
    },
    

});
frappe.ui.form.on('Material Out Asset', {
    qty: function (frm, cdt, cdn) {
        cost_asset(frm, cdt, cdn);
    },
    cost_per_uom: function(frm, cdt, cdn) {
        cost_asset(frm, cdt, cdn);
    },
    asset_table_add:function(frm, cdt, cdn) {
        //console.log("wh triggered");
        frappe.model.set_value(cdt, cdn, 'from_warehouse', frm.doc.d_from_warehouse);
        frappe.model.set_value(cdt, cdn, 'to_warehouse', frm.doc.d_to_warehouse);
        refresh_field('asset_table')
    },
});
frappe.ui.form.on('Material Out Table', {
    qty: function (frm, cdt, cdn) {
        cost_comp(frm, cdt, cdn);
    },
    cost_per_unit: function(frm, cdt, cdn) {
        cost_comp(frm, cdt, cdn);
    },
    component_table_add:function(frm, cdt, cdn) {
        //console.log("wh triggered");
        frappe.model.set_value(cdt, cdn, 'f_wh', frm.doc.d_from_warehouse);
        frappe.model.set_value(cdt, cdn, 't_wh', frm.doc.d_to_warehouse);
        refresh_field('component_table')
    },
    
});

function cost_comp(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if(d.qty){
            frappe.model.set_value(cdt, cdn, 'pending_qty', d.qty);
        }
        d.total_cost = d.qty * d.cost_per_unit ;
        d.total_weight = d.qty * d.weight_per_unit;
        refresh_field("component_table");
        // calculate grand total
        let grand_total = 0;
        let total = 0;
        frm.doc.component_table.forEach(function(a) {
        grand_total += a.total_cost || 0;
        });
        frm.set_value("component_total", grand_total);
        refresh_field("component_total");
        frm.set_value("basic_total", frm.doc.component_total+frm.doc.asset_total+frm.doc.rm_total);
        refresh_field("basic_total");
    }

function cost_rm(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
        if(d.qty){
            frappe.model.set_value(cdt, cdn, 'pending_qty', d.qty);
        }
         d.total_cost = d.qty * d.cost_per_uom ;
        refresh_field("rm_table");
        // calculate grand total
        let grand_total = 0;
        let total = 0;
        frm.doc.rm_table.forEach(function(a) {
        grand_total += a.total_cost;
        });
        frm.set_value("rm_total", grand_total);
        refresh_field("rm_total");
        frm.set_value("basic_total", frm.doc.component_total+frm.doc.asset_total+frm.doc.rm_total);
        refresh_field("basic_total");
}

function cost_asset(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
        if(d.qty){
            frappe.model.set_value(cdt, cdn, 'pending_qty', d.qty);
        }

        d.total_cost = d.qty * d.cost_per_uom ;
        refresh_field("asset_table");
        // calculate grand total
        let grand_total = 0;
        let total = 0;
        frm.doc.asset_table.forEach(function(a) {
        grand_total += a.total_cost || 0;
        });
        frm.set_value("asset_total", grand_total);
        refresh_field("asset_total");
        frm.set_value("basic_total", frm.doc.component_total+frm.doc.asset_total+frm.doc.rm_total);
        refresh_field("basic_total");
}