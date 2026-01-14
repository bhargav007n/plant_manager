# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from plant_manager.plant_manager.doctype.production_work_order.production_work_order import ProductionWorkOrder


class MaterialOut(Document):
	def on_submit(self):
		self.create_ssl_entry()




	# def validate(self):
	# 	self.flags.ignore_links = True

	# def before_update_after_submit(self):
	# 	self.flags.ignore_links = True

	# def before_cancel(self):
	# 	self.delete_ssl_entry()
	@frappe.whitelist()		
	def update_pending_qty(self):
		for a in self.get("component_table"):
			a_qty = 0
			for b in self.get("mrn"):
				if a.comp_code == b.comp_code:
					a_qty = a_qty + b.received_qty
				
			a.pending_qty = a.qty - a_qty

		for i in self.get("rm_table"):
			i_qty = 0
			for b in self.get("mrn"):
				if i.component_code == b.comp_code:
					i_qty = i_qty + b.received_qty
				
			i.pending_qty = i.qty - i_qty

		for j in self.get("rm_table"):
			j_qty = 0
			for b in self.get("mrn"):
				if j.component_code == b.comp_code:
					j_qty = j_qty + b.received_qty
				
			j.pending_qty = j.qty - j_qty
		
		self.save(ignore_permissions=True)
		
		
	@frappe.whitelist()
	def create_ssl_entry(self):
		for a in self.get("component_table"):
			#print(a.batch)
			doc = frappe.get_doc("Production Work Order", a.batch)
			doc.append('ssl_entry', {
				'date': self.p_date,
				'process_id': a.for_process,
				'qty': a.qty,
				'transaction_type': 'Material Out',
				'transaction_id': self.name,
				'operation_status': a.opt_stat,
				'from_warehouse': a.f_wh,
				'to_warehouse': a.t_wh,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			pwodoc =  frappe.get_doc("Production Work Order" , a.batch)
			pwodoc.load_calculations()
			
	@frappe.whitelist()	
	def delete_ssl_entry(self):
		for a in self.get("component_table"):
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
					pwodoc.load_calculations()
