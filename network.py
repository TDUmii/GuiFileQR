"""Tìm địa chỉ IPv4 của máy tính trên mạng nội bộ."""

import ipaddress
import socket


PRIVATE_LANS = tuple(
    ipaddress.IPv4Network(network)
    for network in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
)


def local_addresses():
    """Ưu tiên địa chỉ của mạng nội bộ, kể cả khi máy đang kết nối VPN."""
    addresses = set()
    try:
        results = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET, socket.SOCK_STREAM)
        addresses.update(ipaddress.IPv4Address(result[4][0]) for result in results)
    except OSError:
        pass

    preferred = None
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            # UDP chỉ xác định tuyến đường, không gửi dữ liệu ra mạng.
            probe.connect(("192.0.2.1", 80))
            preferred = ipaddress.IPv4Address(probe.getsockname()[0])
            addresses.add(preferred)
        except OSError:
            pass

    def order(address):
        return (
            not any(address in network for network in PRIVATE_LANS),
            address != preferred,
            address,
        )

    usable = (address for address in addresses if not (
        address.is_loopback or address.is_link_local or address.is_unspecified
    ))
    return [str(address) for address in sorted(usable, key=order)]
