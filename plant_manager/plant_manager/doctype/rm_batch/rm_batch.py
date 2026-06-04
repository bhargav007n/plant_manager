# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RMBatch(Document):
	def validate(self):

		# updating pending qty
		self.update_pending_qty()
		


	@frappe.whitelist()
	def update_pending_qty(self):
		if(self.rm_consumtion):
			consumed_qty = 0
			for a in self.get("rm_consumtion"):
				consumed_qty=consumed_qty+a.rm_consumed
				pass
			self.p_qty = self.rm_qty-consumed_qty
		else:
			self.p_qty = self.rm_qty
		pass