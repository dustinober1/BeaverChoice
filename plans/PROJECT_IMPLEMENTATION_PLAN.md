# The Beaver's Choice Paper Company - Multi-Agent System Implementation Plan

## 1. Executive Summary & Context

The Beaver's Choice Paper Company (formerly referenced in starter assets as Munder Difflin) requires a modernized multi-agent sales, inventory, and quoting system. The company is currently losing sales due to delayed response times and inadequate inventory visibility.

This project delivers an autonomous, modular, text-based multi-agent system (utilizing **4 agents**, well within the 5-agent hard constraint) that processes inbound customer quote inquiries, checks warehouse stock levels, calculates supplier restock lead times, queries past pricing patterns to provide competitive bulk discounts, finalizes sales transactions, and produces clear, customer-friendly communications while strictly concealing confidential internal metrics.

---

## 2. Multi-Agent Architecture & Design

### Framework: `smolagents`
We select **`smolagents`** (by Hugging Face) for orchestration:
- Direct support for specialized worker agents managed by a master orchestrator (`managed_agents`).
- Seamless integration with OpenAI-compatible endpoints (`OpenAIServerModel`) matching Udacity's proxy configuration (`https://openai.vocareum.com/v1`).
- Native Python function tooling via `@tool` decorators.
- High reliability, concise code structure, and strict adherence to project guidelines.

```
                           +--------------------------------+
                           |        Customer Inquiry        |
                           +---------------+----------------+
                                           |
                                           v
                           +--------------------------------+
                           |       Orchestrator Agent       |
                           |  (Inquiry intake, delegation,  |
                           |   customer-facing responses)   |
                           +-------+-------+--------+-------+
                                   |       |        |
                    +--------------+       |        +---------------+
                    |                      |                        |
                    v                      v                        v
         +--------------------+  +--------------------+  +--------------------+
         |  Inventory Manager |  |    Quoting Agent   |  |    Sales Closer    |
         |       Agent        |  |                    |  |       Agent        |
         +--------------------+  +--------------------+  +--------------------+
         | - Stock verification| | - Historical quote |  | - Sales transaction|
         | - Supplier lead    |  |   lookup           |  |   execution        |
         |   time calculation |  | - Pricing & bulk   |  | - Ledger & cash    |
         | - Restock orders   |  |   discounting      |  |   balance check    |
         +--------------------+  +--------------------+  +--------------------+
```

### Agent Roles & Specifications

| Agent | Core Responsibilities | Inputs | Outputs |
| :--- | :--- | :--- | :--- |
| **Orchestrator Agent** | Parses customer requests, dates, and deadlines. Sequentially coordinates with Inventory Manager, Quoter, and Sales Closer. Synthesizes a transparent, polite customer response. | Natural language customer inquiry with date | Final customer-facing response, confirmation, or rejection with justification |
| **Inventory Manager Agent** | Checks on-hand quantities, verifies whether supplier restock is needed, calculates supplier arrival dates against customer delivery deadlines, and initiates supplier orders if feasible and cash allows. | Requested items, quantities, inquiry date, needed delivery date | Stock status (`IN_STOCK`, `CAN_RESTOCK_IN_TIME`, `CANNOT_MEET_DEADLINE`, `OUT_OF_STOCK`), available delivery date |
| **Quoting Agent** | Evaluates requested items, consults historical quotes for comparable orders, computes base prices from catalog, and applies tiered volume discounts. | Confirmed item list, quantities, customer type, event type | Itemized quote breakdown, applied discount percentage, total quote price |
| **Sales Closer Agent** | Records official sales transactions into the `transactions` table upon confirmed quote and availability. Verifies database consistency and returns receipt details. | Item name, sold quantity, agreed total price, transaction date | Transaction ID, confirmation status, updated financial metrics |

---

## 3. Tool Mapping & 100% Starter Function Coverage

The rubric mandates that **all 7 starter helper functions** must be actively utilized in at least one agent tool definition. Below is the mapping:

