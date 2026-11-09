# -*- coding: utf-8 -*-
# Part of Smart Product Margin Alert module.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_min_margin_percent = fields.Float(
        related='company_id.default_min_margin_percent',
        readonly=False,
        string="Default Minimum Margin (%)",
        help="Global baseline profit margin threshold for all newly monitored products in this company."
    )
    default_margin_alert_mode = fields.Selection(
        related='company_id.default_margin_alert_mode',
        readonly=False,
        string="Default Alert Mode",
        help="Enforces whether low margin triggers a warning or blocks sales confirmation."
    )
    allow_manager_margin_override = fields.Boolean(
        related='company_id.allow_manager_margin_override',
        readonly=False,
        string="Allow Manager Override",
        help="Empower Margin Managers to approve exceptions and confirm blocked orders."
    )
    notify_low_margin_confirmation = fields.Boolean(
        related='company_id.notify_low_margin_confirmation',
        readonly=False,
        string="Log Low Margin Warning in Chatter",
        help="Creates an immutable compliance log entry in Chatter when orders with low-margin items are processed."
    )
