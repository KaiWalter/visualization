import plotly.graph_objects as go

# Define nodes
nodes = [
    {"name": "Functions Consumption Plan", "group": "compute",
     "start": "2016-10", "end": "2018-06"},
    {"name": "Service Fabric Stateful Applications",
     "group": "compute", "start": "2017-01", "end": "2018-06"},
    {"name": "Functions in Service Fabric Containers",
     "group": "compute", "start": "2018-06", "end": "2023-03"},
    {"name": "Function Containers on Container Apps",
     "group": "compute", "start": "2023-03", "end": None},
    {"name": "Service Bus", "group": "messaging", "start": "2016-10", "end": None},
    {"name": "API Management", "group": "gateway", "start": "2016-10", "end": None},
    {"name": "Key Vault", "group": "gateway", "start": "2023-09", "end": None}
]

# Define links
links = [
    {"source": "Functions Consumption Plan",
        "target": "Functions in Service Fabric Containers", "value": 1, "date": "2018-06"},
    {"source": "Service Fabric Stateful Applications",
        "target": "Functions in Service Fabric Containers", "value": 1, "date": "2018-06"},
    {"source": "Functions in Service Fabric Containers",
        "target": "Function Containers on Container Apps", "value": 2, "date": "2023-03"}
]

current_month = "2024-06"

# ---------- helper functions


def to_month_serial(month):
    """Convert from YYYY-MM format to a serial month number for chart calculation.
    """
    return int(month[:4])*12+int(month[5:]) if month and len(month) == 7 else 0


def nodify(nodes, node_labels):

    months = list(set([n["start"] for n in nodes]).union(
        [n["end"] for n in nodes]))
    months.sort()
    month_span = to_month_serial(months[-1])-to_month_serial(months[0])+1

    groups = list(set([n["group"] for n in nodes]))
    groups.sort()

    groups_max = {}
    for n in (n for n in nodes if n["isTarget"] == False):
        if n["group"] in groups_max:
            groups_max[n["group"]] += 2.2
        else:
            groups_max[n["group"]] = 1.0

    groups_max_total = sum(groups_max.values())

    group_y = 0.001
    groups_y = {}
    for group in groups:
        groups_y[group] = group_y
        group_y += groups_max[group] / groups_max_total

    nodes_y = {}
    nodes_x = {}
    for n in nodes:
        y = groups_y[n["group"]]
        nodes_y[n["name"]] = y if y > 0 else 0.001
        x_distance = to_month_serial(n["start"])-to_month_serial(months[0])
        x = x_distance / month_span
        nodes_x[n["name"]] = x if x > 0 else 0.001

    x_values = [nodes_x[n] for n in node_labels]
    y_values = [nodes_y[n] for n in node_labels]

    return x_values, y_values


def add_closing_nodes(nodes, current_month):
    """ Add virtual nodes representing prolonging last state to current month
    Indicate source and target links in nodes
    """

    closing_nodes = []

    for current_node in nodes:
        if not current_node["end"]:
            current_node["end"] = current_month
            closing_node = current_node.copy()
            closing_node["start"] = current_month
            closing_node["end"] = current_month
            closing_node["name"] = closing_node["name"] + " (current)"
            closing_node["isSource"] = False
            closing_node["isTarget"] = True
            closing_nodes.append(closing_node)
            closing_value = 1
            for l in links:
                if l["target"] == current_node["name"] and l["date"] == current_node["start"]:
                    closing_value = l["value"]
                    break
            closing_link = {
                "source": current_node["name"],
                "target": closing_node["name"],
                "value": closing_value,
            }
            links.append(closing_link)

        current_node["isSource"] = False
        current_node["isTarget"] = False

        for l in links:
            if l["source"] == current_node["name"]:
                current_node["isSource"] = True
            if l["target"] == current_node["name"]:
                current_node["isTarget"] = True

    nodes.extend(closing_nodes)

    return nodes

# ----------


nodes = add_closing_nodes(nodes, current_month)

node_labels = list(set([p["name"] for p in nodes]))
node_labels.sort()
label_to_index = {label: i for i, label in enumerate(node_labels)}

# Create Sankey diagram components
link_sources = [label_to_index[link["source"]] for link in links]
link_targets = [label_to_index[link["target"]] for link in links]
link_values = [link["value"] for link in links]

nodified = nodify(nodes, node_labels)

# Plotting the Sankey diagram
# https://plotly.com/python/reference/sankey/
fig = go.Figure(data=[go.Sankey(
    arrangement='snap',
    node=dict(
        pad=5,
        thickness=10,
        line=dict(color="black", width=0),
        label=node_labels,
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
    font=dict(size=10, color='white'),
    plot_bgcolor='black',
    paper_bgcolor='black'
)

fig.show()
