# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssemblyLog(Document):
	def validate(self):
		# frappe.throw("I am validating")

	# 1. Validating the assembly item qty are in correct numbers.
		if self.assembly_bom:              # if assembly bom is present
			# 1.a. Total qty of indvidual component
			comp ={}
			for a in self.get("acp"):
				comp[a.comp_id] = comp.get(a.comp_id, 0.0) + a.req_qty

			# 1.b. Checking the required Qty
			doc = frappe.get_doc("Assembly BOM", self.assembly_bom)
			for b in doc.bom:
				if comp[b.bom_component] != (self.asb_qty*b.bom_qty):
					frappe.throw(f"For {b.bom_component} required qty is {self.asb_qty*b.bom_qty} but used {comp[b.bom_component]}")

	

	def on_submit(self):
		self.create_disp_entry()
		self.create_pwo()
	
	@frappe.whitelist()
	def load_bom(self):
		self.acp=[]
		if not self.asb_qty:
			frappe.throw("Please in put the Qty & select Assembly BOM")	
		data = frappe.get_all(
			"Assembly BOM Table",
			filters={"parent": self.assembly_bom},
			fields=[
				"bom_component",
				"bom_qty",
			],
		)
		for d in range(len(data)):
			self.append('acp',{
								'comp_id':data[d].bom_component,
								'req_qty':self.asb_qty*data[d].bom_qty,
							}
						)

	@frappe.whitelist()
	def create_disp_entry(self):
		for a in self.get("acp"):					
			doc = frappe.get_doc("Production Work Order", a.batch)
			if (doc.comp_qty-doc.disp_qty)<a.req_qty:
				frappe.throw(f"Component {a.comp_id} doest not have enough qty ({doc.comp_qty-doc.disp_qty}) in {a.batch} to assemble. Required qty is {a.req_qty}")
			doc.append('dispatch', {
				'dispatch_date': self.assembly_date,
				'document_name': self.name,
				'document_qty': a.req_qty,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			doc.before_save_trigger()

	@frappe.whitelist()
	def create_pwo(self):
		asm_doc = frappe.new_doc('Production Work Order')
		asm_doc.pos = frappe.get_doc('Component',self.comp_id).dos
		asm_doc.pwo_qty = self.asb_qty
		asm_doc.pwo_date = self.assembly_date
		asm_doc.created_against = self.name
		asm_doc.insert(ignore_permissions=True)
		asm_doc.load_operation()
		frappe.flags.ignore_permissions = True
		asm_doc.save(ignore_permissions=True,)
		asm_doc.submit()
		frappe.flags.ignore_permissions = False	
		
		# updating Production work order name
		self.batch = asm_doc.get_title()
		self.save(ignore_permissions=True)

	@frappe.whitelist()	
	def delete_disp_entry(self):
		for a in self.get("acp"):
			rows = frappe.get_all(
				"PWO Dispatch", 
				filters={"parent": a.batch},
				fields=[
					"document_name", "name",
				],
				)
			for row in rows:
				if row.document_name == self.name:
					frappe.delete_doc("PWO Dispatch", row.name, ignore_permissions=True)
					frappe.db.commit()
					pwodoc =  frappe.get_doc("Production Work Order" , a.batch)
					pwodoc.before_save_trigger()

		pwo_ssl = frappe.get_all(
			"PWO SSL", 
			filters={"parent": self.batch},
			# fields=[
			# 	"transaction_id", "name",
			# ],
			)
		if len(pwo_ssl)>0:
			frappe.throw(f"Please check the Production Work order, already Transaction has done against {self.batch}")
		asm_pwodoc =  frappe.get_doc("Production Work Order" , self.batch)
		asm_pwodoc.flags.ignore_permissions = True
		asm_pwodoc.flags.ignore_links = True
		asm_pwodoc.ignore_links_on_delete = True
		asm_pwodoc.cancel()
		frappe.delete_doc("Production Work Order", self.batch)
		frappe.msgprint(f"deleting PWO : {self.batch}")

	@frappe.whitelist()
	def external_validation(self):	
		# 1. Validating 
		for a in self.get("acp"):					
			doc = frappe.get_doc("Production Work Order", a.batch)
			if (doc.comp_qty-doc.disp_qty)<a.req_qty:
				frappe.throw(f"Component {a.comp_id} doest not have enough qty ({doc.comp_qty-doc.disp_qty}) in {a.batch} to assemble. Required qty is {a.req_qty}")