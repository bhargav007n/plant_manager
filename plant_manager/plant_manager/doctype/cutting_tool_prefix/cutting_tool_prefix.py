# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CuttingToolPrefix(Document):
	def validate(self):
		if self.counter == None:
			self.counter = 1
		self.prefix_name= " "
		self.prefix_name= "".join(filter(None, [self.prefix,"-",str(self.counter).zfill(2)]))


		doc = frappe.get_doc("Cutting Tool Type", self.cutting_tool_type)
		if doc.abbreviation == self.prefix:
			frappe.throw("Update the prefix")

	
			


		
