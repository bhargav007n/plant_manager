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
        }

        )
	},
});
