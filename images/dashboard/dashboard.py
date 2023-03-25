import panel as pn

pn.extension(sizing_mode="stretch_width")

import hvplot.pandas
import hvplot.networkx as hvnx
from datetime import date
import bigbangvendorgraph as graph
import networkx as nx
import matplotlib.pyplot as plt
import pickle

with open("preload_list.pickle", "rb") as handle:
    preloads = pickle.load(handle)


def load_data():
    with open("preload_archive.pickle", "rb") as handle:
        preload_archive = pickle.load(handle)
    return preload_archive


preload_archive = pn.state.as_cached("data", load_data)


archive_select_widget = pn.widgets.AutocompleteInput(
    name="Select the working group(s) you are interested in",
    options=list(preloads),
    value="httpbisa",
    case_sensitive=False,
    placeholder="Select an archive",
)


@pn.depends(archive_select=archive_select_widget)
def plot_daily_activity(archive_select):
    # print(archive_select)
    archive = preload_archive[archive_select]
    daily_activity = archive.get_activity()
    daily_activity_sum = daily_activity.sum(1)
    daily_activity_sum.index = daily_activity_sum.index.map(date.fromordinal)
    daily_activity_sum = daily_activity_sum.rename("Daily Activity")
    window = 100
    return daily_activity_sum.rolling(window).mean().dropna(how="all").hvplot()


@pn.depends(archive_select=archive_select_widget)
def get_top_senders(archive_select):
    archive = preload_archive[archive_select]
    top_senders = archive.get_activity().sum().sort_values(ascending=False)[:15]
    return top_senders.rename("Number of Emails")


@pn.depends(archive_select=archive_select_widget)
def plot_interactions(archive_select):
    archive = preload_archive[archive_select]
    df = archive.data.copy()
    ig = graph.messages_to_interaction_graph(df)
    threshold = 0.15
    max_sent = max([data["sent"] for name, data in ig.nodes(data=True)])
    ig.remove_nodes_from(
        [
            name
            for name, data in ig.nodes(data=True)
            if data["sent"] < threshold * max_sent
        ]
    )

    edges, weights = zip(*nx.get_edge_attributes(ig, "weight").items())
    weights_multiplier = 50.0 / max(weights)
    weights = [w * weights_multiplier for w in weights]

    pos = nx.layout.kamada_kawai_layout(ig)

    node_size_multiplier = 1000 / max(
        [data["sent"] for name, data in ig.nodes(data=True)]
    )
    node_size = [
        data["sent"] * node_size_multiplier for name, data in ig.nodes(data=True)
    ]

    return hvnx.draw(
        ig,
        pos,
        node_size=node_size,
        node_color="#CCCCFF",
        font_size=12,
        edge_width=weights,
        edge_color=weights,
        edge_cmap=plt.cm.viridis,
    )


archive_select_widget_boxed = pn.Column(
    pn.pane.Markdown(
        "### Welcome to the Standards and Governance Dashboard

With this dashboard we help you to analyze publicly available data about standard-setting. Currently we are allowing you to analyze data from mailinglist conversations and other data to get deeper insight into standard-setting processes.

You can also run these analyses, and many more, by locally installing [BigBang](https://github.com/datactive/bigbang)."
    ),
    archive_select_widget,
)

plot_daily_activity_boxed = pn.Column(
    pn.pane.Markdown(
        "#### In this graph you see the activity over the lifespan of the mailinglist. From this you can understand for how long the Working Group exists and how active it has been, and whether there have been any peeks in activity."
    ),
    plot_daily_activity,
)

get_top_senders_boxed = pn.Column(
    pn.pane.Markdown(
        "#### This table shows the information of the top senders to the mailinglist, such as their name, their email address, and the amount of email they have sent."
    ),
    get_top_senders,
)

plot_interactions_boxed = pn.Column(
    pn.pane.Markdown(
        "#### This graph shows the interaction among the post posters to the working group mailinglist. It allows you to understand who sents the most mails, and to whom they are responding. The bigger the size of the node, the more emails they have sent. If you click on the node, you will see the emailaddress of the sender and the amount of emails they have sent"
    ),
    plot_interactions,
)


privacy_statement = """
<a href=""> Privacy Statement </a>
"""
template = pn.template.FastListTemplate(
    site="BigBang", title="Mailing Lists Dashboard", sidebar_footer=privacy_statement
)

side_md = pn.pane.Markdown(
    """

### Welcome to the BigBang Dashboard

BigBang is an open source toolkit
for studying processes of open collaboration and deliberation
via analysis of the communications records. You can analyse different
mailing lists with the BigBang project and look at daily
activity, interaction graphs and the top senders.

------------
""",
    width=500,
)


template.sidebar.append(side_md)

template.main.append(
    pn.Column(
        archive_select_widget_boxed,
        pn.Row(plot_daily_activity_boxed, plot_interactions_boxed),
        get_top_senders_boxed,
    )
)

template.servable()
