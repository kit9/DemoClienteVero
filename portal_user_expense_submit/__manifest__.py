# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Expenses Submit Portal User Employee from Website",
    'version': '1.1.2',
    'category': 'Human Resources',
    'price': 79.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """ This app allow your portal employee submit HR Expenses and View Expenses Sheet from my account Portal.""",
    'description': """
This module allow your portal employee to view, create Expenses and Show Expenses Sheet from my account
Odoo Expense Portal User Employee
Odoo Expense Portal User Employee
Portal Expense Employee
Odoo Portal Expense
Odoo Expense Employee
Odoo Employee Expense Self Service Portal
employee expense portal
self service portal expense
self service employee expense portal
expense employee portal self service
employee self service
ESS
ess
self service odoo
portal
self service
self portal
odoo self service employee
employee portal
employee job portal
self service odoo employee
employee details
employee leave
employee expense
employee holidays
self service portal​
Odoo expense Portal User Employee
Expense Portal User
Odoo expenses
Your expenses
My expenses
Project expense
User expenses
Employee expenses
Portal user expenses
portal expense
website expense
enterprise user expense
enterprise expense user
enterprise employee expense
enterprise expense employee
expense for enterprise user
expense for enterprise employee
expense recording
expense entry for enterprise
expense entry employee enterprise
enterprise paid users
enterprise free users
enterprise employee user
enterprise user employee
expense user fill
expense employee fill
enterprise expense encoding
expense fill
enterprise expense
hr expense
hr expense enterprise employee
hr expense enterprise user
enterprise fill expense activities
expense activities
expense lines enterprise user
expense lines enterprise employee
expense work enterprise user
expense work user
expense work employee enterprise
portal expense enterprise
portal expense
website expense
expense data
odoo enterprise user
odoo enterprise employee
odoo external employee
odoo external user
external user expense
worker expense
This module allow you to employee(s) who are portal user and it will allow to record expense.
labour expense
external employee expense
external user expense
expense Entry from Web-My Account using Portal User as Employee
external expense employee
external expense user
                   """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'images': ['static/description/submit.png'],
    'live_test_url': 'https://youtu.be/s3LlNs70Z3Q',
    'depends': [
        'hr',
        'website',
        'portal',
        'hr_expense',
    ],
    'data': [
        'views/user.xml',
        'views/expense_portal_templent.xml',
        'views/expences_sheet_template.xml',
        'views/expense.xml',
        'report/expense_report.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 0,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
