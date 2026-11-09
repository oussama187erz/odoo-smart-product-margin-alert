# -*- coding: utf-8 -*-
# Part of Smart Product Margin Alert module.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_low_margin_lines = fields.Boolean(
        string="Contains Low Margin Lines",
        compute='_compute_margin_summary',
        store=True,
        help="Flags if any active line on this order is below its target margin."
    )
    has_blocked_margin_lines = fields.Boolean(
        string="Contains Blocked Margin Lines",
        compute='_compute_margin_summary',
        store=True,
        help="Flags if any line on this order has a margin violation with 'Block Confirmation' policy."
    )
    low_margin_lines_count = fields.Integer(
        string="Low Margin Items Count",
        compute='_compute_margin_summary',
        store=True
    )
    margin_approval_state = fields.Selection(
        selection=[
            ('normal', 'Compliant'),
            ('warning', 'Warning (Below Target)'),
            ('blocked', 'Blocked (Action Required)'),
            ('overridden', 'Manager Overridden'),
        ],
        string="Margin Compliance State",
        default='normal',
        tracking=True,
        copy=False,
        help="Overall compliance status of this sales order regarding profit margin requirements."
    )
    margin_overridden_by_id = fields.Many2one(
        comodel_name='res.users',
        string="Override Approved By",
        readonly=True,
        copy=False
    )
    margin_override_date = fields.Datetime(
        string="Override Approved On",
        readonly=True,
        copy=False
    )

    @api.depends(
        'order_line.has_margin_warning',
        'order_line.is_margin_blocked',
        'order_line.margin_status',
        'order_line.display_type'
    )
    def _compute_margin_summary(self):
        for order in self:
            valid_lines = order.order_line.filtered(lambda l: not l.display_type and l.product_id)
            warned_lines = valid_lines.filtered(lambda l: l.has_margin_warning)
            blocked_lines = valid_lines.filtered(lambda l: l.is_margin_blocked)

            order.has_low_margin_lines = bool(warned_lines)
            order.has_blocked_margin_lines = bool(blocked_lines)
            order.low_margin_lines_count = len(warned_lines)

            # Preserve overridden state if already approved by manager
            if order.margin_approval_state != 'overridden':
                if blocked_lines:
                    order.margin_approval_state = 'blocked'
                elif warned_lines:
                    order.margin_approval_state = 'warning'
                else:
                    order.margin_approval_state = 'normal'

    def action_override_margin_block(self):
        """Allows authorized Margin Compliance Managers to approve low-margin orders."""
        self.ensure_one()
        if not self.env.user.has_group('smart_product_margin_alert.group_margin_manager'):
            raise UserError(_(
                "Access Denied: Only users with the 'Margin Compliance Manager' role "
                "are authorized to override order margin confirmation blocks."
            ))

        if not self.company_id.allow_manager_margin_override:
            raise UserError(_(
                "Configuration Notice: Manager margin override is disabled in the company settings."
            ))

        self.write({
            'margin_approval_state': 'overridden',
            'margin_overridden_by_id': self.env.user.id,
            'margin_override_date': fields.Datetime.now(),
        })

        # Post audit note to chatter
        blocked_lines = self.order_line.filtered(lambda l: l.is_margin_blocked)
        lines_summary = "<br/>".join([
            f"• <b>{l.product_id.display_name}</b>: Sold at {l.price_unit:.2f} | Margin: {l.line_margin_percent:.1f}% (Required: {l.min_margin_percent:.1f}%)"
            for l in blocked_lines
        ])
        self.message_post(
            body=_(
                "<b>🛡️ Margin Block Overridden</b><br/>"
                "User <b>%(user)s</b> authorized confirmation for order <b>%(order)s</b> despite margin violations:<br/>%(lines)s"
            ) % {
                'user': self.env.user.name,
                'order': self.name,
                'lines': lines_summary or _("No specific lines"),
            },
            subtype_xmlid="mail.mt_note",
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Margin Override Approved"),
                'message': _("Order %s margin block has been authorized by %s. You may now confirm the order.") % (self.name, self.env.user.name),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_confirm(self):
        """Authoritative confirmation check enforcing margin compliance."""
        for order in self:
            if order.has_blocked_margin_lines and order.margin_approval_state != 'overridden':
                blocked_lines = order.order_line.filtered(lambda l: l.is_margin_blocked)
                details = "\n".join([
                    f"• {line.product_id.display_name}: Sold at {line.price_unit:.2f} (Cost: {line.purchase_price:.2f}) -> Margin: {line.line_margin_percent:.2f}% (Minimum Required: {line.min_margin_percent:.2f}%)"
                    for line in blocked_lines
                ])
                raise ValidationError(_(
                    "⚠️ SALES CONFIRMATION BLOCKED - MARGIN COMPLIANCE\n\n"
                    "This sales order cannot be confirmed because the following product(s) fail to satisfy "
                    "the minimum profit margin requirement set to 'Block Sales Confirmation':\n\n"
                    "%(details)s\n\n"
                    "Resolution Options:\n"
                    "1. Adjust unit price(s) on the affected line(s) to meet the required margin.\n"
                    "2. Request an authorized Margin Compliance Manager to click 'Manager Override' on this order."
                ) % {'details': details})

            # If order has warnings and company chatter audit is enabled, log summary
            if order.has_low_margin_lines and order.company_id.notify_low_margin_confirmation:
                warned_lines = order.order_line.filtered(lambda l: l.has_margin_warning)
                lines_str = "<br/>".join([
                    f"• <b>{l.product_id.display_name}</b>: Sold at {l.price_unit:.2f} (Cost: {l.purchase_price:.2f}) -> Margin: {l.line_margin_percent:.1f}% (Target: {l.min_margin_percent:.1f}%)"
                    for l in warned_lines
                ])
                order.message_post(
                    body=_(
                        "<b>⚠️ Margin Compliance Notice upon Confirmation</b><br/>"
                        "This order was confirmed with %(count)d item(s) below target profit margin:<br/>%(lines)s"
                    ) % {
                        'count': len(warned_lines),
                        'lines': lines_str,
                    },
                    subtype_xmlid="mail.mt_note",
                )

        return super().action_confirm()
