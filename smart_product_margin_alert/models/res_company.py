# -*- coding: utf-8 -*-
# Part of Smart Product Margin Alert module.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_min_margin_percent = fields.Float(
        string="Default Minimum Margin (%)",
        default=20.0,
        digits=(16, 2),
        help="Global default minimum gross profit margin percentage applied to monitored products."
    )
    default_margin_alert_mode = fields.Selection(
        selection=[
            ('disabled', 'Disabled'),
            ('warning', 'Warning Only'),
            ('block', 'Block Sales Confirmation'),
        ],
        string="Default Margin Alert Mode",
        default='warning',
        help="Default policy when sales orders contain products priced below the minimum margin threshold."
    )
    allow_manager_margin_override = fields.Boolean(
        string="Allow Manager Override",
        default=True,
        help="Permits authorized Margin Compliance Managers to confirm sales orders containing blocked low-margin lines."
    )
    notify_low_margin_confirmation = fields.Boolean(
        string="Chatter Audit on Confirmation",
        default=True,
        help="Automatically post an audit note to the Sales Order chatter whenever low-margin or overridden items are confirmed."
    )
