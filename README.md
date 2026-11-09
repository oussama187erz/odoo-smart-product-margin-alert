# Odoo Smart Product Margin Alert & Analytics Dashboard

A comprehensive Odoo module designed to help businesses monitor, control, and analyze product profit margins in real-time. Protect your business profitability with automated margin alerts during quote creation and interactive analytics dashboards.

---

## Key Features

* **Real-Time Sale Order Margin Alerts:** Get instant visual warnings on Quotation & Sale Order lines when selling below configured minimum target margins.
* **Interactive Margin Dashboard:** Custom JavaScript/OWL dashboard featuring graphical metrics, analytics, and summary key performance indicators (KPIs).
* **Configurable Thresholds:** Easily set minimum margin percentages at company level or per product/product category via standard settings.
* **Product Template Enhancements:** Native integration with product templates to define specific margin rules, cost baselines, and safety bounds.
* **Security & Access Controls:** Built-in security groups (`ir.model.access.csv` & `margin_security.xml`) ensuring restricted access to sensitive margin and cost details.
* **Demo Data Included:** Comes pre-loaded with test products for fast evaluation and deployment testing.

---

## Module Structure

```text
smart_product_margin_alert/
├── data/
│   └── demo_products.xml
├── models/
│   ├── margin_dashboard.py
│   ├── product_template.py
│   ├── res_company.py
│   ├── res_config_settings.py
│   ├── sale_order.py
│   └── sale_order_line.py
├── security/
│   ├── ir.model.access.csv
│   └── margin_security.xml
├── static/
│   ├── description/ (icon.png, banner.png, index.html)
│   └── src/ (js, scss, xml for Dashboard view)
└── views/
    ├── margin_dashboard_views.xml
    ├── margin_menus.xml
    ├── product_template_views.xml
    ├── res_config_settings_views.xml
    └── sale_order_views.xml
