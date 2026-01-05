# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

from frappe.utils import get_datetime
from datetime import datetime
from frappe.model.document import Document
import frappe


class CuttingTool(Document):
	# def on_update(self):
	# 	self.counter_update()
	def after_insert(self):
		self.counter_add()
	def on_trash(self):
		self.counter_sub()

	def validate(self):
		self.update_status()

	@frappe.whitelist()
	def counter_add(self):
		doc_prefix = frappe.get_doc("Cutting Tool Prefix", self.prefix)
		
		# To add the counter
		if self.cutting_tool_id==doc_prefix.prefix_name:
			doc_prefix.counter=int(doc_prefix.counter+1)
			doc_prefix.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			
	@frappe.whitelist()
	def counter_sub(self):
		doc_prefix = frappe.get_doc("Cutting Tool Prefix", self.prefix)
		# to reduce the counter	
		previous_prefix= doc_prefix.prefix_name.removesuffix(str(int(doc_prefix.counter)))	
		previous_prefix=previous_prefix+str(int(doc_prefix.counter-1))
		if doc_prefix.counter != 1:
			if self.cutting_tool_id==previous_prefix:
				doc_prefix.counter=int(doc_prefix.counter-1)
				doc_prefix.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
				#frappe.throw(previous_prefix)
		

	@frappe.whitelist()
	def update_status(self):
		# Clear existing data
		self.issued_to = None
		self.to_machine = None
		self.for_component = None
		self.usage_info = None
		self.current_location = None
		self.issued_date = None
		#frappe.throw("hi, validating")

		# evaluating & assigning values
		if self.usage_log:
			# frappe.throw("hi, evaluating")
			a = frappe.utils.get_datetime("01-01-1200 00:00:00")
			
			for rowx in self.get("usage_log"):
				b = get_datetime(rowx.issued_date)
				if b > a:
					a = b
					self.issued_to = rowx.issued_to
					self.to_machine	= rowx.to_machine	 		
					self.for_component =rowx.for_component	
					self.usage_info = rowx.usage_info	
					self.current_location = rowx.issued_location
					self.issued_date = a
					
					# if it is returned 
					if rowx.returned_date:
						self.issued_date = rowx.returned_date
						self.current_location =	rowx.returned_location
			
