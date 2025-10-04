# SwiftShop Sales Dashboard

An interactive data visualization dashboard for SwiftShop sales data built with Dash and Plotly.

## Features

- **Data Table:** Interactive table with date range filtering and CSV export
- **Monthly Sales Chart:** Bar chart showing sales by month for selected years
- **Sales Distribution:** Interactive pie chart for sales distribution by category, product, region or payment method
- **Customer Ratings:** Histogram of average customer ratings
- **Month Comparison:** Compare order counts across different months and years
- **Category and Region Analysis:** Analyze orders by product category and customer region


## Installation

1. Clone this repository or download the source code
2. Install the required packages:

```
pip install -r requirements.txt
```

# Or install packages individually:

```
pip install dash pandas plotly numpy
```


3. Run the application:

```
python app.py
```

4. Open your web browser and navigate to `http://127.0.0.1:8050/`

## Data Structure

The dashboard uses a CSV file with the following columns:
- `order_id`: Unique order identifier
- `order_date`: Date of order
- `product_name`: Name of the product
- `category`: Product category
- `quantity`: Quantity ordered
- `unit_price`: Price per unit
- `total_amount`: Total amount for the order
- `payment_method`: Method of payment
- `customer_region`: Geographic region of the customer
- `customer_rating`: Rating provided by customer (1-5)

## Customization

To use your own data:
1. Replace the `data/swiftshop_sales_data.csv` file with your own data
2. Ensure your data has the same column names or update the code accordingly

## Dependencies

- Dash
- Plotly
- Pandas


## Acknowledgements

- Data visualization powered by [Plotly](https://plotly.com/)
- Web application framework by [Dash](https://dash.plotly.com/)