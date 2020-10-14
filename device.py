def get_name(device):
    return device.get('name', '')


def get_route_manager_name(device):
    return device.get('rmname', '')


def get_route_pos(device):
    return device.get('routePos', '?')


def get_route_max(device):
    return device.get('routeMax', '?')


def get_last_updated(device):
    return device.get('lastProtoDateTime', '')
