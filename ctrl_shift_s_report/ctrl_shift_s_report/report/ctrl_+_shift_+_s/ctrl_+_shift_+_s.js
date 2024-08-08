// Copyright (c) 2024, Software At Work (India) Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ctrl + Shift + S"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_default("company")
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "120",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "120",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "120",
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width": "120",
			on_change: async function () {
				frappe.query_report.set_filter_value('item_desc', "");
				frappe.query_report.set_filter_value('item_code', "");
				frappe.query_report.set_filter_value('abc_classification', "");
				frappe.query_report.set_filter_value('price_list_rate', "");
			}
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "120",
			on_change: async function () {
				let value = frappe.query_report.get_filter_value('item_code');
				frappe.query_report.set_filter_value('item_group', "");
				if (value == "" || value == undefined) {
					frappe.query_report.set_filter_value('item_desc', "");
					frappe.query_report.set_filter_value('abc_classification', "");
					frappe.query_report.set_filter_value('price_list_rate', "");
				} else {
					let data = await frappe.db.get_value("Item", value, ['description', 'abc']);
					let price_list = frappe.query_report.get_filter_value('price_list');
					frappe.query_report.set_filter_value('item_desc', data.message.description);
					frappe.query_report.set_filter_value('abc_classification', data.message.abc);
					frappe.call({
						method: 'frappe.client.get_value',
						args: {
							doctype: 'Item Price',
							filters: {
								item_code: value,
								price_list: price_list
							},
							fieldname: ['price_list_rate']
						},
						callback: function (r) {
							if (r.message) {
								var price_list_rate = r.message.price_list_rate;
								if (price_list_rate != undefined)
									frappe.query_report.set_filter_value('price_list_rate', price_list_rate);
								else
									frappe.query_report.set_filter_value('price_list_rate', 0);

							}
						}
					});
				}
			}
		},
		{
			"fieldname": "item_desc",
			"label": __("Item Desc"),
			"fieldtype": "Data",
			"width": "120",
			"read_only": 1
		},
		{
			"fieldname": "price_list_rate",
			"label": __("Price List Rate"),
			"fieldtype": "Currency",
			"width": "120",
			"read_only": 1
		},
		{
			"fieldname": "abc_classification",
			"label": __("ABC Classification"),
			"fieldtype": "Data",
			"width": "120",
			"read_only": 1
		},
		{
			"fieldname": "party_type",
			"label": __("Party Type"),
			"fieldtype": "Autocomplete",
			options: ["Customer", "Supplier"],
			on_change: function () {
				frappe.query_report.set_filter_value('party', "");
			}
		},
		{
			"fieldname": "party",
			"label": __("Party"),
			"fieldtype": "MultiSelectList",
			get_data: function (txt) {
				if (!frappe.query_report.filters) return;

				let party_type = frappe.query_report.get_filter_value('party_type');
				if (!party_type) return;

				return frappe.db.get_link_options(party_type, txt);
			},
		},
		{
			"fieldname": "voucher_type",
			"label": __("Voucher Type"),
			"fieldtype": "Autocomplete",
			options: ["Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order"],
		},
		{
			"fieldname": "price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
			"default": "Current Rate",
			"width": "120",
			on_change: async function () {
				let value = frappe.query_report.get_filter_value('item_code');
				let price_list = frappe.query_report.get_filter_value('price_list');
				frappe.call({
					method: 'frappe.client.get_value',
					args: {
						doctype: 'Item Price',
						filters: {
							item_code: value,
							price_list: price_list
						},
						fieldname: ['price_list_rate']
					},
					callback: function (r) {
						if (r.message) {
							var price_list_rate = r.message.price_list_rate;
							if (price_list_rate != undefined)
								frappe.query_report.set_filter_value('price_list_rate', price_list_rate);
							else
								frappe.query_report.set_filter_value('price_list_rate', 0);

						}
					}
				});
			}
		}
	]
};
