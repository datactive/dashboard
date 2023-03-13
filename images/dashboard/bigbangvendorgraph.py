import warnings
import networkx as nx

__all__ = ["messages_to_interaction_graph"]


def clean_from(m_from):
    """
    Return a person's name extracted from 'From' field
    of email, based on heuristics.
    """

    cleaned = m_from

    try:
        if "(" in m_from:
            cleaned = m_from[m_from.index("(") + 1 : m_from.rindex(")")]
        elif "<" in m_from:
            # if m_from.index("<") > -1:
            cleaned = m_from[0 : m_from.index("<") - 1]

    except ValueError:
        warnings.warn("%s is hard to clean" % (m_from))

    cleaned = cleaned.strip('"')

    return cleaned


def messages_to_interaction_graph(messages, verbose=False, clean=True):
    """Return a interactable graph given messages."""

    IG = nx.DiGraph()

    from_dict = {}
    sender_counts = {}
    reply_counts = {}

    # if not isinstance(messages, pandas.core.frame.DataFrame):
    #     # df = process.messages_to_dataframe(messages)
    #     pass
    # else:
    df = messages

    for m in df.iterrows():
        m_from = m[1]["From"]
        if clean:
            m_from = clean_from(m_from)

        from_dict[m[0]] = m_from
        sender_counts[m_from] = sender_counts.get(m_from, 0) + 1
        # the necessity of this initialization step may be dubious
        reply_counts[m_from] = reply_counts.get(m_from, {})
        IG.add_node(m_from)

    for sender, count in list(sender_counts.items()):
        IG.nodes[sender]["sent"] = count

    replies = [m for m in df.iterrows() if m[1]["In-Reply-To"] is not None]

    for m in replies:
        m_from = m[1]["From"]

        if clean:
            m_from = clean_from(m_from)

        reply_to_mid = m[1]["In-Reply-To"]

        if reply_to_mid in from_dict:
            m_to = from_dict[reply_to_mid]
            reply_counts[m_from][m_to] = reply_counts[m_from].get(m_to, 0) + 1
        else:
            if verbose:
                print(reply_to_mid + " not in archive")

    for m_from, edges in list(reply_counts.items()):
        for m_to, count in list(edges.items()):
            IG.add_edge(m_from, m_to, weight=count)

    return IG
