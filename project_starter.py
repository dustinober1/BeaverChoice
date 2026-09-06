import pandas as pd
import numpy as np
import os
import time
import dotenv
import ast
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union
from sqlalchemy import create_engine, Engine

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine = db_engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = date.isoformat() if isinstance(date, datetime) else date

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        # Convert date to ISO format if it's a datetime object
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        # Query all transactions on or before the specified date
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################

from smolagents import OpenAIServerModel, ToolCallingAgent, tool

# Load environment configuration
dotenv.load_dotenv()
api_key = os.getenv("UDACITY_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1")

if not api_key:
    print("WARNING: No OpenAI API key found in environment (.env or system env)!")

# Instantiate OpenAI model via Vocareum proxy
model = OpenAIServerModel(
    model_id="gpt-4o-mini",
    api_base=api_base,
    api_key=api_key,
)

# Helper for item catalog normalization
def normalize_item_name(name: str) -> str:
    """
    Resolve natural language item names to canonical catalog names in paper_supplies.
    """
    name_clean = name.strip().lower()
    
    # 1. Exact catalog match
    for item in paper_supplies:
        if item["item_name"].lower() == name_clean:
            return item["item_name"]
            
    # 2. Known alias mappings
    aliases = {
        "a4 glossy paper": "Glossy paper",
        "glossy a4 paper": "Glossy paper",
        "a4 matte paper": "Matte paper",
        "matte a4 paper": "Matte paper",
        "a3 matte paper": "Matte paper",
        "matte a3 paper": "Matte paper",
        "a3 glossy paper": "Glossy paper",
        "heavy cardstock": "Cardstock",
        "heavyweight cardstock": "Cardstock",
        "white cardstock": "Cardstock",
        "colored cardstock": "Cardstock",
        "colorful cardstock": "Cardstock",
        "a4 white printer paper": "A4 paper",
        "a4 printer paper": "A4 paper",
        "a4 printing paper": "A4 paper",
        "a4 white paper": "A4 paper",
        "standard copy paper": "Standard copy paper",
        "standard printer paper": "Standard copy paper",
        "standard printing paper": "Standard copy paper",
        "white printer paper": "Standard copy paper",
        "printer paper": "Standard copy paper",
        "printing paper": "Standard copy paper",
        "a5 colored paper": "Colored paper",
        "a3 colored paper": "Colored paper",
        "colorful poster paper": "Poster paper",
        "poster board": "Large poster paper (24x36 inches)",
        "poster boards": "Large poster paper (24x36 inches)",
        "large poster paper": "Large poster paper (24x36 inches)",
        "washi tape": "Decorative adhesive tape (washi tape)",
        "decorative washi tape": "Decorative adhesive tape (washi tape)",
        "decorative adhesive tape": "Decorative adhesive tape (washi tape)",
        "streamers": "Party streamers",
        "party streamers": "Party streamers",
        "table napkins": "Paper napkins",
        "napkins": "Paper napkins",
        "paper napkins": "Paper napkins",
        "paper cups": "Paper cups",
        "cups": "Paper cups",
        "paper plates": "Paper plates",
        "plates": "Paper plates",
        "envelopes": "Envelopes",
        "recycled envelopes": "Envelopes",
        "kraft paper envelopes": "Envelopes",
        "folders": "Presentation folders",
        "presentation folders": "Presentation folders",
        "construction paper": "Construction paper",
        "colorful construction paper": "Construction paper",
        "recycled paper": "Recycled paper",
        "eco-friendly paper": "Eco-friendly paper",
        "notepads": "Notepads",
        "invitation cards": "Invitation cards",
        "flyers": "Flyers",
        "table covers": "Table covers",
        "banner paper": "Banner paper",
        "sticky notes": "Sticky notes",
    }
    for alias, target in aliases.items():
        if alias in name_clean:
            return target

    # 3. Substring / keyword match in paper_supplies
    for item in paper_supplies:
        it_lower = item["item_name"].lower()
        if it_lower in name_clean or name_clean in it_lower:
            return item["item_name"]
            
    # 4. Token intersection match
    tokens = set(name_clean.split())
    for item in paper_supplies:
        it_tokens = set(item["item_name"].lower().split())
        if len(tokens.intersection(it_tokens)) >= 2:
            return item["item_name"]

    return name

