# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProcessOperation(Document):

	def validate(self):
		self.title= " "
		self.title= ' - '.join(filter(None, [self.operation_name,self.comp_name ]))