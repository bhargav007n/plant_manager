# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SalesInvoice(Document):
	def on_submit(self):
		self.create_disp_entry()

	@frappe.whitelist()
	def create_disp_entry(self):
		# for Production Work order update
		for a in self.get("sales_pwo"):
			doc = frappe.get_doc("Production Work Order", a.pwo_batch)
			doc.append('dispatch', {
				'dispatch_date': self.sales_invoice_date,
				'document_name': self.name,
				'document_qty': a.dispatch_qty,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			doc.calculate_disp()
		
		# for sales order update
		for b in self.get("sales_item_list"):
			doc = frappe.get_doc("Sales Order", b.sales_order)
			doc.append('dispatch_components', {
				'so_delivery_date': b.sa_delivery_date,
				'component_code':b.component_code,
				'sales_invoice': self.name,
				'sales_date':self.sales_invoice_date,
				'dispatch_qty': b.qty,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			sa_doc = frappe.get_doc("Sales Order", b.sales_order)
			sa_doc.update_pending_qty()
			
	@frappe.whitelist()	
	def delete_disp_entry(self):
		for a in self.get("sales_pwo"):
			rows = frappe.get_all(
				"PWO Dispatch", 
				filters={"parent": a.pwo_batch},
				fields=[
					"document_name", "name",
				],
				)
			for row in rows:
				if row.document_name == self.name:
					frappe.delete_doc("PWO Dispatch", row.name, ignore_permissions=True)
					frappe.db.commit()
					pwodoc =  frappe.get_doc("Production Work Order" , a.pwo_batch)
					pwodoc.calculate_disp()

		for b in self.get("sales_item_list"):
			rows = frappe.get_all(
				"Sales Order Dispatch", 
				filters={"parent": b.sales_order},
				fields=[
					"sales_invoice", "name",
				],
				)
			for row in rows:
				if row.sales_invoice == self.name:
					frappe.delete_doc("Sales Order Dispatch", row.name, ignore_permissions=True)
					frappe.db.commit()
					pwodoc =  frappe.get_doc("Sales Order" , b.sales_order)
					pwodoc.update_pending_qty()

	@frappe.whitelist()	
	def auto_load_pwo(self):
    # 1. Aggregate quantities by component code using a dictionary (much faster and avoids duplicate bugs)
		n_dup_comp = {} #Declared as dict which stores value in key
		for a in self.get("sales_item_list"):
			if a.component_code:
				n_dup_comp[a.component_code] = n_dup_comp.get(a.component_code, 0) + int(a.qty)

		# 2. Process each unique component
		self.sales_pwo=[]
		for comp_code, total_required_qty in n_dup_comp.items():
			if total_required_qty <= 0:
				continue

			# Fetch matching PWOs sorted by date (FIFO)
			pwo_records = frappe.get_all(
				"Production Work Order",
				filters=[
					["comp_code", "=", str(comp_code)],
					["pwo_status", "!=", "Closed"],
					["comp_qty", ">", 0],
					["docstatus", "=", 1]
				],
				fields=["name", "comp_code", "comp_qty", "pwo_date"],
				order_by="pwo_date asc"
			)

			asc_qty = total_required_qty

			# 3. FIFO Allocation Loop
			for pwo in pwo_records:
				if asc_qty <= 0:
					break  # Required quantity completely fulfilled

				available_qty = int(pwo.comp_qty)
				if available_qty <= 0:
					continue

				# Determine how much to deduct from this specific PWO batch
				allocated_qty = min(asc_qty, available_qty)

				# Append the allocation row
				self.append('sales_pwo', {
					'component_code': pwo.comp_code,
					'pwo_batch': pwo.name,
					'dispatch_qty': allocated_qty,
				})

				# Reduce the remaining quantity needed
				asc_qty -= allocated_qty
