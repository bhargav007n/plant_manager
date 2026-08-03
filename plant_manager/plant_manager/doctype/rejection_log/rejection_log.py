# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RejectionLog(Document):
	def on_submit(self):
		self.create_ssl_entry()

	@frappe.whitelist()
	def create_ssl_entry(self):
		for a in self.get("rej_lst"):	
				# Verify if the default warehouse
			if not frappe.get_doc("Master Settings").default_rejected_warehouse:
				frappe.throw("Please input the default Rework Warehouse in the Master Setting page ")
			if not frappe.get_doc("Master Settings").default_production_warehouse:
				frappe.throw("Please input the default Production Warehouse in the Master Setting page ")		
				
			doc = frappe.get_doc("Production Work Order", a.batch)
			doc.append('ssl_entry', {
				'date': self.date,
				'process_id': a.opt_id,
				'qty': a.rej_qty,
				'transaction_type': 'Rejection Log',
				'transaction_id': self.name,
				'operation_status': a.rej_frm,
				'from_warehouse': a.f_wh,
				'to_warehouse': a.t_wh,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			pwodoc =  frappe.get_doc("Production Work Order" , a.batch)
			pwodoc.before_save_trigger()
				
	@frappe.whitelist()	
	def delete_ssl_entry(self):
		for a in self.get("rej_lst"):
			rows = frappe.get_all(
				"PWO SSL", 
				filters={"parent": a.batch},
				fields=[
					"transaction_id", "name",
				],
				)
			for row in rows:
				if row.transaction_id == self.name:
					frappe.delete_doc("PWO SSL", row.name, ignore_permissions=True)
					frappe.db.commit()
					pwodoc =  frappe.get_doc("Production Work Order" , a.batch)
					pwodoc.before_save_trigger()