# ==============================================================================
# Agent Tools (Wrapping all 7 Required Starter Functions)
# ==============================================================================

@tool
def check_item_stock(item_name: str, as_of_date: str) -> str:
    """
    Check current warehouse stock quantity for a specific paper product as of a given date.

    Args:
        item_name: Name of the paper product to check.
        as_of_date: The date for checking stock in ISO format (YYYY-MM-DD).
    """
    canonical_name = normalize_item_name(item_name)
    df = get_stock_level(canonical_name, as_of_date)
    if df.empty:
        return f"Item '{canonical_name}' has 0 units in stock as of {as_of_date}."
    stock = int(df.iloc[0]["current_stock"])
    return f"Current stock for '{canonical_name}' as of {as_of_date} is {stock} units."

@tool
def get_inventory_snapshot(as_of_date: str) -> str:
    """
    Retrieve an inventory snapshot of all products currently in stock in the warehouse.

    Args:
        as_of_date: The cutoff date in ISO format (YYYY-MM-DD).
    """
    inv = get_all_inventory(as_of_date)
    if not inv:
        return f"No inventory recorded on or before {as_of_date}."
    lines = [f"- {item}: {qty} units" for item, qty in sorted(inv.items())]
    return f"Active warehouse inventory as of {as_of_date}:\n" + "\n".join(lines)

@tool
def estimate_supplier_delivery(request_date: str, quantity: int) -> str:
    """
    Calculate estimated supplier delivery date if restocking is required for an order.
    Lead times: <=10 units: 0 days; 11-100: 1 day; 101-1000: 4 days; >1000: 7 days.

    Args:
        request_date: The order/inquiry date in ISO format (YYYY-MM-DD).
        quantity: The quantity of items required from the supplier.
    """
    est_date = get_supplier_delivery_date(request_date, quantity)
    return f"For {quantity} units ordered on {request_date}, supplier delivery arrives on {est_date}."

@tool
def check_company_cash(as_of_date: str) -> str:
    """
    Check the company cash balance as of a given date.

    Args:
        as_of_date: Cutoff date in ISO format (YYYY-MM-DD).
    """
    cash = get_cash_balance(as_of_date)
    return f"Current company cash balance as of {as_of_date} is ${cash:.2f}."

@tool
def order_supplier_restock(item_name: str, quantity: int, unit_cost: float, order_date: str) -> str:
    """
    Place a supplier replenishment order and log it into the transactions ledger.

    Args:
        item_name: Name of the item to reorder.
        quantity: Quantity of units to order.
        unit_cost: Cost per unit from the supplier.
        order_date: Date of the restock order in ISO format (YYYY-MM-DD).
    """
    canonical_name = normalize_item_name(item_name)
    total_cost = quantity * unit_cost
    cash = get_cash_balance(order_date)
    if cash < total_cost:
        return f"Restock rejected: Insufficient cash balance (${cash:.2f} available, ${total_cost:.2f} required)."
    tx_id = create_transaction(canonical_name, "stock_orders", quantity, total_cost, order_date)
    return f"Successfully created supplier stock order #{tx_id} for {quantity} units of '{canonical_name}' totaling ${total_cost:.2f} on {order_date}."

@tool
def get_company_financial_summary(as_of_date: str) -> str:
    """
    Generate a company financial report showing cash, inventory valuation, and assets.

    Args:
        as_of_date: Cutoff date in ISO format (YYYY-MM-DD).
    """
    report = generate_financial_report(as_of_date)
    return (
        f"Financial Summary as of {report['as_of_date']}:\n"
        f"Cash Balance: ${report['cash_balance']:.2f}\n"
        f"Inventory Valuation: ${report['inventory_value']:.2f}\n"
        f"Total Assets: ${report['total_assets']:.2f}"
    )

