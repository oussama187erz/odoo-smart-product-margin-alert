# -*- coding: utf-8 -*-
# Part of Smart Product Margin Alert module.

from odoo import api, models, _


class ProductMarginDashboard(models.AbstractModel):
    _name = 'smart.product.margin.dashboard'
    _description = 'Product Margin Intelligence Analytics Backend'

    @api.model
    def get_dashboard_data(self, filter_status='all'):
        """Computes live analytics data for the Product Margin Intelligence dashboard."""
        company = self.env.company
        currency = company.currency_id
        currency_symbol = currency.symbol or '$'

        domain = [
            ('margin_monitoring_enabled', '=', True),
            ('company_id', 'in', [False, company.id]),
        ]

        if filter_status == 'low':
            domain.append(('margin_status', '=', 'low'))
        elif filter_status == 'negative':
            domain.append(('margin_status', '=', 'negative'))
        elif filter_status == 'healthy':
            domain.append(('margin_status', '=', 'healthy'))
        elif filter_status == 'alerts':
            domain.append(('margin_status', 'in', ['low', 'negative']))

        ProductTemplate = self.env['product.template'].with_context(active_test=True)
        products = ProductTemplate.search(domain)

        # Baseline metrics across all monitored products
        all_monitored = ProductTemplate.search([
            ('margin_monitoring_enabled', '=', True),
            ('company_id', 'in', [False, company.id]),
        ])
        total_monitored = len(all_monitored)

        healthy_products = all_monitored.filtered(lambda p: p.margin_status == 'healthy')
        low_margin_products = all_monitored.filtered(lambda p: p.margin_status == 'low')
        negative_products = all_monitored.filtered(lambda p: p.margin_status == 'negative')

        healthy_count = len(healthy_products)
        low_count = len(low_margin_products)
        negative_count = len(negative_products)

        # Ratios
        healthy_pct = round((healthy_count / total_monitored * 100.0), 1) if total_monitored else 0.0
        low_pct = round((low_count / total_monitored * 100.0), 1) if total_monitored else 0.0
        negative_pct = round((negative_count / total_monitored * 100.0), 1) if total_monitored else 0.0

        # Weighted / Arithmetic average margin %
        if total_monitored:
            total_margin_sum = sum(p.current_margin_percent for p in all_monitored)
            avg_margin_percent = round(total_margin_sum / total_monitored, 1)
        else:
            avg_margin_percent = 0.0

        default_min_margin = company.default_min_margin_percent or 20.0
        avg_margin_diff = round(avg_margin_percent - default_min_margin, 1)

        # Margin Distribution Intervals
        dist_loss = len(all_monitored.filtered(lambda p: p.current_margin_percent < 0.0))
        dist_critical = len(all_monitored.filtered(lambda p: 0.0 <= p.current_margin_percent < 10.0))
        dist_low = len(all_monitored.filtered(lambda p: 10.0 <= p.current_margin_percent < 20.0))
        dist_healthy = len(all_monitored.filtered(lambda p: 20.0 <= p.current_margin_percent < 35.0))
        dist_high = len(all_monitored.filtered(lambda p: p.current_margin_percent >= 35.0))

        # Top 10 Profitable Products (by Profit Amount)
        top_profitable_recs = all_monitored.sorted(key=lambda p: (p.profit_amount, p.current_margin_percent), reverse=True)[:10]
        top_profitable = [{
            'id': p.id,
            'name': p.name,
            'code': p.default_code or '',
            'cost': round(p.standard_price, 2),
            'price': round(p.list_price, 2),
            'profit': round(p.profit_amount, 2),
            'margin_percent': round(p.current_margin_percent, 1),
            'status': p.margin_status,
        } for p in top_profitable_recs]

        # Top 10 Lowest Margin Products
        lowest_margin_recs = all_monitored.sorted(key=lambda p: p.current_margin_percent)[:10]
        lowest_margin = [{
            'id': p.id,
            'name': p.name,
            'code': p.default_code or '',
            'cost': round(p.standard_price, 2),
            'price': round(p.list_price, 2),
            'profit': round(p.profit_amount, 2),
            'margin_percent': round(p.current_margin_percent, 1),
            'min_margin_percent': round(p.min_margin_percent, 1),
            'status': p.margin_status,
        } for p in lowest_margin_recs]

        # Margin Alerts (products requiring attention: low and negative)
        alert_products = all_monitored.filtered(lambda p: p.margin_status in ['low', 'negative']).sorted(
            key=lambda p: p.current_margin_percent
        )
        alerts_list = [{
            'id': p.id,
            'name': p.name,
            'code': p.default_code or '',
            'cost': round(p.standard_price, 2),
            'price': round(p.list_price, 2),
            'profit': round(p.profit_amount, 2),
            'margin_percent': round(p.current_margin_percent, 1),
            'min_margin_percent': round(p.min_margin_percent, 1),
            'status': p.margin_status,
            'status_label': dict(p._fields['margin_status'].selection).get(p.margin_status, p.margin_status),
            'alert_mode': p.margin_alert_mode,
            'alert_mode_label': dict(p._fields['margin_alert_mode'].selection).get(p.margin_alert_mode, p.margin_alert_mode),
        } for p in alert_products]

        return {
            'company_name': company.name,
            'currency_symbol': currency_symbol,
            'kpi': {
                'total_monitored': total_monitored,
                'healthy_count': healthy_count,
                'healthy_pct': healthy_pct,
                'low_count': low_count,
                'low_pct': low_pct,
                'negative_count': negative_count,
                'negative_pct': negative_pct,
                'avg_margin_percent': avg_margin_percent,
                'default_min_margin': default_min_margin,
                'avg_margin_diff': avg_margin_diff,
            },
            'charts': {
                'distribution': {
                    'labels': [
                        _('Loss-Making (< 0%)'),
                        _('Critical (0-10%)'),
                        _('Low (10-20%)'),
                        _('Healthy (20-35%)'),
                        _('High Profit (> 35%)'),
                    ],
                    'data': [dist_loss, dist_critical, dist_low, dist_healthy, dist_high],
                },
                'status_donut': {
                    'labels': [_('Healthy Margin'), _('Low Margin Alert'), _('Loss-Making')],
                    'data': [healthy_count, low_count, negative_count],
                    'colors': ['#16A34A', '#F59E0B', '#DC2626'],
                },
                'top_profitable': top_profitable,
                'lowest_margin': lowest_margin,
            },
            'alerts': alerts_list,
        }
