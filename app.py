import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table, no_update
import datetime

# Read the CSV file
df = pd.read_csv('data/swiftshop_sales_data.csv')

# Fill missing values in 'customer_region' with 'Unknown'
df['customer_region'] = df['customer_region'].fillna('Unknown')

# Fill missing values in 'payment_method' with 'Unknown'
df['payment_method'] = df['payment_method'].fillna('Unknown')

# Fill missing values in 'customer_rating' with the mean rating (rounded)
df['customer_rating'] = df['customer_rating'].fillna(df['customer_rating'].mean().round())

# Store original date format for display
original_dates = df['order_date'].copy()

# Convert order_date to datetime for proper filtering and grouping
df['order_date'] = pd.to_datetime(df['order_date'])

# Extract month name and year for analysis
df['month'] = df['order_date'].dt.strftime('%B')  # Full month name
df['year'] = df['order_date'].dt.year.astype(int)  # Extract year as integer
df['month_num'] = df['order_date'].dt.month  # Create a month number column for proper sorting

# Create list of columns for display table (exclude computed columns)
table_cols = [col for col in df.columns if col not in ['year', 'month_num']]

# Create display DataFrame (for the data table)
display_df = df[table_cols].copy()
display_df['order_date'] = original_dates  # Restore original date format

# Create month order mapping for proper sorting in the visualization
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

# Calculate KPIs
# Average Order Value
avg_order_value = df['total_amount'].mean().round(2)

# Most Sold Product
product_sales = df.groupby('product_name')['quantity'].sum().reset_index()
most_sold_product = product_sales.sort_values('quantity', ascending=False).iloc[0]
most_sold_product_name = most_sold_product['product_name']
most_sold_product_qty = int(most_sold_product['quantity'])

# Customer Rating by Category
category_ratings = df.groupby('category')['customer_rating'].mean().round(1).reset_index()
category_ratings = category_ratings.sort_values('customer_rating', ascending=False)

# Initialize the Dash app with CSS from assets folder
app = Dash(__name__)
app.title = "SwiftShop Sales Dashboard"

