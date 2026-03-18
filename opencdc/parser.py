"""opencdc.parser
Reads Yosys-generated JSON netlist and returns structured data.
"""
import json


def load_netlist(json_path: str) -> dict:
    """Load a Yosys JSON netlist from disk."""
    with open(json_path) as f:
        return json.load(f)


def get_cells(netlist: dict) -> dict:
    """Return all cells from the top module."""
    modules = netlist.get("modules", {})
    if not modules:
        raise ValueError("No modules found in netlist")
    top = list(modules.values())[0]
    return top.get("cells", {})


def get_flip_flops(netlist: dict) -> list:
    """Extract all flip-flop cells from the netlist."""
    cells = get_cells(netlist)
    ff_types = {"$dff", "$dffe", "$sdff", "$adff", "$fdre", "$fdce"}
    ffs = []
    for name, cell in cells.items():
        if cell.get("type", "").lower() in ff_types:
            ffs.append({"name": name, "type": cell["type"],
                        "connections": cell.get("connections", {})})
    return ffs


if __name__ == "__main__":
    import sys
    nl = load_netlist(sys.argv[1])
    ffs = get_flip_flops(nl)
    print(f"Found {len(ffs)} flip-flops:")
    for ff in ffs:
        print(f"  {ff['name']} ({ff['type']})")
