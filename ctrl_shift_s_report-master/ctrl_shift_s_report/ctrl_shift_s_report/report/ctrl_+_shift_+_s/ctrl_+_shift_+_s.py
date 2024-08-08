# Copyright (c) 2024, Software At Work (India) Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from typing import Dict
from erpnext.stock.utils import get_stock_balance
from frappe.utils import getdate


def execute(filters=None):
    return CtrlShiftS(filters).run()


class CtrlShiftS():
    def __init__(self, filters):
        self.filters = frappe._dict(filters or {})
        self.query = ""
        self.query_filters = {}
        self.summery = []
        self.data = []
        self.columns = []

    def run(self):
        self.get_columns()
        self.get_data()
        self.get_summery()

        return self.columns, self.data, None , None, self.summery

    def get_columns(self):
        columns = [
            {
                "label": _("Voucher No"),
                "fieldname": "voucher_no",
                "fieldtype": "Dynamic Link",
                "options": "voucher_type",
                "width": 150,
            },
            {
                "label": _("Voucher Date"),
                "fieldname": "voucher_date",
                "fieldtype": "Date",
                "width": 150,
            },
            {
                "label": _("Party Type"),
                "fieldname": "party_type",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Party"),
                "fieldname": "party",
                "fieldtype": "Dynamic Link",
                "options": "party_type",
                "width": 150,
            },
            {
                "label": _("Party Name"),
                "fieldname": "party_name",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Qty"),
                "fieldname": "qty",
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "label": _("Vendor Bill"),
                "fieldname": "vendor_bill",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Vendor Bill Date"),
                "fieldname": "vendor_bill_date",
                "fieldtype": "Date",
                "width": 150,
            },
            {
                "label": _("Voucher Type"),
                "fieldname": "voucher_type",
                "fieldtype": "Data",
                "width": 150,
            },
        ]
        self.columns = columns

    def add_date_filter(self):
        self.query += f" WHERE voucher_date between '{self.filters.from_date}' and '{self.filters.to_date}'"

    def add_company_filter(self):
        self.query += f" and company = '{self.filters.company}'"

    def add_item_group_filter(self):
        self.query += f" and item_code in (SELECT name from `tabItem` where item_group ='{self.filters.item_group}')"

    def add_item_code_filter(self):
        self.query += f" and item_code = '{self.filters.item_code}'"

    def add_branch_filter(self):
        self.query += f" and branch = '{self.filters.branch}'"
    
    def add_party_filter(self):
        parties = "','".join(map(str,self.filters.party))
        self.query += f" AND party IN('{parties}')"

    def get_data(self):

        si_query = """SELECT 
        si.name as voucher_no,
        si.posting_date as voucher_date,
        si.customer as party,
        si.customer_name as party_name,
        sii.qty as qty,
        '' as vendor_bill,
        '' as vendor_bill_date,
        si.creation as creation,
        'Sales Invoice' as voucher_type,
        'Customer' as party_type,
        si.branch as branch,
        si.company as company,
        sii.item_code as item_code
        from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name = sii.parent WHERE si.docstatus = 1"""

        pi_query = """SELECT 
        pi.name as voucher_no,
        pi.posting_date as voucher_date,
        pi.supplier as party,
        pi.supplier_name as party_name,
        pii.qty as qty,
        pi.bill_no as vendor_bill,
        pi.bill_date as vendor_bill_date,
        pi.creation as creation,
        'Purchase Invoice' as voucher_type,
        'Supplier' as party_type,
        pi.branch as branch,
        pi.company as company,
        pii.item_code as item_code
        from `tabPurchase Invoice` as pi join `tabPurchase Invoice Item` as pii on pi.name = pii.parent WHERE pi.docstatus = 1"""

        so_query = """SELECT 
        so.name as voucher_no,
        so.transaction_date as voucher_date,
        so.customer as party,
        so.customer_name as party_name,
        soi.qty as qty,
        '' as vendor_bill,
        '' as vendor_bill_date,
        so.creation as creation,
        'Sales Order' as voucher_type,
        'Customer' as party_type,
        so.branch as branch,
        so.company as company,
        soi.item_code as item_code
        from `tabSales Order` as so join `tabSales Order Item` as soi on so.name = soi.parent WHERE so.docstatus = 1"""

        po_query = """SELECT 
        po.name as voucher_no,
        po.transaction_date as voucher_date,
        po.supplier as party,
        po.supplier_name as party_name,
        poi.qty as qty,
        '' as vendor_bill,
        '' as vendor_bill_date,
        po.creation as creation,
        'Purchase Order' as voucher_type,
        'Supplier' as party_type,
        po.branch as branch,
        po.company as company,
        poi.item_code as item_code
        from `tabPurchase Order` as po join `tabPurchase Order Item` as poi on po.name = poi.parent WHERE po.docstatus = 1"""

        if self.filters.voucher_type:
            if self.filters.voucher_type == "Sales Invoice":
                query = si_query
            elif self.filters.voucher_type == "Purchase Invoice":
                query = pi_query
            elif self.filters.voucher_type == "Sales Order":
                query = so_query
            elif self.filters.voucher_type == "Purchase Order":
                query = po_query
        else:
            query = "("+ si_query + ") UNION ALL (" + pi_query + ")"

        self.query = f"SELECT voucher_no,voucher_date,party,party_name,sum(qty) as qty,vendor_bill,vendor_bill_date,creation,voucher_type,party_type from ({query}) as query"
        self.add_date_filter()

        if self.filters.company:
            self.add_company_filter()

        if self.filters.item_group:
            self.add_item_group_filter()

        if self.filters.item_code:
            self.add_item_code_filter()
        
        if self.filters.branch:
            self.add_branch_filter()
            
        if len(self.filters.party)>0:
            self.add_party_filter()

        self.query += " group by voucher_no order by voucher_date,creation,voucher_no"

        self.data = frappe.db.sql(self.query, self.query_filters,as_dict=1)

    def get_stock_balance(self,date):
        query = """SELECT w.* FROM `tabWarehouse` as w JOIN `tabBranch` as b on w.branch = b.name WHERE w.is_group = 0 AND w.company = %(company)s"""
        filters = {"company" : self.filters.get("company")}

        if self.filters.branch:
            query += """ AND w.branch = %(branch)s"""
            filters["branch"] = self.filters.get("branch")

        warehouse_list = frappe.db.sql(query,filters,as_dict=1)
        
        item_query = """SELECT DISTINCT item_code FROM `tabStock Ledger Entry` where company = %(company)s"""
        item_query_filters = {"company":self.filters.company}
        
        if self.filters.item_group:
            item_query+=""" AND item_code IN (select name from `tabItem` where item_group = %(item_group)s)"""
            item_query_filters["item_group"] = self.filters.item_group

        if self.filters.item_code:
            item_query+=""" AND item_code = %(item_code)s"""
            item_query_filters["item_code"] = self.filters.item_code


        stock = 0
        for warehouse in warehouse_list:
            item_query_exe = item_query + """ AND warehouse = %(wh)s"""
            item_query_filters["wh"] = warehouse.name
            items = frappe.db.sql(item_query_exe,item_query_filters,as_dict=1)
            for item in items:
                stock += get_stock_balance(warehouse = warehouse.name,item_code=item["item_code"],posting_date=date)
        return stock

    def get_summery(self):
        open_qty = 0
        in_qty = 0
        out_qty = 0
        close_qty = 0

        open_qty = self.get_stock_balance(getdate( self.filters.from_date))
        for row in self.data:
            if row.voucher_type in ["Purchase Invoice","Purchase Order"]:
                in_qty += row.qty
            if row.voucher_type in ["Sales Invoice","Sales Order"]:
                out_qty += row.qty
        
        close_qty = self.get_stock_balance(getdate( self.filters.to_date))

        self.summery = [
            {"value": open_qty, "label": _("Opening Quantity"), "datatype": "Float"},
            {"value": in_qty, "label": _("Incoming Quantity"), "datatype": "Float"},
            {"value": out_qty, "label": _("Outgoing Quantity"), "datatype": "Float"},
            {"value": close_qty, "label": _("Closing Quantity"), "datatype": "Float"},
        ]