# Main layout 
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("SwiftShop Sales Dashboard", className='dashboard-title')
    ], className='dashboard-header'),
    
    # Navbar with tabs
    dcc.Tabs([
        # Tab for Data Table
        dcc.Tab(
            label='Data Table', 
            className='custom-tab',
            selected_className='custom-tab--selected',
            children=[
                html.Div([
                    html.H3('SwiftShop Sales Data', className='section-heading'),
                    
                    # Date Range Picker and Export Button
                    html.Div([
                        html.Div([
                            html.Label('Filter by Date Range:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                            dcc.DatePickerRange(
                                id='date-range-picker',
                                min_date_allowed=df['order_date'].min().date(),
                                max_date_allowed=df['order_date'].max().date(),
                                start_date=df['order_date'].min().date(),
                                end_date=df['order_date'].max().date(),
                                display_format='YYYY-MM-DD',
                                style={'marginBottom': '15px'},
                                calendar_orientation='horizontal',
                                day_size=35,
                                clearable=True,
                                # Styling for the selected dates
                                month_format='MMMM YYYY',
                                persistence=True,
                                persisted_props=['start_date', 'end_date'],
                                persistence_type='session',                           
                            ),
                        ], style={'flex': '2'}),
                        
                        html.Div([
                            html.Button(
                                'Export to CSV', 
                                id='btn-download-csv', 
                                style={
                                    'backgroundColor': '#3498db',
                                    'color': 'white',
                                    'border': 'none',
                                    'padding': '10px 15px',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'marginLeft': '20px',
                                    'fontWeight': 'bold'
                                }
                            ),
                            dcc.Download(id='download-dataframe-csv'),
                        ], style={'flex': '1', 'textAlign': 'right'}),
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),
                    
                    # Data Table
                    dash_table.DataTable(
                        id='data-table',
                        columns=[{"name": i, "id": i} for i in display_df.columns],
                        data=display_df.to_dict('records'),
                        page_size=100,
                        style_table={'overflowX': 'auto'},
                        style_header={
                            'backgroundColor': '#3498db',
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                            'border': '1px solid #3498db'
                        },
                        style_cell={
                            'minWidth': '100px', 
                            'width': '150px', 
                            'maxWidth': '300px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'backgroundColor': 'white',
                            'color': '#34495e',
                            'fontFamily': 'Arial, sans-serif',
                            'fontSize': '14px',
                            'textAlign': 'left',
                            'padding': '8px'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#dfe6e9'
                            }
                        ],
                        page_action='native',
                        page_current=0,
                    )
                ], className='content-container')
            ]
        ),
        
        # Tab for Visualizations
        dcc.Tab(
            label='Visualizations', 
            className='custom-tab',
            selected_className='custom-tab--selected',
            children=[
                html.Div([
                    html.H3('Sales Visualizations', className='section-heading'),
                    
                    # KPIs Section
                    html.Div([
                        html.H4("Key Performance Indicators", style={'textAlign': 'center', 'marginBottom': '20px'}),
                        
                        # KPI Cards Container
                        html.Div([
                            # KPI Card 1: Average Order Value
                            html.Div([
                                html.H5("Average Order Value", style={'marginBottom': '10px'}),
                                html.Div([
                                    html.Span(f"${avg_order_value}", 
                                             style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#3498db'}),
                                ], style={'textAlign': 'center'}),
                                html.P("Average amount spent per order", style={'fontSize': '12px', 'color': '#7f8c8d'})
                            ], style={
                                'flex': '1', 
                                'padding': '15px', 
                                'borderRadius': '8px', 
                                'backgroundColor': 'white', 
                                'boxShadow': '0px 2px 5px rgba(0,0,0,0.1)',
                                'margin': '0 10px'
                            }),
                            
                            # KPI Card 2: Most Sold Product
                            html.Div([
                                html.H5("Most Sold Product", style={'marginBottom': '10px'}),
                                html.Div([
                                    html.Span(most_sold_product_name, 
                                             style={'fontSize': '22px', 'fontWeight': 'bold', 'color': '#3498db'})
                                ], style={'textAlign': 'center'}),
                                html.P(f"Sold {most_sold_product_qty} units", style={'fontSize': '12px', 'color': '#7f8c8d'})
                            ], style={
                                'flex': '1', 
                                'padding': '15px', 
                                'borderRadius': '8px', 
                                'backgroundColor': 'white', 
                                'boxShadow': '0px 2px 5px rgba(0,0,0,0.1)',
                                'margin': '0 10px'
                            }),
                            
                            # KPI Card 3: Category Ratings
                            html.Div([
                                html.H5("Customer Ratings by Category", style={'marginBottom': '10px'}),
                                html.Div([
                                    html.Table([
                                        html.Thead(
                                            html.Tr([
                                                html.Th("Category", style={'paddingRight': '15px', 'textAlign': 'left'}),
                                                html.Th("Rating", style={'textAlign': 'center'})
                                            ])
                                        ),
                                        html.Tbody([
                                            html.Tr([
                                                html.Td(row['category'], style={'paddingRight': '15px',}),
                                                html.Td([
                                                    html.Span(f"{row['customer_rating']} ", style={'fontWeight': 'bold'}),
                                                    html.Span("★", style={'color': '#f1c40f'})
                                                ], style={'textAlign': 'center'})
                                            ]) for i, row in category_ratings.iterrows()
                                        ])
                                    ], style={'width': '100%', 'fontSize': '14px'})
                                ], style={'textAlign': 'center'})
                            ], style={
                                'flex': '1', 
                                'padding': '15px', 
                                'borderRadius': '8px', 
                                'backgroundColor': 'white', 
                                'boxShadow': '0px 2px 5px rgba(0,0,0,0.1)',
                                'margin': '0 10px'
                            })
                        ], style={
                            'display': 'flex', 
                            'justifyContent': 'space-between',
                            'marginBottom': '30px'
                        })
                    ], className='kpi-section', style={'marginBottom': '30px', 'paddingBottom': '20px', 'borderBottom': '1px solid #ddd'}),
                    
                    # Year filter for the bar chart
                    html.Div([
                        html.H4("Monthly Sales Analysis", style={'marginBottom': '15px'}),
                        html.Label('Select Year:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                        dcc.RadioItems(
                            id='year-filter',
                            options=[
                                {'label': '2024', 'value': 2024},
                                {'label': '2025', 'value': 2025}
                            ],
                            value=2024,  
                            labelStyle={'display': 'inline-block', 'marginRight': '20px'},
                            style={'margin': '20px'}
                        )
                    ], style={'marginBottom': '20px', }),
                    
                    # Bar chart showing monthly sales
                    dcc.Graph(id='monthly-sales-chart'),
                    
                    # Pie Chart Section
                    html.Div([
                        html.H4("Sales Distribution", style={'marginTop': '30px', 'marginBottom': '15px'}),
                        html.Div([
                            dcc.Dropdown(
                                id='pie-chart-dropdown',
                                options=[
                                    {'label': 'Customer Region', 'value': 'customer_region'},
                                    {'label': 'Category', 'value': 'category'},
                                    {'label': 'Payment Method', 'value': 'payment_method'}
                                ],
                                value='category', 
                                style={'width': '300px', 'marginY': '20px'},
                                clearable=False  
                            )
                        ]),
                        dcc.Graph(id='sales-distribution-pie-chart')
                    ], style={'marginTop': '30px', 'paddingTop': '20px', 'borderTop': '1px solid #ddd'}),
                    
                    # Histogram Section for Customer Ratings
                    html.Div([
                        html.H4("Customer Rating Distribution", style={'marginTop': '30px', 'marginBottom': '15px'}),
                        html.Div([
                            dcc.Dropdown(
                                id='rating-histogram-dropdown',
                                options=[
                                    {'label': 'Product', 'value': 'product_name'},
                                    {'label': 'Category', 'value': 'category'},
                                    {'label': 'Customer Region', 'value': 'customer_region'}
                                ],
                                value='product_name',  
                                style={'width': '300px', 'marginY': '20px'},
                                clearable=False  
                            )
                        ]),
                        dcc.Graph(id='customer-rating-histogram')
                    ], style={'marginTop': '30px', 'paddingTop': '20px', 'borderTop': '1px solid #ddd'}),
                    
                    # Monthly Order Comparison Section
                    html.Div([
                        html.H4("Monthly Order Count Comparison", style={'marginTop': '30px', 'marginBottom': '15px'}),
                        html.Div([
                            dcc.Dropdown(
                                id='month-comparison-dropdown',
                                options=[
                                    {'label': month, 'value': month} for month in month_order
                                ],
                                value=['January'],  # Default to January as a list for multi-selection
                                multi=True,    
                                style={'width': '500px', 'marginY': '20px'},
                                placeholder="Select one or more months to compare"
                            )
                        ]),
                        dcc.Graph(id='month-comparison-chart')
                    ], style={'marginTop': '30px', 'paddingTop': '20px', 'borderTop': '1px solid #ddd'}),
                    
                    # Category and Region Orders Count Section
                    html.Div([
                        html.H4("Orders by Category and Region", style={'marginTop': '30px', 'marginBottom': '15px'}),
                        html.Div([
                            # Filter controls in a row
                            html.Div([
                                # Category selection
                                html.Div([
                                    html.Label('Select Categories:', style={'fontWeight': 'bold', 'marginRight': '10px', 'display': 'block'}),
                                    dcc.Dropdown(
                                        id='category-filter-dropdown',
                                        options=[
                                            {'label': category, 'value': category} for category in df['category'].unique()
                                        ],
                                        value=(df['category'].unique())[:2],  # Default to first 2 categories
                                        multi=True,
                                        style={'width': '100%' , 'marginTop': '10px'},
                                        placeholder="Select one or more categories"
                                    )
                                ], style={'flex': '1', 'marginRight': '20px' }),
                                
                                # Region selection
                                html.Div([
                                    html.Label('Select Regions:', style={'fontWeight': 'bold', 'marginRight': '10px', 'display': 'block'}),
                                    dcc.Dropdown(
                                        id='region-filter-dropdown',
                                        options=[
                                            {'label': region, 'value': region} for region in df['customer_region'].unique()
                                        ],
                                        value=(df['customer_region'].unique())[:2],  # Default to first 2 regions
                                        multi=True,
                                        style={'width': '100%', 'marginTop': '10px'},
                                        placeholder="Select one or more regions"
                                    )
                                ], style={'flex': '1'}),
                            ], style={'display': 'flex', 'margin': '20px'}),
                            
                            # Chart display options
                            html.Div([
                                html.Label('Display Mode:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                                dcc.RadioItems(
                                    id='category-region-display-mode',
                                    options=[
                                        {'label': 'Group by Category', 'value': 'category'},
                                        {'label': 'Group by Region', 'value': 'region'}
                                    ],
                                    value='category',
                                    labelStyle={'display': 'inline-block', 'marginRight': '20px' , 'marginTop': '10px'},
                                )
                            ], style={'marginBottom': '15px'})
                        ]),
                        dcc.Graph(id='category-region-chart')
                    ], style={'marginTop': '30px', 'paddingTop': '20px', 'borderTop': '1px solid #ddd'}),
                    
                ], className='content-container')
            ]
        )
    ], className='custom-tabs')
], className='dashboard-container')



