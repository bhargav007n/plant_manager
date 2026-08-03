# Copyright (c) 2026, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssemblyBOM(Document):

	def validate(self):
		self.bom_name =	str(self.component_code) + "-"+ str(self.revision)
		