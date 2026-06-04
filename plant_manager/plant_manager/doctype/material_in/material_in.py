# Copyright (c) 2025, Bhargav N and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MaterialIn(Document):
	def validate(self):
		frappe.msgprint(f"Before Save: component_table rows = {len(self.component_table)}")
		frappe.msgprint("Validation pending")

	def before_save(self):
		frappe.msgprint(f"Before Save (again): component_table rows = {len(self.component_table)}")

	def on_submit(self):
		self.create_mo_receipt()
		self.create_ssl_entry()
		self.create_pwo()

	@frappe.whitelist()
	def before_cancel(self):
		# Component table & RM table
		self.delete_ssl_mrn_entry()
		# Asset
		self.delete_mo_asset()
		pass

		


	@frappe.whitelist()
	def create_mo_receipt(self):
		for a in self.get("component_table"):
			doc = frappe.get_doc("Material Out", a.material_out)
			doc.append('mrn', {
				'r_date_time': self.p_date,
				'received_qty': a.qty,
				'material_in': self.name,
				'comp_code': a.comp_code,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			modoc =  frappe.get_doc("Material Out" , a.material_out)
			modoc.update_pending_qty()

		for b in self.get("asset"):
			doc = frappe.get_doc("Material Out", b.material_out)
			doc.append('mrn', {
				'r_date_time': self.p_date,
				'received_qty': b.qty,
				'material_in': self.name,
				'comp_code': b.component_code,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			frappe.msgprint("updated asset")
			modoc =  frappe.get_doc("Material Out" , b.material_out)
			modoc.update_pending_qty()
		
		for c in self.get("rm_table"):
			doc = frappe.get_doc("Material Out", c.material_out)
			doc.append('mrn', {
				'r_date_time': self.p_date,
				'received_qty': c.rm_consumed,
				'material_in': self.name,
				'comp_code': c.rm_component,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			modoc =  frappe.get_doc("Material Out" , c.material_out)
			modoc.update_pending_qty()


	@frappe.whitelist()
	def create_ssl_entry(self):
		for a in self.get("component_table"):
			print(a.batch)
			doc = frappe.get_doc("Production Work Order", a.batch)
			doc.append('ssl_entry', {
				'date': self.p_date,
				'process_id': a.completed_process,
				'qty': a.qty,
				'transaction_type': 'Material In',
				'transaction_id': self.name,
				'operation_status': a.operation_status,
				'from_warehouse': a.f_wh,
				'to_warehouse': a.t_wh,
				'duration': a.duration,
				'dur_min' : a.dur_min,
			})
			doc.save(
				ignore_permissions=True, # ignore write permissions during insert
				)
			pwodoc =  frappe.get_doc("Production Work Order" , a.batch)
			pwodoc.load_calculations()
			
	@frappe.whitelist()	
	def delete_ssl_mrn_entry(self):
		for a in self.get("component_table"):
			rows = frappe.get_all(
				"PWO SSL", 
				filters={"parent": a.batch},
				fields=[
					"transaction_id", "name",
				],
				)
			for row in rows:
				if row.transaction_id == self.name:
					frappe.delete_doc("PWO SSL", row.name, ignore_permissions=True)
					frappe.db.commit()
					pwodoc =  frappe.get_doc("Production Work Order" , a.batch)
					pwodoc.load_calculations()

			# To delete material receipt notes in Material Out Doc
			mrn_rows = frappe.get_all(
				"Material Out Receipt Note", 
				filters={"parent": a.material_out},
				fields=[
					"material_in", "name",
				],
				)
			for mrn_row in mrn_rows:
				if mrn_row.material_in == self.name:
					frappe.delete_doc("Material Out Receipt Note", mrn_row.name, ignore_permissions=True)
					frappe.db.commit()
					modoc =  frappe.get_doc("Material Out" , a.material_out)
					modoc.update_pending_qty()
		
		# RM Table
		for b in self.get("rm_table"):
			rows = frappe.get_all(
				"PWO SSL", 
				filters={"parent": b.pwo_batch},
				fields=[
					"transaction_id", "name",
				],
				)
			if len(rows)>2:
				frappe.throw(f"Please check the Production Work order, already Transaction has done against {b.pwo_batch}")
			pwodoc =  frappe.get_doc("Production Work Order" , b.pwo_batch)
			pwodoc.flags.ignore_permissions = True
			pwodoc.flags.ignore_links = True
			pwodoc.ignore_links_on_delete = True
			pwodoc.cancel()
			frappe.delete_doc("Production Work Order", b.pwo_batch)
			frappe.msgprint("deleting PWO")

			# To delete material receipt notes in Material Out Doc
			mrn_rows = frappe.get_all(
				"Material Out Receipt Note", 
				filters={"parent": b.material_out},
				fields=[
					"material_in", "name",
				],
				)
			for mrn_row in mrn_rows:
				if mrn_row.material_in == self.name:
					frappe.delete_doc("Material Out Receipt Note", mrn_row.name, ignore_permissions=True)
					frappe.db.commit()
					modoc =  frappe.get_doc("Material Out" , b.material_out)
					modoc.update_pending_qty()
					frappe.msgprint("deleting MRN")

			# To delete RM Consumtion Table in RM Batch
			rmc_rows = frappe.get_all(
				"RM Batch Table", 
				filters={"parent": b.rm_batch},
				fields=[
					"material_in", "name",
				],
				)
			for rmc_row in rmc_rows:
				if rmc_row.material_in == self.name:
					frappe.delete_doc("RM Batch Table", rmc_row.name, ignore_permissions=True)
					frappe.db.commit()
					rm_doc =  frappe.get_doc("RM Batch" , b.rm_batch)
					rm_doc.update_pending_qty()
					rm_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
					frappe.msgprint("deleting MRN & Updating")
	
	@frappe.whitelist()	
	def delete_mo_asset(self):
		for a in self.get("asset"):

			# To delete material receipt notes in Material Out Doc
			mrn_rows = frappe.get_all(
				"Material Out Receipt Note", 
				filters={"parent": a.material_out},
				fields=[
					"material_in", "name",
				],
				)
			for mrn_row in mrn_rows:
				if mrn_row.material_in == self.name:
					frappe.delete_doc("Material Out Receipt Note", mrn_row.name, ignore_permissions=True)
					frappe.db.commit()
					modoc =  frappe.get_doc("Material Out" , a.material_out)
					modoc.update_pending_qty()
					
		
	@frappe.whitelist()	
	def create_pwo(self):
		for a in self.get("rm_table"):
			if a.is_end_piece != 1:
				doc = frappe.new_doc('Production Work Order')
				doc.pos = frappe.get_doc('Component',a.fg_component).dos
				doc.pwo_qty = a.qty
				doc.pwo_date = self.p_date
				doc.created_against = self.name
				doc.insert(ignore_permissions=True)
				doc.load_operation()
				frappe.flags.ignore_permissions = True
				doc.save(ignore_permissions=True,)
				doc.submit()
				frappe.flags.ignore_permissions = False	
				
				# frappe.msgprint("pwo")

				# updating Production work order name
				a.pwo_batch = doc.get_title()
				self.save(ignore_permissions=True)
				master_settings =frappe.get_doc("Master Settings")
				u_doc = frappe.get_doc("Production Work Order", a.pwo_batch)
				# Material Out SSL entry
				u_doc.append('ssl_entry', {
					'date':a.mo_date,
					'process_id': a.completed_process,
					'qty': a.qty,
					'transaction_type': 'Material OUT',
					'transaction_id': a.material_out,
					'operation_status': 'Vendor',
					'from_warehouse': master_settings.default_production_warehouse,
					'to_warehouse': a.from_warehouse,
				})
				u_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
					)	

				# Material In SSL entry
				u_doc.append('ssl_entry', {
					'date': self.p_date,
					'process_id': a.completed_process,
					'qty': a.qty,
					'transaction_type': 'Material IN',
					'transaction_id': self.name,
					'operation_status': 'Completed',
					'from_warehouse': a.from_warehouse,
					'to_warehouse': a.to_warehouse,
				})
				u_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
				pwodoc =  frappe.get_doc("Production Work Order" , a.pwo_batch)
				pwodoc.before_save_trigger()
				# frappe.msgprint("pwo updating")

				#Updating RM Btch
				rm_doc = frappe.get_doc("RM Batch", a.rm_batch)
				rm_doc.append('rm_consumtion', {
					'component_id': a.fg_component,
					'batch':a.pwo_batch,
					'rm_consumed':a.rm_consumed,
					'cut_qty': a.qty,
					'material_in': self.name,
				})
				rm_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
					)
				rm_doc.update_pending_qty()
				rm_doc.save(
					ignore_permissions=True, # ignore write permissions during insert
					)


