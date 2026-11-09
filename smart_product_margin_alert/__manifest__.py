# -*- coding: utf-8 -*-
# Part of Smart Product Margin Alert module.
# Commercial Edition for Odoo 18 Community.

{
    'name': 'Smart Product Margin Alert',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Intelligent Product Margin Monitoring, Real-time Sales Alerts & Executive Margin Analytics',
    'description': """
Smart Product Margin Alert — Commercial Edition
===============================================
A premium enterprise application for Odoo 18 Community that provides real-time gross margin intelligence, 
automated sales order margin protection, and executive profitability analytics.

Key Enterprise Features:
-----------------------
* **Product Margin Intelligence Dashboard (OWL + Chart.js)**:
  - Real-time KPI Cards: Monitored Products, Healthy Margins, Low Margins, Loss-Making & Average Profit Margin.
  - Interactive Visualizations: Margin Distribution, Compliance Status Donut, Top 10 Profitable & Lowest Margin items.
  - Live Margin Alerts table highlighting at-risk products with instant inspection shortcuts.
* **Intelligent Product Margin Monitor**:
  - Filterable list view with color-coded profit badges, margins, minimum thresholds, and alert modes.
  - Advanced search filters: Monitored Products, Healthy, Low Margin Alert, Loss-Making, Block Mode vs Warning Mode.
* **Product Form Margin Intelligence Tab**:
  - Clean 3-group layout: Configuration, Profitability Metrics, Status & Risk.
  - Contextual visual banners alerting managers if a product is selling at a loss or below margin targets.
* **Sales Order Experience & Validation**:
  - Real-time line-by-line margin calculations with clear status badges.
  - Multi-tier alert enforcement: 'Warning Only' with automated Chatter audit logging, or 'Block Confirmation'.
  - Native alert banners with authorized 'Manager Override' workflow for approved commercial exceptions.
* **Multi-Company & Security Governance**:
  - Configurable global margin defaults per company.
  - Two-tier security roles: Viewer/User and Margin Compliance Manager.
    """,
    'author': 'Antigravity Enterprise Solutions',
    'website': 'https://github.com/antigravity',
    'license': 'OPL-1',
    'depends': [
        'base',
        'product',
        'sale_management',
        'sale_margin',
    ],
    'data': [
        'security/margin_security.xml',
        'security/ir.model.access.csv',
        'data/demo_products.xml',
        'views/res_config_settings_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/margin_dashboard_views.xml',
        'views/margin_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smart_product_margin_alert/static/src/scss/margin_dashboard.scss',
            'smart_product_margin_alert/static/src/xml/margin_dashboard.xml',
            'smart_product_margin_alert/static/src/js/margin_dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 49.00,
    'currency': 'EUR',
}
