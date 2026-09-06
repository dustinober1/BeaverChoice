"""
Generate an executive-grade workflow diagram for The Beaver's Choice Paper Company Multi-Agent System.
Visualizes agent responsibilities, orchestration, tool bindings, and data flow.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_rounded_box(ax, xy, width, height, title, subtitle="", items=None, box_color="#EBF5FB", edge_color="#2980B9", title_color="#1B4F72"):
    x, y = xy
    # Box
    rect = patches.FancyBboxPatch(
        (x, y - height), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=2, edgecolor=edge_color, facecolor=box_color, zorder=2
    )
    ax.add_patch(rect)
    
    # Title bar
    title_rect = patches.FancyBboxPatch(
        (x, y - 0.05), width, 0.05,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        linewidth=1, edgecolor=edge_color, facecolor=edge_color, zorder=3
    )
    ax.add_patch(title_rect)
    ax.text(x + width/2, y - 0.027, title, ha="center", va="center", color="white", weight="bold", fontsize=11, zorder=4)
    
    curr_y = y - 0.075
    if subtitle:
        ax.text(x + 0.02, curr_y, subtitle, ha="left", va="top", color=title_color, weight="bold", fontsize=9, zorder=4)
        curr_y -= 0.035
        
    if items:
        for it in items:
            ax.text(x + 0.02, curr_y, it, ha="left", va="top", color="#2C3E50", fontsize=8, zorder=4)
            curr_y -= 0.028

def create_workflow_diagram():
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#F8F9F9")

    # Header / Title Banner
    header_box = patches.FancyBboxPatch(
        (0.04, 0.92), 0.92, 0.06,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        linewidth=1.5, edgecolor="#1A5276", facecolor="#1A5276", zorder=2
    )
    ax.add_patch(header_box)
    ax.text(0.5, 0.95, "THE BEAVER'S CHOICE PAPER COMPANY: MULTI-AGENT SALES & ORDER WORKFLOW",
            ha="center", va="center", color="white", weight="bold", fontsize=14, zorder=4)
    ax.text(0.5, 0.93, "Autonomous 4-Agent Architecture with 100% Starter Helper Function Tool Coverage (smolagents)",
            ha="center", va="center", color="#D4E6F1", style="italic", fontsize=9, zorder=4)

    # 1. Customer Inquiry (Input)
    draw_rounded_box(ax, (0.04, 0.88), 0.26, 0.12, "CUSTOMER INQUIRY", 
                     "Natural Language Input",
                     ["• Items & Quantities requested",
                      "• Request Date & Required Delivery Date",
                      "• Event context (e.g. conference, party)"],
                     box_color="#FEF9E7", edge_color="#D4AC0D", title_color="#7D6608")

    # 2. Orchestrator Agent
    draw_rounded_box(ax, (0.36, 0.88), 0.38, 0.15, "ORCHESTRATOR AGENT (Master Coordinator)",
                     "Core Responsibilities:",
                     ["• Ingests customer inquiry & extracts items/deadlines",
                      "• Sequentially coordinates worker agents (Inv -> Quote -> Sales)",
                      "• Evaluates fulfillment feasibility vs. rejection constraints",
                      "• Synthesizes polite, transparent customer response (zero PII/margin leaks)",
                      "• High-Level Monitoring: generate_financial_report()"],
                     box_color="#E8F8F5", edge_color="#117864", title_color="#0E6251")

    # 3. Customer Response (Output)
    draw_rounded_box(ax, (0.78, 0.88), 0.18, 0.12, "FINAL RESPONSE",
                     "Customer Facing Output",
                     ["• Confirmed Order & Receipt, OR",
                      "• Transparent Rejection Reason",
                      "• Delivery date commitment",
                      "• No internal margin disclosures"],
                     box_color="#EBF5FB", edge_color="#2874A6", title_color="#1B4F72")

    # Arrows for top level
    # Customer -> Orchestrator
    ax.annotate("", xy=(0.36, 0.82), xytext=(0.30, 0.82),
                arrowprops=dict(facecolor="#34495E", edgecolor="#34495E", width=1.5, headwidth=6, shrink=0.05))
    ax.text(0.33, 0.835, "Inquiry Data", ha="center", fontsize=8, weight="bold", color="#34495E")

    # Orchestrator -> Customer Response
    ax.annotate("", xy=(0.78, 0.82), xytext=(0.74, 0.82),
                arrowprops=dict(facecolor="#117864", edgecolor="#117864", width=1.5, headwidth=6, shrink=0.05))
    ax.text(0.76, 0.835, "Final Quote / Rejection", ha="center", fontsize=8, weight="bold", color="#117864")

    # 4. Worker Agent Layer Container
    worker_box = patches.FancyBboxPatch(
        (0.04, 0.05), 0.92, 0.64,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.5, linestyle="--", edgecolor="#7F8C8D", facecolor="#FFFFFF", zorder=1
    )
    ax.add_patch(worker_box)
    ax.text(0.5, 0.67, "SPECIALIZED WORKER AGENTS LAYER (Max 5 Agents Constraint: 3 Worker Agents + 1 Orchestrator)",
            ha="center", va="center", color="#7F8C8D", weight="bold", fontsize=10)

    # Worker 1: Inventory Manager Agent
    draw_rounded_box(ax, (0.06, 0.64), 0.28, 0.56, "INVENTORY MANAGER AGENT",
                     "Responsibilities: Stock Verification & Restock Lead Times",
                     ["[Data In]: Item list, quantities, request & delivery dates",
                      "[Data Out]: Stock availability, supplier ETA, reorder status",
                      "",
                      "--- INTEGRATED STARTER TOOLS & FUNCTIONS ---",
                      "1. tool_get_stock_level(item_name, as_of_date)",
                      "   -> Uses: get_stock_level()",
                      "   Calculates current net warehouse stock.",
                      "",
                      "2. tool_get_all_inventory(as_of_date)",
                      "   -> Uses: get_all_inventory()",
                      "   Snapshot of entire active stock inventory.",
                      "",
                      "3. tool_get_supplier_delivery_date(date, qty)",
                      "   -> Uses: get_supplier_delivery_date()",
                      "   Evaluates supplier lead-time schedule (0-7 days).",
                      "",
                      "4. tool_check_cash_balance(as_of_date)",
                      "   -> Uses: get_cash_balance()",
                      "   Confirms company liquidity before restock order.",
                      "",
                      "5. tool_order_supplier_restock(item, qty, price, date)",
                      "   -> Uses: create_transaction('stock_orders')",
                      "   Places supplier restock transaction if feasible."],
                     box_color="#FEF5E7", edge_color="#D35400", title_color="#A04000")

    # Worker 2: Quoting Agent
    draw_rounded_box(ax, (0.37, 0.64), 0.27, 0.56, "QUOTING AGENT",
                     "Responsibilities: Pricing & Volume Discounts",
                     ["[Data In]: Validated items, volumes, customer/event type",
                      "[Data Out]: Itemized quote breakdown, discounts, total",
                      "",
                      "--- INTEGRATED STARTER TOOLS & FUNCTIONS ---",
                      "1. tool_search_quote_history(search_terms, limit)",
                      "   -> Uses: search_quote_history()",
                      "   Analyzes historical quotes & explanations for",
                      "   comparable orders and benchmark market rates.",
                      "",
                      "2. tool_calculate_quote_price(item, qty, job, event)",
                      "   Applies catalog unit prices from paper_supplies",
                      "   Applies transparent tiered bulk discounts:",
                      "   • <200 units: Standard pricing (0% discount)",
                      "   • 200 - 999 units: 5% volume discount",
                      "   • 1,000 - 4,999 units: 10% volume discount",
                      "   • >=5,000 units: 15% bulk partner discount",
                      "",
                      "Produces clear itemized rationale for customer."],
                     box_color="#F4ECF7", edge_color="#7D3C98", title_color="#5B2C6F")

    # Worker 3: Sales Closer Agent
    draw_rounded_box(ax, (0.67, 0.64), 0.27, 0.56, "SALES CLOSER AGENT",
                     "Responsibilities: Transaction Execution & Settlement",
                     ["[Data In]: Quoted items, sold quantities, total price, date",
                      "[Data Out]: Transaction confirmation, receipt, updated ledger",
                      "",
                      "--- INTEGRATED STARTER TOOLS & FUNCTIONS ---",
                      "1. tool_record_sales_transaction(item, qty, price, date)",
                      "   -> Uses: create_transaction('sales')",
                      "   Writes finalized sale record into database",
                      "   Increments company cash balance and deducts stock.",
                      "",
                      "2. tool_verify_cash_ledger(as_of_date)",
                      "   -> Uses: get_cash_balance()",
                      "   Verifies cash position post-transaction.",
                      "",
                      "3. tool_generate_financial_audit(as_of_date)",
                      "   -> Uses: generate_financial_report()",
                      "   Audits financial ledger integrity and assets."],
                     box_color="#EAF2F8", edge_color="#2471A3", title_color="#1A5276")

    # Flow arrows connecting Orchestrator to Workers
    # 1. Orchestrator -> Inventory Manager
    ax.annotate("", xy=(0.20, 0.64), xytext=(0.42, 0.73),
                arrowprops=dict(facecolor="#D35400", edgecolor="#D35400", width=1.5, headwidth=6, shrink=0.02))
    ax.text(0.28, 0.70, "Step 1: Stock Check & ETA", ha="center", fontsize=8, weight="bold", color="#D35400")

    # 2. Orchestrator -> Quoting Agent
    ax.annotate("", xy=(0.50, 0.64), xytext=(0.52, 0.73),
                arrowprops=dict(facecolor="#7D3C98", edgecolor="#7D3C98", width=1.5, headwidth=6, shrink=0.02))
    ax.text(0.55, 0.69, "Step 2: Pricing & Discounts", ha="left", fontsize=8, weight="bold", color="#7D3C98")

    # 3. Orchestrator -> Sales Closer
    ax.annotate("", xy=(0.78, 0.64), xytext=(0.62, 0.73),
                arrowprops=dict(facecolor="#2471A3", edgecolor="#2471A3", width=1.5, headwidth=6, shrink=0.02))
    ax.text(0.74, 0.70, "Step 3: Book Sale", ha="center", fontsize=8, weight="bold", color="#2471A3")

    # Save diagram
    plt.tight_layout()
    plt.savefig("workflow_diagram.png", dpi=300, bbox_inches="tight")
    print("Workflow diagram successfully generated at workflow_diagram.png")

if __name__ == "__main__":
    create_workflow_diagram()
