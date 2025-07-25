quality_checks = [
    {
        "id": "completeness",
        "title": "Completeness",
        "metric_label": "Completeness %",
        "data": [{"column": "id", "value": 98.5}, {"column": "region", "value": 95.2}],
        "icon": "📏"
    },
    {
        "id": "uniqueness",
        "title": "Uniqueness",
        "metric_label": "Uniqueness %",
        "data": [{"column": "id", "value": 99.7}, {"column": "order_id", "value": 100}],
        "icon": "🔐"
    }
]

html = template.render(
    params=params,
    quality_checks=quality_checks,
    plotly_json=plot_json,
    ag_data=json.dumps(ag_data)
)
