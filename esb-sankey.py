import plotly.graph_objects as go

# Define nodes
platforms = [
    {"name": "Functions Consumption Plan", "group": "compute",
        "start": "2016-10", "end": "2018-06"},
    {"name": "Service Fabric Stateful Applications",
        "group": "compute", "start": "2017-01", "end": "2018-06"},
    {"name": "Functions in Service Fabric Containers",
        "group": "compute", "start": "2018-06", "end": "2023-03"},
    {"name": "Function Containers on Container Apps",
        "group": "compute", "start": "2023-03", "end": None},
    {"name": "Service Bus", "group": "messaging", "start": "2016-10", "end": None},
    {"name": "API Management", "group": "gateway", "start": "2016-10", "end": None}
]

# Define links
links = [
    {"source": "Functions Consumption Plan",
        "target": "Functions in Service Fabric Containers", "value": 1, "date": "2018-06"},
    {"source": "Service Fabric Stateful Applications",
        "target": "Functions in Service Fabric Containers", "value": 1, "date": "2018-06"},
    {"source": "Functions in Service Fabric Containers",
        "target": "Function Containers on Container Apps", "value": 1, "date": "2023-03"}
]

# Add virtual platforms representing current state
# Indicate source and target links in nodes
current_month = "2024-06"
closing_platforms = []
for platform in platforms:
    if not platform["end"]:
        platform["end"] = current_month
        closing_platform = platform.copy()
        closing_platform["start"] = current_month
        closing_platform["end"] = current_month
        closing_platform["name"] = closing_platform["name"] + " (current)"
        closing_platforms.append(closing_platform)
        closing_value = 1
        for l in links:
            if l["target"] == platform["name"] and l["date"] == platform["start"]:
                closing_value = l["value"]
                break
        closing_link = {
            "source": platform["name"],
            "target": closing_platform["name"],
            "value": closing_value
        }
        links.append(closing_link)

    platform["isSource"] = False
    platform["isTarget"] = False

    for l in links:
        if l["source"] == platform["name"]:
            platform["isSource"] = True
        if l["target"] == platform["name"]:
            platform["isTarget"] = True

platforms.extend(closing_platforms)

labels = list(set([p["name"] for p in platforms]))
labels.sort()
label_to_index = {label: i for i, label in enumerate(labels)}

# Create Sankey diagram components
link_sources = [label_to_index[link["source"]] for link in links]
link_targets = [label_to_index[link["target"]] for link in links]
link_values = [link["value"] for link in links]

# ----------

def to_month_serial(month):
    return int(month[:4])*12+int(month[5:]) if month and len(month) == 7 else 0


def nodify(nodes, node_labels, links):

    months = list(set([n["start"] for n in nodes]).union(
        [n["end"] for n in nodes]))
    months.sort()
    max_distance = to_month_serial(months[-1])-to_month_serial(months[0])
    lanes = list(set([n["group"] for n in nodes]))
    lanes.sort()

    groups_max = {}
    for l in links:
        n = [n for n in nodes if n["name"] == l["source"]][0]
        if n["group"] in groups_max:
            if l["value"] > groups_max[n["group"]]:
                groups_max[n["group"]] = l["value"]
        else:
            groups_max[n["group"]] = l["value"]
    
    groups_max_total = sum(groups_max.values())

    group_y = 0.001
    groups_y = {}
    for lane in lanes:
        groups_y[lane] = group_y
        group_y += groups_max[lane] / groups_max_total

    nodes_y = {}
    nodes_x = {}
    for n in nodes:
        y = groups_y[n["group"]]
        nodes_y[n["name"]] = y if y > 0 else 0.001
        x_distance = to_month_serial(n["start"])-to_month_serial(months[0])
        x = x_distance / max_distance
        nodes_x[n["name"]] = x if x > 0 else 0.001

    x_values = [nodes_x[n] for n in node_labels]
    y_values = [nodes_y[n] for n in node_labels]

    return x_values, y_values

# ----------

# def get_groups(nodes, label_to_index):
#     groups = {}
#     for n in nodes:
#         if n["group"] in groups:
#             groups[n["group"]].append(label_to_index[n["name"]])
#         else:
#             groups[n["group"]] = [label_to_index[n["name"]]]
    
#     return [v for i, (k, v) in enumerate(groups.items())]

nodified = nodify(platforms, labels, links)
# groups = get_groups(platforms, label_to_index)

# Plotting the Sankey diagram
# https://plotly.com/python/reference/sankey/
fig = go.Figure(data=[go.Sankey(
    arrangement='snap',
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        x=nodified[0],
        y=nodified[1]
    ),
    link=dict(
        source=link_sources,
        target=link_targets,
        value=link_values
    )
)])

fig.update_layout(
    title="Technology Platform Evolution",
    font=dict(size = 10, color = 'white'),
    plot_bgcolor='black',
    paper_bgcolor='black'
)

fig.show()
