# -*- coding: utf-8 -*-
# Part of Smart Product Margin Alert module.

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_min_margin_percent(self):
        company = self.env.company
        return company.default_min_margin_percent if company else 20.0

    def _default_margin_alert_mode(self):
        company = self.env.company
        return company.default_margin_alert_mode if company else 'warning'

    # Configuration Group
    margin_monitoring_enabled = fields.Boolean(
        string="Enable Margin Monitoring",
        default=True,
        help="When enabled, this product is actively monitored for gross profit margin compliance across catalog and sales operations."
    )
    min_margin_percent = fields.Float(
        string="Minimum Margin (%)",
        default=_default_min_margin_percent,
        digits=(16, 2),
        help="Target minimum gross margin percentage required for this product. Sales priced below this threshold trigger alerts or confirmation blocks."
    )
    margin_alert_mode = fields.Selection(
        selection=[
            ('disabled', 'Disabled'),
            ('warning', 'Warning Only'),
            ('block', 'Block Sales Confirmation'),
        ],
        string="Alert Mode",
        default=_default_margin_alert_mode,
        help="Enforcement policy applied during sales order workflow when the sold price produces a margin below the required minimum."
    )

    # Profitability Metrics Group
    profit_amount = fields.Monetary(
        string="Profit Amount",
        compute="_compute_margin_metrics",
        store=True,
        currency_field="currency_id",
        help="Gross profit per unit (Sales Price - Standard Cost Price)."
    )
    current_margin_percent = fields.Float(
        string="Current Margin (%)",
        compute="_compute_margin_metrics",
        store=True,
        digits=(16, 2),
        help="Current gross margin percentage: ((Sales Price - Cost Price) / Sales Price) * 100."
    )

    # Status & Risk Group
    margin_status = fields.Selection(
        selection=[
            ('healthy', 'Healthy'),
            ('low', 'Low Margin'),
            ('negative', 'Negative / Loss-Making'),
        ],
        string="Margin Status",
        compute="_compute_margin_metrics",
        store=True,
        help="Real-time compliance status comparing current margin against the configured target."
    )
    margin_risk_level = fields.Selection(
        selection=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk / Loss'),
        ],
        string="Risk Level",
        compute="_compute_margin_metrics",
        store=True,
        help="Executive risk assessment level."
    )

    @api.depends('list_price', 'standard_price', 'min_margin_percent', 'margin_monitoring_enabled')
    def _compute_margin_metrics(self):
        for template in self:
            sales_price = template.list_price or 0.0
            cost_price = template.standard_price or 0.0
            profit = sales_price - cost_price
            template.profit_amount = profit

            if sales_price > 0.0:
                margin_pct = (profit / sales_price) * 100.0
            elif sales_price == 0.0 and cost_price > 0.0:
                margin_pct = -100.0
            elif sales_price < 0.0:
                margin_pct = -100.0
            else:
                margin_pct = 0.0

            template.current_margin_percent = margin_pct

            if not template.margin_monitoring_enabled:
                template.margin_status = 'healthy'
                template.margin_risk_level = 'low'
            elif profit < 0.0 or margin_pct < 0.0:
                template.margin_status = 'negative'
                template.margin_risk_level = 'high'
            elif margin_pct < (template.min_margin_percent or 0.0):
                template.margin_status = 'low'
                template.margin_risk_level = 'medium'
            else:
                template.margin_status = 'healthy'
                template.margin_risk_level = 'low'

    def action_view_margin_history(self):
        """Action to inspect recent sales order lines for this product to analyze actual realized margins."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Sales Margin History - %s") % self.name,
            'res_model': 'sale.order.line',
            'view_mode': 'list,form',
            'domain': [('product_id.product_tmpl_id', '=', self.id), ('state', 'in', ['sale', 'done'])],
            'context': {'default_product_id': self.product_variant_id.id if self.product_variant_id else False},
        }