# Callback to update the data table based on date range filter
@app.callback(
    Output('data-table', 'data'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_table(start_date, end_date):
    # If both dates are None, return the full dataset
    if start_date is None and end_date is None:
        return display_df.to_dict('records')
    
    # Filter the data by date range
    mask = True  # Start with all rows selected
    if start_date is not None:
        mask = mask & (df['order_date'] >= start_date)
    if end_date is not None:
        mask = mask & (df['order_date'] <= end_date)
    
    # Apply filter, select display columns, and restore date format
    filtered_display_df = df.loc[mask, table_cols].copy()
    date_format_map = dict(zip(df['order_date'], original_dates))
    filtered_display_df['order_date'] = filtered_display_df['order_date'].map(date_format_map)
    
    return filtered_display_df.to_dict('records')


# Callback for CSV download
@app.callback(
    Output('download-dataframe-csv', 'data'),
    [Input('btn-download-csv', 'n_clicks'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')],
    prevent_initial_call=True
)
def export_csv(n_clicks, start_date, end_date):
    if n_clicks is None:
        return no_update
    
    # Filter data based on date range
    mask = True
    if start_date is not None:
        mask = mask & (df['order_date'] >= start_date)
    if end_date is not None:
        mask = mask & (df['order_date'] <= end_date)
    
    # Create export dataframe with original date format
    export_df = df.loc[mask, table_cols].copy()
    date_format_map = dict(zip(df['order_date'], original_dates))
    export_df['order_date'] = export_df['order_date'].map(date_format_map)
    
    # Generate timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return dcc.send_data_frame(
        export_df.to_csv,
        f'swiftshop_sales_data_{timestamp}.csv',
        index=False
    )


# Callback to update the line chart based on the year filter
@app.callback(
    Output('monthly-sales-chart', 'figure'),
    [Input('year-filter', 'value')]
)
def update_monthly_sales_chart(selected_year):
    # Filter the data by selected year
    filtered_df = df[df['year'] == selected_year]
    
    # Group by month and calculate total sales
    monthly_sales = filtered_df.groupby(['month', 'month_num'])['total_amount'].sum().reset_index()
    
    # Sort by month number for chronological display
    monthly_sales = monthly_sales.sort_values('month_num')
    
    # Create the bar chart
    fig = px.bar(
        monthly_sales, 
        x='month', 
        y='total_amount',
        title=f'Monthly Sales for {selected_year}',
        labels={'total_amount': 'Total Sales', 'month': 'Month'},
    )
    
    # Enhance the bar chart appearance
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Total Sales ($)',
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(color='#34495e'),
        margin=dict(l=40, r=40, t=50, b=40),
        bargap=0.2,  # Gap between bars
        # Customize hover label appearance
        hoverlabel=dict(
            bgcolor='#f8f9fa', 
            font_size=12,
            font_color='#2c3e50',  
            bordercolor='#3498db'  
        )
    )
    
    # Enhance the bar style
    fig.update_traces(
        marker_color='#3498db',
        marker_line_color='#2c3e50',
        marker_line_width=1.5,
        opacity=0.8,
        texttemplate='%{y:$,.2f}',
        textposition='outside'
    )
    
    return fig


# Callback to update the pie chart based on dropdown selection
@app.callback(
    Output('sales-distribution-pie-chart', 'figure'),
    [Input('pie-chart-dropdown', 'value')]
)
def update_pie_chart(selected_dimension):
    # Group by selected dimension and calculate total sales
    sales_by_dimension = df.groupby(selected_dimension)['total_amount'].sum().reset_index()
    
    # Pie chart
    fig = px.pie(
        sales_by_dimension,
        names=selected_dimension,
        values='total_amount',
        title=f'Sales Distribution by {selected_dimension.replace("_", " ").title()}',
        hole=0.3, 
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Enhance the pie chart appearance
    fig.update_layout(
        font=dict(color='#34495e'),
        margin=dict(l=20, r=20, t=50, b=20),
        legend_title_text=selected_dimension.replace("_", " ").title(),
        hoverlabel=dict(
            bgcolor='#f8f9fa',  
            font_size=12,
            font_color='#2c3e50',
            bordercolor='#3498db'
        )
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>Total Sales: $%{value:.2f}<br>Percentage: %{percent:.1%}'
    )
    
    return fig


# Callback to update the histogram based on dropdown selection
@app.callback(
    Output('customer-rating-histogram', 'figure'),
    [Input('rating-histogram-dropdown', 'value')]
)
def update_rating_histogram(selected_dimension):
        
    # Group by selected dimension and calculate average rating
    avg_ratings = df.groupby(selected_dimension)['customer_rating'].mean().reset_index().round(2)
    
    # Sort by rating descending for better visualization
    avg_ratings = avg_ratings.sort_values('customer_rating', ascending=False)
    
    # Create the histogram
    fig = px.bar(
        avg_ratings,
        x=selected_dimension,
        y='customer_rating',
        title=f'Average Customer Rating by {selected_dimension.replace("_", " ").title()}',
        text='customer_rating',  
        color='customer_rating', 
        color_continuous_scale=px.colors.sequential.Blues,  
        height=500,  # Taller figure to accommodate longer labels
        labels={'customer_rating': 'Customer Rating' , 'product_name': 'Product Name'}  
    )
    
    # Enhance the histogram appearance
    fig.update_layout(
        xaxis_title=selected_dimension.replace("_", " ").title(),
        yaxis_title='Average Customer Rating',
        yaxis=dict(range=[0, 5.5]), 
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(color='#34495e'),
        margin=dict(l=40, r=40, t=50, b=100), 
        coloraxis_showscale=False,  # Hide the color scale
        # Customize hover label appearance
        hoverlabel=dict(
            bgcolor='#f8f9fa',  
            font_size=12,
            font_color='#2c3e50',
            bordercolor='#3498db'
        )
    )
    
    # Format text on bars and improve bar appearance
    fig.update_traces(
        texttemplate='%{text:.2f}', 
        textposition='outside',  
        marker_line_color='#2c3e50',
        opacity=0.8
    )
    
    
    # Improve x-axis readability for product names
    if selected_dimension == 'product_name':
        fig.update_layout(
            xaxis=dict(
                tickfont=dict(size=10) 
            )
        )
    
    # Add star symbols to y-axis tick labels to represent ratings
    fig.update_yaxes(
        tickmode='array',
        tickvals=[1, 2, 3, 4, 5],
        ticktext=['★', '★★', '★★★', '★★★★', '★★★★★']
    )
    
    return fig


# Helper function to create empty figure with message
def create_empty_figure(title, x_title="No Data", y_title="No Data"):
    return go.Figure().update_layout(
        title=title,
        xaxis={"title": x_title},
        yaxis={"title": y_title},
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(color='#34495e')
    )

# Callback to update the month comparison chart based on month selection
@app.callback(
    Output('month-comparison-chart', 'figure'),
    [Input('month-comparison-dropdown', 'value')]
)
def update_month_comparison_chart(selected_months):
    # Handle case when no months are selected
    if not selected_months:
        return create_empty_figure(
            "Please select at least one month to display data", 
            "Year", 
            "Number of Orders"
        )
    
    # Get all available years from the dataset    
    available_years = sorted(df['year'].unique())
    
    # Create an empty list to store data for each selected month
    all_data = []
    
    # Process each selected month
    for month in selected_months:
        # Filter data and count orders by year for this month
        monthly_data = df[df['month'] == month]
        order_counts = monthly_data.groupby('year')['order_id'].nunique().reset_index()
        order_counts.columns = ['Year', 'Order Count']
        order_counts['Month'] = month  
        
        # Add rows for years with no data (0 orders)
        for year in available_years:
            if year not in order_counts['Year'].values:
                order_counts = pd.concat([
                    order_counts, 
                    pd.DataFrame({'Year': [year], 'Order Count': [0], 'Month': [month]})
                ])
        
        all_data.append(order_counts)
    
    # Combine all the data
    combined_data = pd.concat(all_data)
    
    # Sort by year and month
    combined_data['Month_Order'] = combined_data['Month'].apply(lambda x: month_order.index(x))
    combined_data = combined_data.sort_values(['Year', 'Month_Order'])
    
    # Create the grouped bar chart
    fig = px.bar(
        combined_data, 
        x='Year', 
        y='Order Count',
        color='Month',  # Color by month
        barmode='group',  # Group bars by year
        text='Order Count',  
        title=f'Order Count Comparison by Month and Year',
        color_continuous_scale=px.colors.sequential.Blues, 
        category_orders={"Month": month_order}  # Ensure consistent order of months
    )
    
    # Enhance the bar chart appearance
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Orders ',
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(color='#34495e'),
        margin=dict(l=40, r=40, t=50, b=40),
        bargap=0.2,  # Gap between bars
        # Add a legend title
        legend_title_text='Month',
        # Customize hover label appearance
        hoverlabel=dict(
            bgcolor='#f8f9fa', 
            font_size=12,
            font_color='#2c3e50',  
            bordercolor='#3498db'  
        )
    )
    
    # Format x-axis to show years as integers
    fig.update_xaxes(type='category')
    fig.update_yaxes(dtick=1)  # Set y-axis ticks to integers
    
    # Enhance the bar style
    fig.update_traces(
        marker_line_color='#2c3e50',
        marker_line_width=1.5,
        opacity=0.8,
        textposition='outside' 
    )
    
    return fig


# Callback to update the category and region orders chart based on selections
@app.callback(
    Output('category-region-chart', 'figure'),
    [
        Input('category-filter-dropdown', 'value'),
        Input('region-filter-dropdown', 'value'),
        Input('category-region-display-mode', 'value')
    ]
)
def update_category_region_chart(selected_categories, selected_regions, display_mode):
    # Handle empty selections
    if not selected_categories or not selected_regions:
        return create_empty_figure("Please select at least one category and one region to display data")
    
    # Filter data based on selections
    filtered_df = df[
        (df['category'].isin(selected_categories)) & 
        (df['customer_region'].isin(selected_regions))
    ]
    
    # Check if we have data after filtering
    if filtered_df.empty:
        return create_empty_figure("No data available for the selected filters")
    
    # Prepare data based on display mode
    if display_mode == 'category':
        # Group by category first, then region
        primary_group = 'category'
        secondary_group = 'customer_region'
        title = 'Orders by Category and Region'
    else:
        # Group by region first, then category
        primary_group = 'customer_region'
        secondary_group = 'category'
        title = 'Orders by Region and Category'
    
    # Perform grouping and count orders
    grouped_data = filtered_df.groupby([primary_group, secondary_group])['order_id'].nunique().reset_index()
    grouped_data.columns = [primary_group, secondary_group, 'Order Count']
    
    # Create the grouped bar chart
    fig = px.bar(
        grouped_data,
        x=primary_group,
        y='Order Count',
        color=secondary_group,
        barmode='group',
        text='Order Count',
        title=title,
        color_discrete_sequence=px.colors.qualitative.Dark2,
        labels={
            'category': 'Category', 
            'customer_region': 'Customer Region',
            'Order Count': 'Order Count'
        } 
    )
    
    # Enhance chart appearance
    fig.update_layout(
        xaxis_title=primary_group.replace('_', ' ').title(),
        yaxis_title='Number of Orders',
        plot_bgcolor='rgba(255,255,255,0.9)',
        font=dict(color='#34495e'),
        margin=dict(l=40, r=40, t=50, b=40),
        bargap=0.2,
        legend_title_text=secondary_group.replace('_', ' ').title(),
        hoverlabel=dict(
            bgcolor='#f8f9fa',
            font_size=12,
            font_color='#2c3e50',
            bordercolor='#3498db'
        )
    )
    
    # Format axes and enhance bar style
    fig.update_xaxes(type='category')
    fig.update_yaxes(dtick=1)
    
    fig.update_traces(
        marker_line_color='#2c3e50',
        marker_line_width=1.5,
        opacity=0.8,
        textposition='outside'
    )
    
    return fig


app.run(debug=True)