| Helper Function from `project_starter.py` | Assigned Agent | Tool Name & Implementation Purpose |
| :--- | :--- | :--- |
| `get_stock_level(item_name, as_of_date)` | **Inventory Manager** | `tool_check_stock_level`: Queries exact current inventory for a specific paper item as of the inquiry date. |
| `get_all_inventory(as_of_date)` | **Inventory Manager** | `tool_get_all_inventory`: Obtains full warehouse inventory snapshot to verify multi-item inquiries. |
| `get_supplier_delivery_date(input_date_str, quantity)` | **Inventory Manager** | `tool_get_supplier_lead_time`: Calculates estimated restocking arrival date based on order volume. |
| `get_cash_balance(as_of_date)` | **Inventory Manager** & **Sales Closer** | `tool_check_cash_balance`: Verifies liquidity before placing supplier restock orders and checks post-sale cash. |
| `generate_financial_report(as_of_date)` | **Inventory Manager** / **Orchestrator** | `tool_generate_financial_report`: Provides executive summary of assets, cash, and top-selling products. |
| `search_quote_history(search_terms, limit)` | **Quoting Agent** | `tool_search_quote_history`: Searches historical customer requests and quote explanations for competitive pricing benchmarks. |
| `create_transaction(item_name, transaction_type, quantity, price, date)` | **Sales Closer** & **Inventory Manager** | `tool_create_transaction`: Executes `'sales'` transactions for customer purchases and `'stock_orders'` for supplier restocking. |

---

## 4. Item Catalog Matching Strategy

In `quote_requests_sample.csv`, customer prompts use natural language (e.g., "500 sheets of A4 glossy paper", "300 poster boards (24\" x 36\")", "200 rolls of decorative washi tape"). 

The database catalog contains standardized item names (e.g., `Glossy paper`, `Large poster paper (24x36 inches)`, `Decorative adhesive tape (washi tape)`).

To ensure zero failed transactions due to item naming discrepancies, we implement an intelligent catalog resolver:
1. Exact lowercase normalization and alias lookup.
2. Keyword matching against `paper_supplies` item catalog.
3. Fallback to closest match with high similarity score.

---

## 5. Decision Rules: Order Fulfillment vs. Rejection

The project rubric strictly requires that:
1. **At least three orders are successfully fulfilled** (resulting in cash balance changes).
2. **At least one order is actively rejected**, providing a clear, honest reason to the customer.

### Rules for Acceptance & Fulfillment:
- Requested items are in stock, OR
- Supplier can deliver the required quantity on or before the customer's required delivery date (`delivery_date <= customer_deadline`).
- Company has adequate cash balance to place any necessary supplier restock order.

### Rules for Rejection:
- **Timeline Impossibility**: Customer requested deadline is earlier than supplier lead time (e.g. customer needs 10,000 units in 3 days, but supplier delivery requires 7 days).
- **Unavailable Catalog Items**: Customer requests items not carried in the paper catalog (e.g., balloons, party noisemakers).
- **Insufficient Liquidity**: Company cannot afford bulk restocking.

### Customer Output Guardrails:
- Must explain the outcome clearly (itemized quote and delivery date for fulfilled orders; clear reason such as supplier lead time conflict for rejected orders).
- Must NOT leak confidential margins, internal wholesale costs, or database internal IDs.

---

## 6. Execution & Implementation Steps

### Phase 1: Environment & Dependency Setup
- Create Python 3.11 virtual environment in `.venv` via `uv`.
- Install `smolagents`, `openai`, `pandas`, `SQLAlchemy`, `python-dotenv`, `matplotlib`.
- Configure `.env` with `OPENAI_API_KEY` and `OPENAI_BASE_URL`.

### Phase 2: Workflow Diagram Creation
- Create `generate_diagram.py` using `matplotlib` / `graphviz` to render a polished, high-resolution `workflow_diagram.png`.
- Highlight all 4 agents, data flows, and tool mappings with exact helper function references.

### Phase 3: Single-File Multi-Agent Implementation (`project_starter.py`)
- Fix starter bug in `init_database()` signature default argument.
- Define tools decorated with `@tool` exposing all 7 starter helper functions.
- Build item resolution utility.
- Initialize `InventoryManager`, `QuotingAgent`, `SalesCloser`, and `OrchestratorAgent`.
- Wire `run_test_scenarios()` to execute all 20 rows from `quote_requests_sample.csv` and export `test_results.csv`.

### Phase 4: System Testing & Evaluation
- Execute `python project_starter.py`.
- Verify generated `test_results.csv`:
  - Verify $\ge 3$ fulfilled orders modifying cash.
  - Verify $\ge 1$ rejected order with clear reason.
  - Validate final financial report and state tracking.

### Phase 5: Documentation & Reflection Report
- Author `project_report.md` fulfilling all rubric requirements:
  - Architecture breakdown and workflow diagram discussion.
  - Performance evaluation of `test_results.csv`.
  - Two distinct, concrete suggestions for future system improvements.
