# Copyright (c) 2024, Bhargav N and contributors
# For license information, please see license.txt
import json
import frappe
from frappe.model.document import Document

class ProductionWorkOrder(Document):
	
	def validate(self):
		pass
	
	@frappe.whitelist()
	def before_save_trigger(self):
		self.load_calculations()
		self.calculate_disp()
		


	@frappe.whitelist()
	def load_operation(self):
		if not self.pwo_qty:
			frappe.throw("Please input Production Work Order Qty")

		self.osd=[]
		data = frappe.get_all(
			"POS Table",
			filters={"parent": self.pos},
			fields=[
				"sequence_id",
				"operation_code",
				"operation_name",
			],
			order_by="sequence_id",
		)
		for d in range(len(data)):
			self.append('osd',{
								'sid':data[d].sequence_id,
								'opt_id':data[d].operation_code,
								'opt_name':data[d].operation_name,
								't_qty': 0,
								'p_qty':self.pwo_qty,
								'moved_to_vendor': 0,
								'o_rwk_qty': 0,
								'o_rej_qty':0,
								'o_comp_qty':0,
								'o_conv_qty':0,
								'waiting_qty':0,
								'auto_waiting_qty':0
							}
						)
		self.load_calculations()
			
	@frappe.whitelist()		
	def load_calculations(self):
		
		# loading operation status
		t_rej = 0.0
		t_conv = 0.0
		t_rew = 0.0
		data_map = {}
		qty = 0.0  # FG completed
		for a in self.get("osd"):
			qty1 = 0.0 # Total Qty
			qty2 = 0.0 # Pending qty
			qty3 = 0.0 # Vendor..
			qty4 = 0.0 # Rework..
			qty5 = 0.0 # Reject..
			qty6 = 0.0 # Conversion..
			qty7 = 0.0 # Completed..
			# loading operation status
			for b in self.get("ssl_entry"):		
				

				# Warehouse data collection start
				if a.opt_id == b.process_id:
					if b.from_warehouse:
						# key_out = (b.from_warehouse, b.process_id)
						key_out = b.from_warehouse
						data_map[key_out] = data_map.get(key_out, 0) - b.qty
					if b.to_warehouse:
						# key_in = (b.to_warehouse, b.process_id)
						key_in = b.to_warehouse
						data_map[key_in] = data_map.get(key_in, 0) + b.qty
				# Warehouse data collection end

				if a.opt_id == b.process_id:					
					# Material Out
					if b.transaction_type == "Material Out":
						#print("M.O selected")
						if b.operation_status == "Vendor" :
							qty3 = qty3 + b.qty #qty3 is vendor
							#qty2 = qty2 - b.qty #qty2 is pending qty
						if b.operation_status == "Rework":
							qty3 = qty3 + b.qty #qty3 is vendor
							qty4 = qty4 - b.qty #qty4 is rework

					# Material In		
					if b.transaction_type == "Material In":
						if b.operation_status == "Completed":
							qty7 = qty7 + b.qty #qty7 is completed
							qty3 = qty3 - b.qty #qty3 is vendor

						if b.operation_status == "Rejected":
							qty5 = qty5 + b.qty #qty5 is Rejected
							qty3 = qty3 - b.qty #qty3 is vendor

						if b.operation_status == "Returned Without Operation":
							qty4 = qty4 + b.qty #qty4 is rework
							qty3 = qty3 - b.qty #qty3 is vendor


					# Rework Log
					if b.transaction_type == "Rework Log":
						if b.operation_status == "Rework":
							qty4 = qty4 + b.qty #qty4 is Rework
							qty7 = qty7 - b.qty #qty7 is completed
						
						if b.operation_status == "Rejection":
							qty4 = qty4 + b.qty #qty4 is Rework
							qty5 = qty5 - b.qty #qty5 is Rejection

					# Rejection Log
					if b.transaction_type == "Rejection Log":
						if b.operation_status == "Completed":
							qty5 = qty5 + b.qty #qty5 is Rejected
							qty7 = qty7 - b.qty #qty7 is completed

						if b.operation_status == "Rework":
							qty5 = qty5 + b.qty #qty5 is Rejected
							qty4 = qty4 - b.qty #qty4 is Rework	


					# Conversion Log
					if b.transaction_type == "Conversion Log":
						if b.operation_status == "Pending":
							qty6 = qty6 + b.qty #qty6 is conversion qty
							#qty2 = qty2 - b.qty #qty2 is pending qty

						if b.operation_status == "Rework":
							qty6 = qty6 + b.qty #qty6 is conversion qty
							qty4 = qty4 - b.qty #qty4 is Rework
						
						if b.operation_status == "Vendor":
							qty6 = qty6 + b.qty #qty6 is conversion qty
							qty3 = qty3 - b.qty #qty3 is vendor
						
						if b.operation_status == "Rejection":
							qty6 = qty6 + b.qty #qty6 is conversion qty
							qty5 = qty5 - b.qty #qty5 is Rejected qty
					
					#In-House Production
					if b.transaction_type == "In-House Production":
						if b.operation_status == "Completed":
							qty7 = qty7 + b.qty # qty7 is Completed qty
							#qty2 = qty2 - b.qty # qty2 is Pending qty
						
						if b.operation_status == "Rework":
							qty7 = qty7 + b.qty # qty6 is Completed qty
							qty4 = qty4 - b.qty # qty4 is Rework qty	

					#FG completed
					if b.operation_type == "FG":
						if b.operation_status == "Completed":
							qty = qty + b.qty
							

			a.moved_to_vendor = qty3
			a.o_rwk_qty = qty4
			a.o_rej_qty = qty5
			a.o_conv_qty = qty6
			a.o_comp_qty = qty7

			qty1 = self.pwo_qty - t_rej - t_conv #(previous operation rej cov status of the part)			
			qty2 = qty1 - qty7 - qty6 - qty5 - qty4 - qty3   #(7-completed, 6-coversion, 5-rejection, 4-Rework, 3-vendor )

			a.t_qty = qty1
			a.p_qty = qty2

			t_rew = t_rew + qty4
			t_rej = t_rej + qty5
			t_conv = t_conv + qty6
			self.comp_qty = qty

		self.rej_qty = t_rej
		self.conv_qty = t_conv 
		self.rwk_qty = t_rew

		# loading status of work order (should always be before self.save() )
		c = self.comp_qty + self.conv_qty + self.rej_qty
		if self.pwo_qty > c:
			self.pwo_status = "Open"
		if self.pwo_qty == c:
			self.pwo_status = "Completed"	
		if self.pwo_qty == self.disp_qty + self.conv_qty + self.rej_qty:
			self.pwo_status = "Closed"
		
		
		# Warehouse stock updation
		self.wss=[]
		# for (wh, proc), total_qty in data_map.items():
		for wh, total_qty in data_map.items():
			master_settings = frappe.get_doc("Master Settings")
			if wh==master_settings.default_production_warehouse:
				total_qty = total_qty+self.pwo_qty
				frappe.msgprint("Default Warehouse stock updated")
			# Only add rows where there is a balance	
			if total_qty != 0:
				self.append("wss", {
					"warehouse": wh,
					# "process": proc,
					"qty": total_qty
				})

		
		self.save(ignore_permissions=True)		


	@frappe.whitelist()
	def calculate_disp(self):
		ttl_disp = 0
		for disp in self.get("dispatch"):
			ttl_disp = ttl_disp + disp.inv_qty
		if ttl_disp>self.comp_qty:
			frappe.throw("You cannot dispatch more than completed qty")
		self.disp_qty = ttl_disp
		if self.pwo_qty == self.disp_qty + self.conv_qty + self.rej_qty:
			self.pwo_status = "Closed"

		self.save(ignore_permissions=True)	