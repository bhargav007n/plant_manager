# Copyright (c) 2026, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AccessoryPrefix(Document):
	def validate(self):
		if self.counter == None:
			self.counter = 1
		self.prefix_name= " "
		self.prefix_name= "".join(filter(None, [self.prefix,"-",str(self.counter)]))
		
		# Checking if prefix_name
		doc = frappe.get_doc("Accessory Type", self.accessory_type)
		if doc.abbreviation == self.prefix:
			frappe.throw("Update the prefix")
