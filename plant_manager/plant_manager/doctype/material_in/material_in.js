// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material In", {
	refresh: function(frm) {
        frm.add_custom_button(__("Material Out - Process"),()=>{
            if(frm.doc.vdr) {  

                // MultiSelectDialog for individual child selection
                new frappe.ui.form.MultiSelectDialog({
                    doctype: "Material Out",
                    target: this.cur_frm,
                    setters: {
                        vdr: null,
                    
                    },
                    add_filters_group: 0,
                    date_field: "p_date",
                    allow_child_item_selection: 1,
                    child_fieldname: "component_table", // child table fieldname, whose records will be shown & can be filtered
                    child_columns: ["t_wh","comp_code","batch", "qty","pending_qty"], // child item columns to be displayed
                    get_query() {
                        return {
                            filters: { 
                                docstatus: ["=", 1],
                                vdr: ["=", frm.doc.vdr],
                                pending_qty:[">", 0],
                                t_wh: frm.doc.d_from_warehouse
                            }                       
                        };
                    },
                    action(selections, args) {
                        //console.log(selections);
                        //console.log(args.filtered_children); // list of selected item names
                        selections.forEach(function(mo_id){
                            if(mo_id){
                                frappe.call({
                                    method: 'frappe.client.get',
                                    args: {
                                        doctype: "Material Out",
                                        filters: {
                                            name: mo_id
                                        }
                                    },
                                    callback: function(r) {
                                        if (r.message) {                                                                         
                                            r.message.component_table.forEach(function(component_tables) {
                                                var mo_comp = args.filtered_children;
                                                if(mo_comp.length){
                                                    // frappe.msgprint("Item selected")
                                                    mo_comp.forEach(function(mo_comps){
                                                        if(mo_comps == component_tables.name) {
                                                            frappe.msgprint("Selected Components are loaded", component_tables.name)
                                                            insert_mi_table(frm, mo_id, component_tables, r);                                                        
                                                        }                                                            
                                                    })
                                                } else{
                                                    frappe.msgprint("All Components in Materal out are loaded")
                                                    insert_mi_table(frm, mo_id, component_tables, r);
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

        // Material IN from Asset

        frm.add_custom_button(__("Material Out - Asset"),()=>{
            if(frm.doc.vdr) {                
                // MultiSelectDialog for individual child selection
                new frappe.ui.form.MultiSelectDialog({
                    doctype: "Material Out",
                    target: this.cur_frm,
                    setters: {
                        vdr: null,
                    
                    },
                    add_filters_group: 0,
                    date_field: "p_date",
                    allow_child_item_selection: 1,
                    child_fieldname: "asset_table", // child table fieldname, whose records will be shown & can be filtered
                    child_columns: ["to_warehouse","component_code","qty","pending_qty"], // child item columns to be displayed
                    get_query() {
                        return {
                            filters: { 
                                docstatus: ["=", 1],
                                vdr: ["=", frm.doc.vdr],
                                pending_qty:[">", 0],
                                to_warehouse: frm.doc.d_from_warehouse
                            }                       
                        };
                    },
                    action(selections, args) {
                        //console.log(selections);
                        //console.log(args.filtered_children); // list of selected item names
                        selections.forEach(function(mo_id){
                            if(mo_id){
                                frappe.call({
                                    method: 'frappe.client.get',
                                    args: {
                                        doctype: "Material Out",
                                        filters: {
                                            name: mo_id
                                        }
                                    },
                                    callback: function(r) {
                                        if (r.message) {                                                                         
                                            r.message.asset_table.forEach(function(asset_tables) {
                                                var mo_comp = args.filtered_children;
                                                if(mo_comp.length){
                                                    frappe.msgprint("Item selected")
                                                    mo_comp.forEach(function(mo_comps){
                                                        if(mo_comps == asset_tables.name) {
                                                            insert_asset_table(frm, mo_id, asset_tables, r);     
                                                            frappe.msgprint("Selected Components are loaded", asset_tables.name)                                                   
                                                        }                                                            
                                                    })
                                                } else{
                                                    insert_asset_table(frm, mo_id, asset_tables, r);
                                                    frappe.msgprint("All Components in Materal out are loaded")                                    
                                                }
                                                
                                            });
                                            frm.refresh_field('asset');
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

        // Material IN from RM
        frm.add_custom_button(__("Material Out - RM"),()=>{
            if(frm.doc.vdr) {
                //frm.clear_table('component_table');
                //frappe.msgprint("Vendor Selected");  
                
                // MultiSelectDialog for individual child selection
                new frappe.ui.form.MultiSelectDialog({
                    doctype: "Material Out",
                    target: this.cur_frm,
                    setters: {
                        vdr: null,
                    
                    },
                    add_filters_group: 0,
                    date_field: "p_date",
                    allow_child_item_selection: 1,
                    child_fieldname: "rm_table", // child table fieldname, whose records will be shown & can be filtered
                    child_columns: ["to_warehouse","component_code","rm_batch", "qty","pending_qty"], // child item columns to be displayed
                    get_query() {
                        return {
                            filters: { 
                                docstatus: ["=", 1],
                                vdr: ["=", frm.doc.vdr],
                                pending_qty:[">", 0],
                                to_warehouse: frm.doc.d_from_warehouse
                            }                       
                        };
                    },
                    action(selections, args) {
                        //console.log(selections);
                        //console.log(args.filtered_children); // list of selected item names
                        selections.forEach(function(mo_id){
                            if(mo_id){
                                frappe.call({
                                    method: 'frappe.client.get',
                                    args: {
                                        doctype: "Material Out",
                                        filters: {
                                            name: mo_id
                                        }
                                    },
                                    callback: function(r) {
                                        if (r.message) {                                                                         
                                            r.message.rm_table.forEach(function(rm_tables) {
                                                var mo_comp = args.filtered_children;
                                                if(mo_comp.length){
                                                    // frappe.msgprint("Item selected")
                                                    mo_comp.forEach(function(mo_comps){
                                                        if(mo_comps == rm_tables.name) {
                                                            frappe.msgprint("Selected Components are loaded", rm_tables.name)
                                                            insert_rm_table(frm, mo_id, rm_tables, r);                                                        
                                                        }                                                            
                                                    })
                                                } else{
                                                    frappe.msgprint("All Components in Materal out are loaded")
                                                    insert_rm_table(frm, mo_id, rm_tables, r);
                                                }
                                                
                                            });
                                            frm.refresh_field('rm_table');
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
    
    },
});

function insert_mi_table(frm, mo_id, component_tables, r) {
    var child = frm.add_child('component_table');
    //console.log(pwo_id.comp_code);
    child.comp_code = component_tables.comp_code;
    //child.component_name = r.message.comp_name;
    child.batch = component_tables.batch;
    child.material_out = mo_id;
    child.qty = component_tables.pending_qty;
    child.completed_process = component_tables.for_process;
    child.mo_date = r.message.p_date;
    var dt = moment(frm.doc.p_date).diff(r.message.p_date,'minutes', true);
    child.dur_min = dt;

    // Convert minutes to total seconds
    let total_seconds = Math.floor(dt * 60);
    frappe.model.set_value(child.doctype, child.name, 'duration', total_seconds);
    frm.refresh_field('component_table');
}
function insert_rm_table(frm, mo_id, rm_tables, r) {
    var child = frm.add_child('rm_table');
    //console.log(pwo_id.comp_code);
    child.rm_component = rm_tables.component_code;
    //child.component_name = r.message.comp_name;
    child.rm_batch = rm_tables.rm_batch;
    child.material_out = mo_id;
    //child.qty = rm_tables.pending_qty;
    child.from_warehouse = rm_tables.to_warehouse;
    //child.completed_process = rm_tables.for_process;
    child.mo_date = r.message.p_date;
    var dt = moment(frm.doc.p_date).diff(r.message.p_date,'minutes', true);
    child.dur_min = dt;

    // Convert minutes to total seconds
    let total_seconds = Math.floor(dt * 60);
    frappe.model.set_value(child.doctype, child.name, 'duration', total_seconds);
    frm.refresh_field('rm_table');
}
function insert_asset_table(frm, mo_id, asset_tables, r) {
    var child = frm.add_child('asset');
    child.component_code = asset_tables.component_code;
    child.material_out = mo_id;
    child.qty = asset_tables.pending_qty;   
    child.from_warehouse = asset_tables.to_warehouse;
    child.material_out_date = r.message.p_date;
}
frappe.ui.form.on("Material In", { 
    // before_cancel: function(frm) {
    //     return frm.call({
    //        doc: frm.doc,
    //        method: "before_cancel",
    //        freeze: true,
    //        callback: (response) => {
    //            console.log(response.message);
    //            console.log("before_cancel");
    //        },
    //    });
    // },
    onload: function(frm) {
        frm.set_query('fg_component', 'rm_table', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {                
                'filters': [
                    ['Component', 'rm_component', 'in', d.rm_component],
                    ],
            };
        });
        frm.set_query('completed_process', 'rm_table', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {                
                'filters': [
                    ['Process Operation', 'comp_code', 'in', d.fg_component],
                    ],
            };
        });
        frm.set_query('operation_status', 'rm_table', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {                
                'filters': [
                    ['Operation Status', 'operation_status', 'in', 'Completed, Rework, Rejected'],
                    ],
            };
        });
        frm.set_query('rm_component', 'rm_table', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {                
                'filters': [
                    ['Component', 'is_rm', '=', 1],
                    ],
            };
        });
        frm.set_query('component_code', 'asset', function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {                
                'filters': [
                    ['Component', 'is_asset', '=', 1],
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
        frm.doc.asset.forEach(function(c) {
            c.from_warehouse = frm.doc.d_from_warehouse;
            c.to_warehouse = frm.doc.d_to_warehouse;
        });
        refresh_field('asset_table')
    },
    d_to_warehouse: function(frm) {
        frm.trigger("d_from_warehouse");
    },
    
})
frappe.ui.form.on("Material In RM", { 
    fg_component: async  function(frm, cdt, cdn) {
        await calculate_rm_consumed(frm, cdt, cdn);        
    },
    qty: async function(frm, cdt, cdn) {
        await calculate_rm_consumed(frm, cdt, cdn);
    },
});

// Calculation for RM Consumed
async function calculate_rm_consumed(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    let cut_data = await frappe.db.get_value('Component', d.fg_component, ['cl_mm','blade_mm'])
    frappe.model.set_value(cdt, cdn, 'rm_consumed', ((cut_data.message.cl_mm + cut_data.message.blade_mm)*d.qty/1000));
    refresh_field("rm_table");        
    }
