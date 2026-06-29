"""Always-on logging layer. Runs last; mutates nothing, blocks nothing."""

from sys import stderr

from mitmproxy.dns import DNSFlow
from mitmproxy.http import HTTPFlow
from mitmproxy.tcp import TCPFlow
from mitmproxy.udp import UDPFlow


def request(flow: HTTPFlow):
    print(
        f"{flow.request.method} {flow.request.pretty_url}",
        file=stderr,
    )


def response(flow: HTTPFlow):
    print(
        f"{flow.response.status_code} {flow.response.headers.get('Content-Type')}",
        file=stderr,
    )


def udp_message(flow: UDPFlow):
    _l4_message("UDP", flow)


def tcp_message(flow: TCPFlow):
    _l4_message("TCP", flow)


def _l4_message(protocol: str, flow: UDPFlow | TCPFlow):
    message = flow.messages[-1]
    arrow = "→" if message.from_client else "←"
    print(
        f"{protocol} {arrow} {flow.client_conn.peername} {len(message.content)}",
        file=stderr,
    )


def dns_request(flow: DNSFlow):
    pass # TODO: log


def dns_response(flow: DNSFlow):
    pass # TODO: log
