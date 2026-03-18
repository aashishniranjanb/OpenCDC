"""OpenCDC checker.

This module provides basic clock-domain crossing (CDC) analysis over a Yosys JSON
netlist.

The initial implementation is intentionally small: it identifies nets driven by a
flip-flop in one clock domain and sampled by a flip-flop in another domain.
"""

from typing import Dict, List, Optional, Tuple

from .parser import get_cells, get_flip_flops, load_netlist


def _ff_domain(ff: dict) -> Optional[str]:
    """Return the clock net name for a flip-flop or None if unavailable."""
    clk_nets = ff.get("connections", {}).get("CLK", [])
    if not clk_nets:
        return None
    # In Yosys JSON, CLK connection is a list of nets; we take the first
    return clk_nets[0]


def find_cross_domain_nets(netlist: dict) -> List[dict]:
    """Find nets driven by an FF in one domain and sampled by an FF in another.

    Returns a list of dicts describing each crossing:
      - net: the net name
      - driver_ff: name of the source FF
      - driver_domain: clock net driving the source FF
      - sink_ff: name of the destination FF
      - sink_domain: clock net driving the destination FF
    """

    ffs = get_flip_flops(netlist)

    # Map net -> (ff_name, domain) for nets that are driven by an FF's Q output.
    drivers: Dict[str, Tuple[str, Optional[str]]] = {}
    # Map net -> list of (ff_name, domain) for nets that are sampled on an FF's D input.
    sinks: Dict[str, List[Tuple[str, Optional[str]]]] = {}

    for ff in ffs:
        domain = _ff_domain(ff)
        conns = ff.get("connections", {})

        # Q drives the net
        for net in conns.get("Q", []):
            drivers[net] = (ff["name"], domain)

        # D reads the net
        for net in conns.get("D", []):
            sinks.setdefault(net, []).append((ff["name"], domain))

    crossings: List[dict] = []
    for net, (driver_ff, driver_dom) in drivers.items():
        for sink_ff, sink_dom in sinks.get(net, []):
            if driver_dom is None or sink_dom is None:
                continue
            if driver_dom != sink_dom:
                crossings.append(
                    {
                        "net": net,
                        "driver_ff": driver_ff,
                        "driver_domain": driver_dom,
                        "sink_ff": sink_ff,
                        "sink_domain": sink_dom,
                    }
                )

    return crossings


def check_netlist_file(path: str) -> List[dict]:
    """Load a netlist file and return any cross-domain nets detected."""
    nl = load_netlist(path)
    return find_cross_domain_nets(nl)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m opencdc.checker <yosys-json>")
        raise SystemExit(1)

    crossings = check_netlist_file(sys.argv[1])
    if not crossings:
        print("No cross-domain net crossings detected.")
        raise SystemExit(0)

    print(f"Detected {len(crossings)} potential CDC crossing(s):")
    for c in crossings:
        print(
            f" - net {c['net']} from {c['driver_ff']}({c['driver_domain']}) "
            f"--> {c['sink_ff']}({c['sink_domain']})"
        )
    raise SystemExit(1)
