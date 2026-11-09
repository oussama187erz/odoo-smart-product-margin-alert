# -*- coding: utf-8 -*-
# Part of Smart Product Margin Alert module.

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin_monitoring_enabled = fields.Boolean(
        string="Margin Monitored",
        compute='_compute_margin_alert_info',
        store=True
    )
    min_margin_percent = fields.Float(
        string="Required Margin (%)",
        compute='_compute_margin_alert_info',
        store=True,
        digits=(16, 2),
        help="Minimum required profit margin for this product."
    )
    line_margin_percent = fields.Float(
        string="Margin (%)",
        compute='_compute_margin_alert_info',
        store=True,
        digits=(16, 2),
        help="Actual realized margin percentage on this order line based on sales price and cost."
    )
    margin_alert_mode = fields.Selection(
        selection=[
            ('disabled', 'Disabled'),
            ('warning', 'Warning Only'),
            ('block', 'Block Sales Confirmation'),
        ],
        string="Margin Policy",
        compute='_compute_margin_alert_info',
        store=True
    )
    margin_status = fields.Selection(
        selection=[
            ('healthy', 'Healthy'),
            ('low', 'Low Margin'),
            ('negative', 'Negative / Loss-Making'),
        ],
        string="Margin Status",
        compute='_compute_margin_alert_info',
        store=True
    )
    has_margin_warning = fields.Boolean(
        string="Has Margin Warning",
        compute='_compute_margin_alert_info',
        store=True
    )
    is_margin_blocked = fields.Boolean(
        string="Confirmation Blocked",
        compute='_compute_margin_alert_info',
        store=True,
        help="Indicates whether this order line is currently blocking sales order confirmation due to compliance rules."
    )
    margin_alert_badge = fields.Char(
        string="Margin Intelligence Status",
        compute='_compute_margin_alert_info',
        store=True
    )

    @api.depends(
        'product_id',
        'product_id.margin_monitoring_enabled',
        'product_id.min_margin_percent',
        'product_id.margin_alert_mode',
        'price_subtotal',
        'purchase_price',
        'product_uom_qty',
        'order_id.company_id'
    )
    def _compute_margin_alert_info(self):
        for line in self:
            if line.display_type or not line.product_id:
                line.margin_monitoring_enabled = False
                line.min_margin_percent = 0.0
                line.line_margin_percent = 0.0
                line.margin_alert_mode = 'disabled'
                line.margin_status = 'healthy'
                line.has_margin_warning = False
                line.is_margin_blocked = False
                line.margin_alert_badge = ''
                continue

            product = line.product_id
            monitored = bool(product.margin_monitoring_enabled)
            min_margin = product.min_margin_percent if monitored else 0.0
            alert_mode = product.margin_alert_mode if monitored else 'disabled'

            subtotal = line.price_subtotal or 0.0
            cost_total = (line.purchase_price or 0.0) * (line.product_uom_qty or 0.0)
            profit = subtotal - cost_total

            if subtotal > 0.0:
                pct = (profit / subtotal) * 100.0
            elif subtotal == 0.0 and cost_total > 0.0:
                pct = -100.0
            elif subtotal == 0.0 and cost_total == 0.0:
                pct = 0.0
            else:
                pct = -100.0

            line.margin_monitoring_enabled = monitored
            line.min_margin_percent = min_margin
            line.line_margin_percent = pct
            line.margin_alert_mode = alert_mode

            if not monitored or alert_mode == 'disabled':
                line.margin_status = 'healthy'
                line.has_margin_warning = False
                line.is_margin_blocked = False
                line.margin_alert_badge = _("Monitoring Disabled")
            elif profit < 0.0 or pct < 0.0:
                line.margin_status = 'negative'
                line.has_margin_warning = True
                line.is_margin_blocked = (alert_mode == 'block')
                line.margin_alert_badge = _("Loss-Making (%.1f%% / Min: %.1f%%)") % (pct, min_margin)
            elif pct < min_margin:
                line.margin_status = 'low'
                line.has_margin_warning = True
                line.is_margin_blocked = (alert_mode == 'block')
                line.margin_alert_badge = _("Low Margin (%.1f%% / Min: %.1f%%)") % (pct, min_margin)
            else:
                line.margin_status = 'healthy'
                line.has_margin_warning = False
                line.is_margin_blocked = False
                line.margin_alert_badge = _("Healthy (%.1f%%)") % pct
