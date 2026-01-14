# Copyright (c) 2026, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ToolUsageLog(Document):
	def on_submit(self):
		self.qty_on_submit()
	
	def on_cancel(self):
		self.qty_on_cancel()




	@frappe.whitelist()
	def qty_on_submit(self):
		if self.transaction_type =="Purchase":
			if self.tool_type !="Single Use Tool":
				frappe.throw("Transaction Type is only for Single Use Tools")
		if self.transaction_type =="Purchase":
			if self.tool_type !="Single Use Tool":
				frappe.throw("Transaction Type is only for Single Use Tools")

		if self.tool_type == "Machine Tool Accessory":
			if self.transaction_type == "Issue" :	
				doc_cutting_tool = frappe.get_doc("Machine Tool Accessory", self.tool_name)
				doc_cutting_tool.append('usage_log',{
					'issued_date':self.transaction_date,
					'issued_to':self.issued_to,
					'to_machine':self.to_machine,
					'for_component':self.for_component,
					'issued_location':self.to_location,
					'usage_info':self.usage_info,
					'transaction_id':self.name,
					'status':self.status,	
				})
				doc_cutting_tool.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
				doc_cutting_tool.update_status()
				doc_cutting_tool.save()


			if self.transaction_type == "Used Return" :
				list_cutting_tool_log = frappe.get_all(
					"Cutting Tool Usage Log", 
					filters={
						"parent": self.tool_name,
						"transaction_id":self.returned_against
						},
				)
				table = frappe.get_doc("Cutting Tool Usage Log", list_cutting_tool_log[0].name)
				table.returned_date=self.transaction_date
				table.returned_location=self.to_location
				table.returned_info=self.usage_info
				table.return_transaction_id=self.name
				table.status=self.status	
				table.save(
					ignore_permissions=True, # ignore write permissions during insert
				)
				doc_cutting_tool = frappe.get_doc("Machine Tool Accessory", self.tool_name)
				doc_cutting_tool.update_status()
				doc_cutting_tool.save()
				issued_doc =frappe.get_doc("Tool Usage Log", self.returned_against)
				issued_doc.returned_transaction=self.name
				issued_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
				)


		if self.tool_type == "Cutting Tool":
			if self.transaction_type == "Issue" :	
				doc_cutting_tool = frappe.get_doc("Cutting Tool", self.tool_name)
				doc_cutting_tool.append('usage_log',{
					'issued_date':self.transaction_date,
					'issued_to':self.issued_to,
					'to_machine':self.to_machine,
					'for_component':self.for_component,
					'issued_location':self.to_location,
					'usage_info':self.usage_info,
					'transaction_id':self.name,	
					'status':self.status,	
				})
				doc_cutting_tool.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
				doc_cutting_tool.update_status()
				doc_cutting_tool.save()

			if self.transaction_type == "Used Return" :
				list_cutting_tool_log = frappe.get_all(
					"Cutting Tool Usage Log", 
					filters={
						"parent": self.tool_name,
						"transaction_id":self.returned_against
						},
				)
				table = frappe.get_doc("Cutting Tool Usage Log", list_cutting_tool_log[0].name)
				table.returned_date=self.transaction_date
				table.returned_location=self.to_location
				table.returned_info=self.usage_info
				table.return_transaction_id=self.name
				table.status=self.status
				table.save(
					ignore_permissions=True, # ignore write permissions during insert
				)
				doc_cutting_tool = frappe.get_doc("Cutting Tool", self.tool_name)
				doc_cutting_tool.update_status()
				doc_cutting_tool.save()

				issued_doc =frappe.get_doc("Tool Usage Log", self.returned_against)
				issued_doc.returned_transaction=self.name
				issued_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
				)

						

		if self.tool_type == "Single Use Tool":
			#frappe.throw("hi, evaluating")
			if self.transaction_type == "Purchase":
				doc_tool = frappe.get_doc("Single Use Tool", self.tool_name)
				self.qty_after_transaction = doc_tool.stock_qty + self.qty
				doc_tool.stock_qty = doc_tool.stock_qty + self.qty
				doc_tool.total_qty = doc_tool.total_qty + self.qty
				doc_tool.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
			
			if self.transaction_type == "Issue":
				doc_tool = frappe.get_doc("Single Use Tool", self.tool_name)
				self.qty_after_transaction = doc_tool.stock_qty - self.qty
				doc_tool.stock_qty = doc_tool.stock_qty - self.qty
				doc_tool.save(
					ignore_permissions=True, # ignore write permissions during insert
					)

			if self.transaction_type == "Used Return":
				doc_tool = frappe.get_doc("Single Use Tool", self.tool_name)
				doc_tool.returned_qty = doc_tool.returned_qty + self.qty
				doc_tool.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
				
	@frappe.whitelist()
	def qty_on_cancel(self):
		if self.tool_type == "Machine Tool Accessory":
			if self.transaction_type == "Issue" :
				list_cutting_tool_log = frappe.get_all(
					"Cutting Tool Usage Log",
					filters={
						"parent": self.tool_name,
						"transaction_id":self.name			
						},
				)
				table = frappe.get_doc("Cutting Tool Usage Log", list_cutting_tool_log[0].name)
				if table.return_transaction_id != None:
					frappe.throw("First Delete the returned Tool Usage Log")
				frappe.delete_doc("Cutting Tool Usage Log", list_cutting_tool_log[0].name,ignore_permissions=True)
				frappe.db.commit()
				doc_cutting_tool = frappe.get_doc("Machine Tool Accessory", self.tool_name)
				doc_cutting_tool.update_status()
				doc_cutting_tool.save()



			if self.transaction_type == "Used Return" :
				list_cutting_tool_log = frappe.get_all(
					"Cutting Tool Usage Log", 
					filters={
						"parent": self.tool_name,
						"transaction_id":self.returned_against
						},
				)
				old_log=frappe.get_doc("Tool Usage Log", self.returned_against)
				table = frappe.get_doc("Cutting Tool Usage Log", list_cutting_tool_log[0].name)
				table.returned_date=None
				table.returned_location=None
				table.returned_info=None
				table.return_transaction_id=None
				table.status=old_log.status
				table.save(
					ignore_permissions=True, # ignore write permissions during insert
				)
				doc_cutting_tool = frappe.get_doc("Machine Tool Accessory", self.tool_name)
				doc_cutting_tool.update_status()
				doc_cutting_tool.save()
				issued_doc =frappe.get_doc("Tool Usage Log", self.returned_against)
				issued_doc.returned_transaction=None
				issued_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
				)



		if self.tool_type == "Cutting Tool":
			if self.transaction_type == "Issue" :
				list_cutting_tool_log = frappe.get_all(
					"Cutting Tool Usage Log", 
					filters={
						"parent": self.tool_name,
						"transaction_id":self.name			
						},
				)
				table = frappe.get_doc("Cutting Tool Usage Log", list_cutting_tool_log[0].name)
				if table.return_transaction_id != None:
					frappe.throw("First Delete the returned Tool Usage Log")
				frappe.delete_doc("Cutting Tool Usage Log", list_cutting_tool_log[0].name,ignore_permissions=True)
				frappe.db.commit()
				doc_cutting_tool = frappe.get_doc("Cutting Tool", self.tool_name)
				doc_cutting_tool.update_status()
				doc_cutting_tool.save()



			if self.transaction_type == "Used Return" :
				list_cutting_tool_log = frappe.get_all(
					"Cutting Tool Usage Log", 
					filters={
						"parent": self.tool_name,
						"transaction_id":self.returned_against
						},
				)
				old_log=frappe.get_doc("Tool Usage Log", self.returned_against)
				table = frappe.get_doc("Cutting Tool Usage Log", list_cutting_tool_log[0].name)
				table.returned_date=None
				table.returned_location=None
				table.returned_info=None
				table.return_transaction_id=None
				table.status=old_log.status
				table.save(
					ignore_permissions=True, # ignore write permissions during insert
				)
				doc_cutting_tool = frappe.get_doc("Cutting Tool", self.tool_name)
				doc_cutting_tool.update_status()
				doc_cutting_tool.save()
				issued_doc.returned_transaction=None
				issued_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
				)



		if self.tool_type == "Single Use Tool":
			#frappe.throw("hi, evaluating")
			if self.transaction_type == "Purchase":
				doc_tool = frappe.get_doc("Single Use Tool", self.tool_name)
				#self.qty_after_transaction = doc_tool.stock_qty + self.qty
				doc_tool.stock_qty = doc_tool.stock_qty - self.qty
				doc_tool.total_qty = doc_tool.total_qty - self.qty
				doc_tool.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
			
			if self.transaction_type == "Issue":
				doc_tool = frappe.get_doc("Single Use Tool", self.tool_name)
				#self.qty_after_transaction = doc_tool.stock_qty - self.qty
				doc_tool.stock_qty = doc_tool.stock_qty + self.qty
				doc_tool.save(
					ignore_permissions=True, # ignore write permissions during insert
					)

			if self.transaction_type == "Used Return":
				doc_tool = frappe.get_doc("Single Use Tool", self.tool_name)
				doc_tool.returned_qty = doc_tool.returned_qty - self.qty
				doc_tool.save(
					ignore_permissions=True, # ignore write permissions during insert
					)