@tool
def search_historical_quotes(search_terms_str: str) -> str:
    """
    Search historical quotes for past pricing, discounts, and customer responses.

    Args:
        search_terms_str: Comma-separated search terms (e.g. 'cardstock, event, large').
    """
    terms = [t.strip() for t in search_terms_str.split(",") if t.strip()]
    quotes = search_quote_history(terms, limit=3)
    if not quotes:
        return "No historical quotes matched the search criteria."
    out = []
    for q in quotes:
        out.append(
            f"Quote (${q['total_amount']:.2f}, {q['order_date']}): {q['quote_explanation']} "
            f"(Context: {q.get('job_type', '')} / {q.get('event_type', '')})"
        )
    return "\n---\n".join(out)

@tool
def calculate_quote_and_discounts(item_name: str, quantity: int, customer_role: str = "", event_type: str = "") -> str:
    """
    Calculate customer pricing for an item with tiered volume discounts.

    Args:
        item_name: The name of the item.
        quantity: The quantity requested.
        customer_role: The role/job of the customer (e.g., 'event manager', 'teacher').
        event_type: The event context (e.g., 'ceremony', 'conference').
    """
    canonical_name = normalize_item_name(item_name)
    unit_price = None
    for it in paper_supplies:
        if it["item_name"].lower() == canonical_name.lower():
            unit_price = it["unit_price"]
            break
    if unit_price is None:
        return f"Item '{item_name}' (matched as '{canonical_name}') is not found in our catalog."
    
    # Bulk volume discounts
    if quantity >= 5000:
        discount_pct = 0.15
    elif quantity >= 1000:
        discount_pct = 0.10
    elif quantity >= 200:
        discount_pct = 0.05
    else:
        discount_pct = 0.00
        
    base_total = quantity * unit_price
    discount_amount = base_total * discount_pct
    final_total = round(base_total - discount_amount, 2)
    effective_unit_price = round(final_total / quantity, 4)
    
    return (
        f"Item: '{canonical_name}' | Qty: {quantity} | Catalog Unit Price: ${unit_price:.2f} | "
        f"Discount: {int(discount_pct * 100)}% (-${discount_amount:.2f}) | "
        f"Effective Unit Price: ${effective_unit_price:.4f} | Total Quoted Price: ${final_total:.2f}"
    )

@tool
def record_sales_transaction(item_name: str, quantity: int, total_price: float, transaction_date: str) -> str:
    """
    Finalize and record a customer sales transaction in the database.

    Args:
        item_name: Standard name of the item sold.
        quantity: Number of units sold.
        total_price: Agreed total sale price.
        transaction_date: Date of the sale in ISO format (YYYY-MM-DD).
    """
    canonical_name = normalize_item_name(item_name)
    tx_id = create_transaction(canonical_name, "sales", quantity, total_price, transaction_date)
    new_cash = get_cash_balance(transaction_date)
    return (
        f"Sales transaction #{tx_id} recorded for {quantity} units of '{canonical_name}' "
        f"at ${total_price:.2f} on {transaction_date}. Updated cash balance is ${new_cash:.2f}."
    )

# ==============================================================================
# Multi-Agent System Instantiation (4 Agents: Orchestrator + 3 Workers)
# ==============================================================================

def create_multi_agent_system():
    """
    Instantiate the multi-agent system using smolagents.
    Returns the top-level Orchestrator agent managing Inventory, Quoting, and Sales agents.
    """
    inventory_agent = ToolCallingAgent(
        tools=[
            check_item_stock,
            get_inventory_snapshot,
            estimate_supplier_delivery,
            check_company_cash,
            order_supplier_restock,
            get_company_financial_summary
        ],
        model=model,
        name="inventory_manager",
        description=(
            "Manages warehouse inventory stock, checks on-hand stock levels, calculates supplier delivery lead times, "
            "checks company cash liquidity, and places supplier restock orders if necessary."
        )
    )

    quoting_agent = ToolCallingAgent(
        tools=[
            search_historical_quotes,
            calculate_quote_and_discounts
        ],
        model=model,
        name="quoting_agent",
        description=(
            "Calculates competitive pricing and volume discounts for paper products and searches historical quotes "
            "for market rate benchmarking."
        )
    )

    sales_agent = ToolCallingAgent(
        tools=[
            record_sales_transaction,
            check_company_cash,
            get_company_financial_summary
        ],
        model=model,
        name="sales_closer",
        description=(
            "Finalizes customer sales transactions in the database, records revenue, and verifies cash ledger balance."
        )
    )

    orchestrator = ToolCallingAgent(
        tools=[
            get_company_financial_summary
        ],
        model=model,
        managed_agents=[inventory_agent, quoting_agent, sales_agent],
        name="orchestrator",
        description="Orchestrates multi-agent customer quote processing, inventory validation, quoting, and sales closing."
    )

    return orchestrator

