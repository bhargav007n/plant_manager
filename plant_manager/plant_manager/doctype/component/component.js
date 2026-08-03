// Copyright (c) 2025, Bhargav N and contributors
// For license information, please see license.txt

frappe.ui.form.on("Component", {
	onload: function(frm){
        frm.set_query( "rm_component", function(){
            return{
                'filters':{
                    "is_rm":1
                }
            }
        },
        )
        frm.set_query( 'dos', function(){
            return{
                'filters':{
                    "component_code":cur_frm.doc.component_code
                }
            }
        },
        )
        
        frm.set_query( 'assembly_bom', function(){
            return{
                'filters':{
                    "component_code":cur_frm.doc.component_code
                }
            }
        },
        )
	},
});
