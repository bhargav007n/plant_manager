# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InHouseProduction(Document):
	def on_submit(self):
		self.create_ssl_entry()
		

	@frappe.whitelist()
	def create_ssl_entry(self):
		# Verify if the default warehouse
		if not frappe.get_doc("Master Settings").default_rework_warehouse:
			frappe.throw("Please input the default Rework Warehouse in the Master Setting page ")
		if not frappe.get_doc("Master Settings").default_production_warehouse:
			frappe.throw("Please input the default Production Warehouse in the Master Setting page ")


		for a in self.get("production_log"):
			if (a.is_rework_operation == 0):
				prod_qty = a.acc_qty
				f_warehouse = frappe.get_doc("Master Settings").default_production_warehouse
				t_warehouse = frappe.get_doc("Master Settings").default_production_warehouse
			else:
				prod_qty = a.rew_qty
				f_warehouse = frappe.get_doc("Master Settings").default_rework_warehouse
				t_warehouse = frappe.get_doc("Master Settings").default_production_warehouse

			doc = frappe.get_doc("Production Work Order", a.batch_number)
			doc.append('ssl_entry', {
				'date': self.p_date,
				'process_id': a.operation_id,
				'qty': prod_qty,
				'transaction_type': 'In-House Production',
				'transaction_id': self.name,
				'operation_status': 'Completed',
				'from_warehouse': f_warehouse, 
				'to_warehouse': t_warehouse, 
				'duration': (a.dur_min + a.s_time)*60, 
				'dur_min' : a.dur_min + a.s_time,
				's_dur': a.s_time,
				'p_dur': a.dur_min
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			pwodoc =  frappe.get_doc("Production Work Order" , a.batch_number)
			pwodoc.load_calculations()	
			pwodoc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)	

			# Manual Labour
			
		for a in self.get("mll"):
			if(a.is_not_a_batch_work==0):
				if (a.is_rework == 0):
					prod_qty = a.produced_qty
					f_warehouse = frappe.get_doc("Master Settings").default_production_warehouse
					t_warehouse = frappe.get_doc("Master Settings").default_production_warehouse
				else:
					prod_qty = a.produced_qty
					f_warehouse = frappe.get_doc("Master Settings").default_rework_warehouse
					t_warehouse = frappe.get_doc("Master Settings").default_production_warehouse

				doc = frappe.get_doc("Production Work Order", a.batch)
				doc.append('ssl_entry', {
					'date': self.p_date,
					'process_id': a.operation_code,
					'qty': prod_qty,
					'transaction_type': 'In-House Production',
					'transaction_id': self.name,
					'operation_status': 'Completed',
					'from_warehouse': f_warehouse, 
					'to_warehouse': t_warehouse, 
					'duration': (a.dur_min + a.s_time)*60, 
					'dur_min' : a.dur_min + a.s_time,
					's_dur': a.s_time,
					'p_dur': a.dur_min
				})
				doc.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
				pwodoc =  frappe.get_doc("Production Work Order" , a.batch)
				pwodoc.load_calculations()	
				pwodoc.save(
					ignore_permissions=True, # ignore write permissions during insert
					)

	@frappe.whitelist()	
	def delete_ssl_entry(self):
		for a in self.get("production_log"):
			rows = frappe.get_all(
				"PWO SSL", 
				filters={"parent": a.batch_number},
				fields=[
					"transaction_id", "name",
				],
				)
			for row in rows:
				if row.transaction_id == self.name:
					frappe.delete_doc("PWO SSL", row.name, ignore_permissions=True)
					frappe.db.commit()
					pwodoc =  frappe.get_doc("Production Work Order" , a.batch_number)
					pwodoc.load_calculations()
