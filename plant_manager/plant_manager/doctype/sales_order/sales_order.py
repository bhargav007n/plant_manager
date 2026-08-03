# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesOrder(Document):
	def on_submit(self):
		self.update_pending_qty()

	@frappe.whitelist()		
	def update_pending_qty(self):
		total_dispatch_qty = 0
		for a in self.get("component_list"):
			a_qty = 0
			for b in self.get("dispatch_components"):	
				if (a.component_code == b.component_code) :
					if a.delivery_date == b.so_delivery_date:
						a_qty = a_qty + b.dispatch_qty
				
			a.pending_qty = a.qty - a_qty
			total_dispatch_qty = total_dispatch_qty + a_qty

		self.total_dispatch_qty = total_dispatch_qty
		self.save(ignore_permissions=True)
		self.update_status()

	
	@frappe.whitelist()		
	def update_status(self):
		if self.status != "Short Closed":
			if self.total_order_qty==self.total_dispatch_qty:
				self.status="Closed"
			if self.total_order_qty>self.total_dispatch_qty:
				self.status="Open"
			self.save(ignore_permissions=True)


# validation checklist
# 	1. Do not allow multiple rows for same dates for a given component but multiple rows are allowed for same component but different dates
# 	2.