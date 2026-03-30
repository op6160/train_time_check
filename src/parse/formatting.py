def train_rate_time_formatting(train_rate_time_str):
    """
    date: 2026/03/14
    now version: n分遅れ or 61分以上

    Args:
        train_rate_time_str (str): a train rate time string

    Returns:
        str: formatted train rate time
    """
    if train_rate_time_str == "61分以上":
        return "61+"
    
    time_number_only = train_rate_time_str.split("分")[0]
    return time_number_only


def destination_formatting(destination):
    """
    date: 2026/03/14
    Args:
        destination (str): train destination

    Returns:
        str: formatted destination
    """
    return destination