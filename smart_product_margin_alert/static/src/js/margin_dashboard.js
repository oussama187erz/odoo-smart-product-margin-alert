/** @odoo-module **/

import { Component, useState, onWillStart, useEffect, useRef, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";

export class ProductMarginDashboard extends Component {
    static template = "smart_product_margin_alert.ProductMarginDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.distCanvasRef = useRef("distCanvas");
        this.statusCanvasRef = useRef("statusCanvas");
        this.profitCanvasRef = useRef("profitCanvas");
        this.lowestCanvasRef = useRef("lowestCanvas");

        this.chartInstances = [];

        this.state = useState({
            loading: true,
            filterStatus: "all",
            data: {
                company_name: "",
                currency_symbol: "$",
                kpi: {
                    total_monitored: 0,
                    healthy_count: 0,
                    healthy_pct: 0,
                    low_count: 0,
                    low_pct: 0,
                    negative_count: 0,
                    negative_pct: 0,
                    avg_margin_percent: 0,
                    default_min_margin: 20,
                    avg_margin_diff: 0,
                },
                charts: {
                    distribution: { labels: [], data: [] },
                    status_donut: { labels: [], data: [], colors: [] },
                    top_profitable: [],
                    lowest_margin: [],
                },
                alerts: [],
            },
        });

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.loadData();
        });

        useEffect(() => {
            if (!this.state.loading && window.Chart) {
                this.renderAllCharts();
            }
        });

        onWillUnmount(() => {
            this.destroyCharts();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const result = await this.orm.call(
                "smart.product.margin.dashboard",
                "get_dashboard_data",
                [],
                { filter_status: this.state.filterStatus }
            );
            this.state.data = result;
        } catch (error) {
            console.error("Error loading Product Margin Intelligence Dashboard data:", error);
            this.notification.add("Failed to load margin analytics data.", {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }

    async refreshDashboard() {
        this.destroyCharts();
        await this.loadData();
    }

    async setFilter(filter) {
        if (this.state.filterStatus === filter) return;
        this.state.filterStatus = filter;
        this.destroyCharts();
        await this.loadData();
    }

    destroyCharts() {
        for (const chart of this.chartInstances) {
            try {
                chart.destroy();
            } catch (e) {
                console.warn("Could not destroy chart instance", e);
            }
        }
        this.chartInstances = [];
    }

    renderAllCharts() {
        this.destroyCharts();

        // 1. Margin Distribution Bar Chart
        if (this.distCanvasRef.el) {
            const dist = this.state.data.charts.distribution;
            const distChart = new window.Chart(this.distCanvasRef.el, {
                type: "bar",
                data: {
                    labels: dist.labels,
                    datasets: [
                        {
                            label: "Number of Products",
                            data: dist.data,
                            backgroundColor: [
                                "#DC2626", // Loss
                                "#EA580C", // Critical
                                "#F59E0B", // Low
                                "#5146E5", // Healthy
                                "#16A34A", // High
                            ],
                            borderRadius: 6,
                            borderSkipped: false,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => ` ${context.parsed.y} products`,
                            },
                        },
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0, stepSize: 1 },
                            grid: { color: "#F1F5F9" },
                        },
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 11 } },
                        },
                    },
                },
            });
            this.chartInstances.push(distChart);
        }

        // 2. Margin Status Donut Chart
        if (this.statusCanvasRef.el) {
            const donut = this.state.data.charts.status_donut;
            const statusChart = new window.Chart(this.statusCanvasRef.el, {
                type: "doughnut",
                data: {
                    labels: donut.labels,
                    datasets: [
                        {
                            data: donut.data,
                            backgroundColor: donut.colors,
                            borderWidth: 2,
                            borderColor: "#FFFFFF",
                            hoverOffset: 4,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "68%",
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: {
                                boxWidth: 12,
                                padding: 14,
                                font: { size: 12, weight: "500" },
                            },
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => ` ${context.label}: ${context.raw} products`,
                            },
                        },
                    },
                },
            });
            this.chartInstances.push(statusChart);
        }

        // 3. Top Profitable Products (Horizontal Bar Chart)
        if (this.profitCanvasRef.el) {
            const topList = this.state.data.charts.top_profitable || [];
            const profitChart = new window.Chart(this.profitCanvasRef.el, {
                type: "bar",
                data: {
                    labels: topList.map((p) => p.name.length > 22 ? p.name.substring(0, 20) + "..." : p.name),
                    datasets: [
                        {
                            label: `Profit per Unit (${this.state.data.currency_symbol})`,
                            data: topList.map((p) => p.profit),
                            backgroundColor: "#5146E5",
                            borderRadius: 4,
                            barPercentage: 0.7,
                        },
                    ],
                },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const item = topList[context.dataIndex];
                                    return ` Profit: ${item.profit} ${this.state.data.currency_symbol} (Margin: ${item.margin_percent}%)`;
                                },
                            },
                        },
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            grid: { color: "#F1F5F9" },
                        },
                        y: {
                            grid: { display: false },
                            ticks: { font: { size: 11 } },
                        },
                    },
                },
            });
            this.chartInstances.push(profitChart);
        }

        // 4. Lowest Margin Products (Horizontal Bar Chart)
        if (this.lowestCanvasRef.el) {
            const lowList = this.state.data.charts.lowest_margin || [];
            const lowestChart = new window.Chart(this.lowestCanvasRef.el, {
                type: "bar",
                data: {
                    labels: lowList.map((p) => p.name.length > 22 ? p.name.substring(0, 20) + "..." : p.name),
                    datasets: [
                        {
                            label: "Margin (%)",
                            data: lowList.map((p) => p.margin_percent),
                            backgroundColor: lowList.map((p) => p.margin_percent < 0 ? "#DC2626" : "#F59E0B"),
                            borderRadius: 4,
                            barPercentage: 0.7,
                        },
                    ],
                },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const item = lowList[context.dataIndex];
                                    return ` Margin: ${item.margin_percent}% | Min Required: ${item.min_margin_percent}%`;
                                },
                            },
                        },
                    },
                    scales: {
                        x: {
                            grid: { color: "#F1F5F9" },
                        },
                        y: {
                            grid: { display: false },
                            ticks: { font: { size: 11 } },
                        },
                    },
                },
            });
            this.chartInstances.push(lowestChart);
        }
    }

    formatCurrency(amount) {
        if (amount === undefined || amount === null) return `0.00 ${this.state.data.currency_symbol}`;
        const formatted = new Intl.NumberFormat("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(amount);
        return `${formatted} ${this.state.data.currency_symbol}`;
    }

    openProduct(productId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Product Profitability Details",
            res_model: "product.template",
            res_id: productId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openMarginMonitor(filterDomain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Product Margin Monitor",
            res_model: "product.template",
            domain: [["margin_monitoring_enabled", "=", true], ...filterDomain],
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openSalesOrders(filterDomain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Margin Compliance Sales Orders",
            res_model: "sale.order",
            domain: filterDomain.length ? filterDomain : [["has_low_margin_lines", "=", true]],
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openSettings() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Margin Intelligence Configuration",
            res_model: "res.config.settings",
            views: [[false, "form"]],
            target: "current",
            context: { module: "smart_product_margin_alert" },
        });
    }
}

registry.category("actions").add("product_margin_dashboard", ProductMarginDashboard);
