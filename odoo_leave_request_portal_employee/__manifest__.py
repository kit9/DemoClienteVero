# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Leaves from Web-My Account using Portal User as Employee',
    'version': '1.3',
    'price': 49.0,
    'currency': 'EUR',
    'category': 'Human Resources',
    'license': 'Other proprietary',
    'summary': 'This module allow your portal employee to view, create and edit own leaves from my account',
    'description': """
Odoo Leave Request Portal Employee
Odoo Leave Request Portal User Employee
Leave Request Portal User
Odoo Leave Request
Your Leave Request
self service
employee self service
self service portal
portal self service
portal employee
portal user
portal login
My attendances
Project Leave Request
User Leave Request
Employee Leave Request
Portal user Leave Request
portal Leave Request
website Leave Request
enterprise user leave request
enterprise leave request user
enterprise employee leave request
enterprise leave request employee
leave request for enterprise user
leave request for enterprise employee
leave request recording
leave request entry for enterprise
leave request entry employee enterprise
leave request paid users
leave request free users
leave request employee user
leave request user employee
leave request user fill
leave request employee fill
enterprise leave request
leave request fill
enterprise leave request
hr leave request
hr leave request enterprise employee
hr leave request enterprise user
enterprise fill leave request activities
leave request activities
leave request lines enterprise user
leave request lines enterprise employee
leave request work enterprise user
leave request work user
leave request work employee enterprise
portal leave request enterprise
portal leave request
website leave request
leave request data
leave request import
leave request export
odoo enterprise user
odoo enterprise employee
odoo external employee
odoo external user
external user leave request
worker leave request
This module allow you to employee(s) who are not real users of system but portal users / external user and it will allow to record leave request.
labour leave request
external employee leave request
external user leave request
leave request Entry from Web-My Account using Portal User as Employee
external leave request employee
external leave request user
Portal Users who are employee of system but not real users can fill/record leave request Activities.
If your company using leave request application but not purchased real users from Odoo Enterprise then your employee can fill leave request as portal users.
No need to create real users in system if you are only using leave request module to make leave request entry for your all employees. So you can create portal users and set it on employee form and employee can use that portal user logged to fill leave request activities.
Make sure you have set Portal leave request group on portal user form on settings of users.
No need to purchase users from Odoo Enterprise only to fill leave request any more.

Odoo Holiday Request Portal User Employee
Holiday Request Portal User
Odoo Holiday Request
Your Holiday Request
My attendances
Project Holiday Request
User Holiday Request
Employee Holiday Request
Portal user Holiday Request
portal Holiday Request
website Holiday Request
enterprise user Holiday request
enterprise Holiday request user
enterprise employee Holiday request
enterprise Holiday request employee
Holiday request for enterprise user
Holiday request for enterprise employee
Holiday request recording
Holiday request entry for enterprise
Holiday request entry employee enterprise
Holiday request paid users
Holiday request free users
Holiday request employee user
Holiday request user employee
Holiday request user fill
Holiday request employee fill
enterprise Holiday request
Holiday request fill
enterprise Holiday request
hr Holiday request
hr Holiday request enterprise employee
hr Holiday request enterprise user
enterprise fill Holiday request activities
Holiday request activities
Holiday request lines enterprise user
Holiday request lines enterprise employee
Holiday request work enterprise user
Holiday request work user
Holiday request work employee enterprise
portal Holiday request enterprise
portal Holiday request
website Holiday request
Holiday request data
Holiday request import
Holiday request export
odoo enterprise user
odoo enterprise employee
odoo external employee
odoo external user
external user Holiday request
worker Holiday request
This module allow you to employee(s) who are not real users of system but portal users / external user and it will allow to record Holiday request.
labour Holiday request
external employee Holiday request
external user Holiday request
Holiday request Entry from Web-My Account using Portal User as Employee
external Holiday request employee
external Holiday request user
Portal Users who are employee of system but not real users can fill/record Holiday request Activities.
If your company using Holiday request application but not purchased real users from Odoo Enterprise then your employee can fill Holiday request as portal users.
No need to create real users in system if you are only using Holiday request module to make Holiday request entry for your all employees. So you can create portal users and set it on employee form and employee can use that portal user logged to fill Holiday request activities.
Make sure you have set Portal Holiday request group on portal user form on settings of users.
No need to purchase users from Odoo Enterprise only to fill Holiday request any more.

For more details please watch Video or contact us before buy.

""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'https://www.probuse.com',
    'images': ['static/description/img1.jpg'],
    # 'live_test_url': 'https://youtu.be/wuk7twK8cCM',
    'live_test_url': 'https://youtu.be/WW8FdlwEmp8',

    'depends': [
                #'website_portal',
                'base',
                'website',
                'portal',
                'hr_holidays',
                'resource',
                ],
    'data': [
        # 'security/holiday_security.xml',
        'security/ir.model.access.csv',
        'views/website_portal_templates.xml',
        'views/users_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
