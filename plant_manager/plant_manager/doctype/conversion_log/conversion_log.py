# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConversionLog(Document):
	def on_submit(self):
		self.create_ssl_entry()
		self.create_pwo()

	@frappe.whitelist()
	def before_cancel(self):
		self.delete_ssl_entry()
		self.delete_pwo()	

	@frappe.whitelist()
	def create_ssl_entry(self):
		doc = frappe.get_doc("Production Work Order",self.from_batch)
		doc.append('ssl_entry', {
			'date': self.conversion_date,
			'process_id': self.from_operation_id,
			'qty': self.conversion_qty,
			'transaction_type': 'Conversion Log',
			'transaction_id': self.name,
			'operation_status': self.fos,
			'from_warehouse': self.from_warehouse,
			'to_warehouse': None,
			})
		doc.save(
			ignore_permissions=True, # ignore write permissions during insert
			)
		doc.load_calculations()
		doc.save(
			ignore_permissions=True, # ignore write permissions during insert
			)

	@frappe.whitelist()
	def create_pwo(self):
		doc = frappe.new_doc('Production Work Order')
		doc.pos = frappe.get_doc('Component',self.to_component_id).dos
		doc.pwo_qty = self.conversion_qty
		doc.pwo_date = self.conversion_date
		doc.created_against = self.name
		doc.insert(ignore_permissions=True)
		doc.load_operation()
		frappe.flags.ignore_permissions = True
		doc.save(ignore_permissions=True,)
		doc.submit()
		frappe.flags.ignore_permissions = False	

		# updating Production work order name
		self.to_batch = doc.get_title()
		self.save(ignore_permissions=True)

	@frappe.whitelist()
	def delete_ssl_entry(self):
		rows = frappe.get_all(
			"PWO SSL", 
			filters={"parent": self.from_batch},
			fields=[
				"transaction_id", "name",
			],
			)
		for row in rows:
			if row.transaction_id == self.name:
				frappe.delete_doc("PWO SSL", row.name, ignore_permissions=True)
				frappe.db.commit()
				pwodoc =  frappe.get_doc("Production Work Order" ,self.from_batch)
				pwodoc.load_calculations()

	@frappe.whitelist()
	def delete_pwo(self):
		rows = frappe.get_all(
				"PWO SSL", 
				filters={"parent": self.to_batch},
				fields=[
					"transaction_id", "name",
				],
				)
		if self.to_batch:
			if len(rows)>0:
				frappe.throw(f"Please check the Production Work order, already Transaction has done against {self.to_batch}")
			pwodoc =  frappe.get_doc("Production Work Order" , self.to_batch)
			pwodoc.flags.ignore_permissions = True
			pwodoc.flags.ignore_links = True
			pwodoc.ignore_links_on_delete = True
			pwodoc.cancel()
			frappe.delete_doc("Production Work Order", self.to_batch)
			frappe.msgprint("deleting PWO")