# ==============================================================================
# Test Scenario Runner
# ==============================================================================

def run_test_scenarios():
    print("Initializing Database...")
    init_database()
    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    print(f"Initial State ({initial_date}): Cash = ${current_cash:.2f}, Inventory = ${current_inventory:.2f}")

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n==========================================")
        print(f"=== Request {idx+1} of {len(quote_requests_sample)} ===")
        print(f"Context: {row['job']} organizing {row['event']} (Need: {row['need_size']})")
        print(f"Request Date: {request_date}")
        print(f"Current Cash: ${current_cash:.2f} | Current Inventory: ${current_inventory:.2f}")

        # Construct structured instruction for the orchestrator
        prompt = (
            f"You are the Sales & Operations Orchestrator for The Beaver's Choice Paper Company.\n"
            f"Process the following customer inquiry:\n\n"
            f"CUSTOMER INQUIRY:\n"
            f"\"{row['request']}\"\n\n"
            f"METADATA:\n"
            f"- Request Date: {request_date}\n"
            f"- Customer Role: {row['job']}\n"
            f"- Event Type: {row['event']}\n"
            f"- Order Size Category: {row['need_size']}\n\n"
            f"EXECUTION PROCEDURE:\n"
            f"1. Identify all requested items, quantities, and customer's required delivery deadline.\n"
            f"2. Delegate to 'inventory_manager' to check stock for each item as of {request_date}.\n"
            f"   - If stock is insufficient, check supplier lead time with estimate_supplier_delivery.\n"
            f"   - If an item is NOT in our paper catalog, or if supplier delivery date is AFTER the customer's deadline, the order CANNOT be fulfilled as requested.\n"
            f"3. DECISION:\n"
            f"   - If CANNOT be fulfilled: Do NOT execute any sale. Synthesize a polite, transparent explanation to the customer explaining the specific constraint (e.g. supplier restock date is after their required delivery date, or item not carried) and propose the earliest feasible date.\n"
            f"   - If CAN be fulfilled: Delegate to 'quoting_agent' to calculate prices and volume discounts, then delegate to 'sales_closer' to record each sales transaction on {request_date}.\n"
            f"4. FINAL CUSTOMER RESPONSE:\n"
            f"   Provide a polite, professional response to the customer summarizing the quote, discounts, total, and delivery schedule (or clear explanation if declining).\n"
            f"   CRITICAL PRIVACY: Do NOT mention internal wholesale costs, company profit margins, or internal database IDs."
        )

        try:
            # Instantiate fresh agent team for clean per-inquiry state
            orchestrator = create_multi_agent_system()
            response = str(orchestrator.run(prompt))
        except Exception as err:
            print(f"ERROR executing agent system: {err}")
            response = f"Thank you for contacting Beaver's Choice Paper Company. We encountered an operational delay reviewing your request for {request_date}. Please contact our sales desk directly."

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"\nResponse:\n{response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": response,
            }
        )

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n==========================================")
    print("===== FINAL FINANCIAL REPORT =====")
    print(f"Final Date: {final_date}")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")
    print(f"Total Assets: ${final_report['total_assets']:.2f}")
    print("==========================================")

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv("test_results.csv", index=False)
    print(f"Saved {len(results_df)} test results to test_results.csv")
    return results

if __name__ == "__main__":
    results = run_test_scenarios()

