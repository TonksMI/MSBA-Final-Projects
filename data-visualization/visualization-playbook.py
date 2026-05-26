"""
Visualization Playbook — Organized by Plot Type
==============================================

A comprehensive teaching handout organized by visualization types rather than
good/bad/important focus. Each page shows multiple variants of the same plot type
with business examples and best practices.

Installation:
pip install -U plotly kaleido reportlab networkx numpy pandas

Author: BUS 672 Course Materials (Plot Type Edition)
Date: 2025
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import networkx as nx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import warnings
warnings.filterwarnings('ignore')

# Set global random seed for reproducibility
np.random.seed(42)

class PlotTypeVisualizationPlaybook:
    def __init__(self):
        # Professional color schemes
        self.colors = {
            'primary': '#2E86AB',       # Blue
            'secondary': '#A23B72',     # Purple
            'accent': '#F18F01',        # Orange
            'success': '#2e7d32',       # Green
            'warning': '#f9a825',       # Gold
            'danger': '#b71c1c',        # Red
            'neutral': '#6C757D',       # Gray
            'light_blue': '#E3F2FD',
            'light_green': '#E8F5E8',
            'light_orange': '#FFF3E0',
            'light_gray': '#F5F5F5'
        }

        # Create output directory
        self.output_dir = 'output_playbook'
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate comprehensive datasets
        self._generate_all_data()

    def _generate_all_data(self):
        """Generate comprehensive business datasets for all plot types"""

        # Categorical Data: Company Performance Analysis
        self.companies = ['TechCorp', 'DataInc', 'CloudSys', 'WebDev', 'AppBuild', 'CodeGen']
        self.revenue = [2.5, 1.8, 3.2, 1.2, 0.9, 1.5]  # Millions
        self.profit_margin = [15.2, 12.8, 18.5, 10.1, 8.3, 11.7]  # Percentage
        self.employees = [120, 85, 150, 65, 45, 75]
        self.market_share = [22, 18, 28, 12, 8, 12]  # Percentage

        # Regional Performance
        self.regions = ['North', 'South', 'East', 'West', 'Central']
        self.regional_sales = [450, 380, 520, 290, 360]  # Thousands
        self.regional_growth = [8.2, 5.4, 12.1, 3.8, 6.9]  # YoY percentage

        # Product Categories
        self.products = ['Software', 'Hardware', 'Services', 'Training', 'Support']
        self.product_revenue = [1800, 1200, 800, 400, 300]  # Thousands
        self.product_satisfaction = [4.2, 3.8, 4.5, 4.1, 3.9]  # 1-5 scale

        # Ordinal Data: Employee Analysis
        self.satisfaction_levels = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
        self.satisfaction_counts = [12, 28, 65, 145, 87]
        self.satisfaction_values = [1, 2, 3, 4, 5]

        self.experience_levels = ['Entry', 'Junior', 'Mid', 'Senior', 'Executive']
        self.experience_salaries = [45000, 65000, 85000, 120000, 180000]
        self.experience_counts = [45, 78, 123, 89, 23]

        # Education progression
        self.education_levels = ['High School', 'Associates', 'Bachelor', 'Master', 'PhD']
        self.education_2022 = [38000, 48000, 72000, 95000, 135000]
        self.education_2023 = [41000, 52000, 78000, 102000, 145000]

        # Quantitative Data: Performance Metrics
        n_samples = 200
        np.random.seed(42)

        # Sales performance analysis
        self.sales_experience = np.random.normal(5, 2.5, n_samples)  # Years
        self.sales_performance = 60 + 3.2 * self.sales_experience + np.random.normal(0, 8, n_samples)
        self.sales_revenue = 50000 + 8000 * self.sales_performance/100 + np.random.normal(0, 12000, n_samples)

        # Customer metrics
        self.customer_age = np.random.randint(22, 70, n_samples)
        self.customer_spend = 100 + 15 * (self.customer_age - 22) + np.random.gamma(2, 50, n_samples)
        self.customer_satisfaction = np.clip(3 + 0.02 * self.customer_spend + np.random.normal(0, 0.5, n_samples), 1, 5)

        # Product metrics
        self.product_cost = np.random.gamma(3, 25, n_samples)
        self.product_price = self.product_cost * np.random.uniform(1.5, 3.0, n_samples)
        self.product_sales = np.random.poisson(np.maximum(1, 50 - 0.3 * self.product_price))

        # Temporal Data: Business Time Series
        self.dates = pd.date_range('2020-01-01', '2023-12-31', freq='M')

        # Revenue trend with seasonality and growth
        trend = np.linspace(800000, 1200000, len(self.dates))
        seasonal = 150000 * np.sin(2 * np.pi * np.arange(len(self.dates)) / 12)
        noise = np.random.normal(0, 30000, len(self.dates))
        self.monthly_revenue = trend + seasonal + noise

        # Operating costs
        self.monthly_costs = 0.65 * self.monthly_revenue + np.random.normal(0, 20000, len(self.dates))

        # Customer acquisition
        self.monthly_customers = 1000 + 20 * np.arange(len(self.dates)) + 200 * np.sin(2 * np.pi * np.arange(len(self.dates)) / 12) + np.random.normal(0, 100, len(self.dates))

        # Website traffic
        self.monthly_traffic = 50000 + 500 * np.arange(len(self.dates)) + 10000 * np.sin(2 * np.pi * np.arange(len(self.dates)) / 12) + np.random.normal(0, 2000, len(self.dates))

        # Calculate derived metrics
        self.monthly_profit = self.monthly_revenue - self.monthly_costs
        self.profit_margin = (self.monthly_profit / self.monthly_revenue) * 100

        # YoY Growth calculation
        self.yoy_growth = []
        for i in range(len(self.dates)):
            if i >= 12:
                yoy = ((self.monthly_revenue[i] - self.monthly_revenue[i-12]) / self.monthly_revenue[i-12]) * 100
            else:
                yoy = 0
            self.yoy_growth.append(yoy)

        # Network/Relational Data: Business Network
        self.network_graph = nx.barabasi_albert_graph(30, 4, seed=42)
        self.network_pos = nx.spring_layout(self.network_graph, seed=42)
        self.betweenness = nx.betweenness_centrality(self.network_graph)
        self.closeness = nx.closeness_centrality(self.network_graph)
        self.degree = dict(self.network_graph.degree())
        self.eigenvector = nx.eigenvector_centrality(self.network_graph)

        # Customer-Product relationships
        self.customer_nodes = list(range(15))
        self.product_nodes = list(range(15, 25))
        self.supplier_nodes = list(range(25, 30))

        # Spatial Data: Geographic Business Analysis
        self.states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI',
                      'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI']

        # Generate realistic state data
        state_populations = [39538223, 29145505, 21538187, 20201249, 13002700,
                           12812508, 11799448, 10711908, 10439388, 10037261,
                           9288994, 8631393, 7705281, 7151502, 7001399,
                           6910840, 6785528, 6196010, 6177224, 5893718]

        self.state_population = dict(zip(self.states, state_populations))
        self.state_sales = {state: pop * np.random.uniform(15, 45) for state, pop in self.state_population.items()}
        self.sales_per_capita = {state: self.state_sales[state] / pop for state, pop in self.state_population.items()}

        # Store locations
        self.store_locations = {
            'CA': {'lat': 36.7783, 'lon': -119.4179, 'stores': 25},
            'TX': {'lat': 31.9686, 'lon': -99.9018, 'stores': 18},
            'FL': {'lat': 27.7663, 'lon': -82.6404, 'stores': 15},
            'NY': {'lat': 42.3601, 'lon': -74.0060, 'stores': 22},
            'PA': {'lat': 41.2033, 'lon': -77.1945, 'stores': 12},
            'IL': {'lat': 40.6331, 'lon': -89.3985, 'stores': 14},
            'OH': {'lat': 40.4173, 'lon': -82.9071, 'stores': 11},
            'GA': {'lat': 32.1656, 'lon': -82.9001, 'stores': 9},
            'NC': {'lat': 35.7596, 'lon': -79.0193, 'stores': 8},
            'MI': {'lat': 44.3148, 'lon': -85.6024, 'stores': 10}
        }

    def create_categorical_plots(self):
        """Create comprehensive categorical plot examples"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Simple Bar Chart: Revenue by Company',
                'Grouped Bar Chart: Revenue vs Employees',
                'Stacked Bar Chart: Market Share Breakdown',
                'Waterfall Chart: Quarterly Changes',
                'Funnel Chart: Sales Conversion',
                'Stacked Bar Chart: Department Performance'
            ),
            specs=[[{}, {}, {}],
                   [{}, {}, {}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.08
        )

        # 1. Simple Bar Chart
        fig.add_trace(
            go.Bar(x=self.companies, y=self.revenue,
                   marker_color=self.colors['primary'],
                   text=[f'${r:.1f}M' for r in self.revenue],
                   textposition='outside',
                   name='Revenue'),
            row=1, col=1
        )

        # 2. Grouped Bar Chart
        fig.add_trace(
            go.Bar(x=self.companies, y=self.revenue,
                   marker_color=self.colors['primary'],
                   name='Revenue ($M)',
                   offsetgroup=1),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=self.companies, y=[e/50 for e in self.employees],  # Scale employees for visibility
                   marker_color=self.colors['secondary'],
                   name='Employees (÷50)',
                   offsetgroup=2),
            row=1, col=2
        )

        # 3. Stacked Bar Chart
        market_other = [100 - sum(self.market_share[:i+1]) if i == 0
                       else 100 - sum(self.market_share) if i == len(self.market_share)-1
                       else 0 for i in range(len(self.market_share))]

        fig.add_trace(
            go.Bar(x=['Market Share'], y=[self.market_share[0]],
                   marker_color=self.colors['primary'],
                   name=self.companies[0]),
            row=1, col=3
        )

        for i, (company, share) in enumerate(zip(self.companies[1:], self.market_share[1:]), 1):
            fig.add_trace(
                go.Bar(x=['Market Share'], y=[share],
                       marker_color=self.colors['secondary'] if i == 1 else
                                  self.colors['accent'] if i == 2 else
                                  self.colors['success'] if i == 3 else
                                  self.colors['warning'] if i == 4 else self.colors['neutral'],
                       name=company),
                row=1, col=3
            )

        # 4. Waterfall Chart - Quarterly Changes
        quarters = ['Q1 Base', 'New Sales', 'Churn', 'Expansion', 'Q2 Total']
        values = [100, 25, -15, 8, 118]  # Starting, additions, subtractions, final

        colors = ['blue', 'green', 'red', 'green', 'blue']
        fig.add_trace(
            go.Waterfall(
                name="Quarterly Changes",
                orientation="v",
                measure=["absolute", "relative", "relative", "relative", "total"],
                x=quarters,
                textposition="outside",
                text=[f"${v}M" for v in values],
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                decreasing={"marker": {"color": self.colors['danger']}},
                increasing={"marker": {"color": self.colors['success']}},
                totals={"marker": {"color": self.colors['primary']}}
            ),
            row=2, col=1
        )

        # 5. Funnel Chart - Sales Conversion
        stages = ['Leads', 'Qualified', 'Proposal', 'Negotiation', 'Closed']
        funnel_values = [1000, 400, 200, 100, 60]

        fig.add_trace(
            go.Funnel(
                y=stages,
                x=funnel_values,
                textinfo="value+percent initial",
                textposition="inside",
                textfont={"size": 12, "color": "white"},
                marker={"color": [self.colors['primary'], self.colors['secondary'],
                               self.colors['accent'], self.colors['warning'], self.colors['success']]}
            ),
            row=2, col=2
        )

        # 6. Stacked Bar Chart - Department Performance
        departments = ['Sales', 'Marketing', 'Engineering', 'Support']
        q1_values = [45, 25, 35, 20]
        q2_values = [50, 30, 40, 25]
        q3_values = [48, 28, 42, 22]

        fig.add_trace(
            go.Bar(
                x=departments,
                y=q1_values,
                name='Q1 Revenue',
                marker_color=self.colors['primary'],
                text=[f'${v}K' for v in q1_values],
                textposition='inside'
            ),
            row=2, col=3
        )

        fig.add_trace(
            go.Bar(
                x=departments,
                y=q2_values,
                name='Q2 Revenue',
                marker_color=self.colors['secondary'],
                text=[f'${v}K' for v in q2_values],
                textposition='inside'
            ),
            row=2, col=3
        )

        fig.add_trace(
            go.Bar(
                x=departments,
                y=q3_values,
                name='Q3 Revenue',
                marker_color=self.colors['accent'],
                text=[f'${v}K' for v in q3_values],
                textposition='inside'
            ),
            row=2, col=3
        )

        # Set the last subplot to stack bars
        fig.update_layout(barmode='stack')

        # Update layout
        fig.update_layout(
            title="Categorical Data Visualization Types",
            height=800,
            showlegend=True,
            font=dict(size=10)
        )

        # Update axes
        fig.update_yaxes(title_text="Revenue ($M)", row=1, col=1)
        fig.update_yaxes(title_text="Value", row=1, col=2)
        fig.update_yaxes(title_text="Market Share (%)", row=1, col=3)
        fig.update_yaxes(title_text="Revenue ($M)", row=2, col=1)
        fig.update_xaxes(title_text="Conversion Count", row=2, col=2)
        fig.update_yaxes(title_text="Revenue ($K)", row=2, col=3)

        return fig

    def create_ordinal_plots(self):
        """Create comprehensive ordinal plot examples"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Ordered Bar Chart: Experience vs Salary',
                'Likert Scale: Employee Satisfaction',
                'Slope Chart: Education Salary Changes',
                'Stacked Likert: Satisfaction Breakdown',
                'Ordered Scatter: Experience Distribution',
                'Rating Scale Heatmap'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.08
        )

        # 1. Ordered Bar Chart
        fig.add_trace(
            go.Bar(x=self.experience_levels, y=self.experience_salaries,
                   marker_color=self.colors['primary'],
                   text=[f'${s/1000:.0f}K' for s in self.experience_salaries],
                   textposition='outside',
                   name='Average Salary'),
            row=1, col=1
        )

        # Add median line
        median_salary = np.median(self.experience_salaries)
        fig.add_hline(y=median_salary, line_dash="dash", line_color="black",
                     annotation_text=f"Median: ${median_salary/1000:.0f}K", row=1, col=1)

        # 2. Likert Scale (Diverging Bar)
        negative = sum(self.satisfaction_counts[:2])
        neutral = self.satisfaction_counts[2]
        positive = sum(self.satisfaction_counts[3:])

        fig.add_trace(
            go.Bar(x=[-negative], y=['Employee Satisfaction'],
                   orientation='h',
                   marker_color=self.colors['danger'],
                   name=f'Negative ({negative})',
                   text=[f'{negative}'], textposition='inside'),
            row=1, col=2
        )

        fig.add_trace(
            go.Bar(x=[neutral], y=['Employee Satisfaction'],
                   orientation='h', base=[0],
                   marker_color=self.colors['neutral'],
                   name=f'Neutral ({neutral})',
                   text=[f'{neutral}'], textposition='inside'),
            row=1, col=2
        )

        fig.add_trace(
            go.Bar(x=[positive], y=['Employee Satisfaction'],
                   orientation='h', base=[neutral],
                   marker_color=self.colors['success'],
                   name=f'Positive ({positive})',
                   text=[f'{positive}'], textposition='inside'),
            row=1, col=2
        )

        # 3. Slope Chart
        for i, level in enumerate(self.education_levels):
            sal_2022 = self.education_2022[i]
            sal_2023 = self.education_2023[i]
            change_pct = ((sal_2023 - sal_2022) / sal_2022) * 100

            color = self.colors['success'] if change_pct > 7 else \
                   self.colors['warning'] if change_pct > 5 else self.colors['danger']

            fig.add_trace(
                go.Scatter(x=[1, 2], y=[sal_2022, sal_2023],
                          mode='lines+markers',
                          line=dict(color=color, width=2),
                          marker=dict(color=color, size=6),
                          name=level,
                          showlegend=False),
                row=1, col=3
            )

            # Add change annotation
            mid_y = (sal_2022 + sal_2023) / 2
            fig.add_annotation(x=1.5, y=mid_y,
                              text=f"{level}<br>+{change_pct:.1f}%",
                              showarrow=False, font_size=8,
                              bgcolor="white", bordercolor=color,
                              row=1, col=3)

        # Add year labels
        fig.add_annotation(x=1, y=max(self.education_2023)*1.1, text="2022",
                          showarrow=False, font_size=12, font_weight="bold", row=1, col=3)
        fig.add_annotation(x=2, y=max(self.education_2023)*1.1, text="2023",
                          showarrow=False, font_size=12, font_weight="bold", row=1, col=3)

        # 4. Stacked Likert (Detailed)
        for i, (level, count) in enumerate(zip(self.satisfaction_levels, self.satisfaction_counts)):
            color = self.colors['danger'] if i < 2 else \
                   self.colors['neutral'] if i == 2 else self.colors['success']

            fig.add_trace(
                go.Bar(x=['Satisfaction Survey'], y=[count],
                       marker_color=color,
                       name=level,
                       text=[f'{count}'], textposition='inside'),
                row=2, col=1
            )

        # 5. Ordered Scatter
        fig.add_trace(
            go.Scatter(x=self.experience_levels, y=self.experience_counts,
                      mode='markers',
                      marker=dict(size=[c/3 for c in self.experience_counts],
                                color=self.colors['accent'],
                                opacity=0.7),
                      text=[f'{c} employees' for c in self.experience_counts],
                      textposition='top center',
                      name='Employee Count'),
            row=2, col=2
        )

        # 6. Rating Scale Heatmap
        # Create synthetic rating data
        departments = ['Sales', 'Marketing', 'IT', 'HR']
        rating_categories = ['Poor', 'Fair', 'Good', 'Excellent']
        rating_matrix = np.random.randint(5, 25, (len(departments), len(rating_categories)))

        fig.add_trace(
            go.Heatmap(z=rating_matrix,
                      x=rating_categories,
                      y=departments,
                      colorscale='RdYlGn',
                      text=rating_matrix,
                      texttemplate="%{text}",
                      textfont={"size": 10},
                      showscale=True),
            row=2, col=3
        )

        # Update layout
        fig.update_layout(
            title="Ordinal Data Visualization Types",
            height=800,
            showlegend=True,
            font=dict(size=10)
        )

        # Update specific axes
        fig.update_yaxes(title_text="Salary ($)", row=1, col=1)
        fig.update_yaxes(title_text="Salary ($)", row=1, col=3)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        fig.update_yaxes(title_text="Employee Count", row=2, col=2)

        return fig

    def create_quantitative_plots(self):
        """Create comprehensive quantitative plot examples"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Scatter Plot: Experience vs Performance',
                'Histogram: Customer Spending Distribution',
                'Box Plot: Performance by Experience Level',
                'Scatter with Regression: Age vs Spending',
                'Violin Plot: Sales Distribution',
                'Bubble Chart: Cost vs Price vs Sales'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.08
        )

        # 1. Scatter Plot
        fig.add_trace(
            go.Scatter(x=self.sales_experience, y=self.sales_performance,
                      mode='markers',
                      marker=dict(color=self.colors['primary'], opacity=0.6),
                      name='Sales Performance',
                      hovertemplate='Experience: %{x:.1f} years<br>Performance: %{y:.1f}%<extra></extra>'),
            row=1, col=1
        )

        # Add trend line
        z = np.polyfit(self.sales_experience, self.sales_performance, 1)
        p = np.poly1d(z)
        x_trend = np.linspace(self.sales_experience.min(), self.sales_experience.max(), 100)
        correlation = np.corrcoef(self.sales_experience, self.sales_performance)[0, 1]

        fig.add_trace(
            go.Scatter(x=x_trend, y=p(x_trend),
                      mode='lines',
                      line=dict(color=self.colors['danger'], width=2),
                      name=f'Trend (r={correlation:.2f})'),
            row=1, col=1
        )

        # 2. Histogram
        fig.add_trace(
            go.Histogram(x=self.customer_spend,
                        nbinsx=25,
                        marker_color=self.colors['secondary'],
                        opacity=0.7,
                        name='Spending Distribution'),
            row=1, col=2
        )

        # Add mean and percentiles
        mean_spend = np.mean(self.customer_spend)
        p25, p75, p90 = np.percentile(self.customer_spend, [25, 75, 90])

        for val, label, color in [(mean_spend, 'Mean', 'black'),
                                 (p25, '25th', 'blue'),
                                 (p75, '75th', 'blue'),
                                 (p90, '90th', 'red')]:
            fig.add_vline(x=val, line_dash="dash", line_color=color,
                         annotation_text=f"{label}: ${val:.0f}", row=1, col=2)

        # 3. Box Plot by Categories
        experience_categories = ['Low (0-3)', 'Medium (3-6)', 'High (6+)']
        for i, cat in enumerate(experience_categories):
            if cat == 'Low (0-3)':
                mask = self.sales_experience <= 3
            elif cat == 'Medium (3-6)':
                mask = (self.sales_experience > 3) & (self.sales_experience <= 6)
            else:
                mask = self.sales_experience > 6

            fig.add_trace(
                go.Box(y=self.sales_performance[mask],
                      name=cat,
                      marker_color=self.colors['primary'] if i == 0 else
                                 self.colors['secondary'] if i == 1 else self.colors['accent'],
                      boxpoints='outliers'),
                row=1, col=3
            )

        # 4. Scatter with Regression Line
        fig.add_trace(
            go.Scatter(x=self.customer_age, y=self.customer_spend,
                      mode='markers',
                      marker=dict(color=self.customer_satisfaction,
                                colorscale='Viridis',
                                showscale=True,
                                colorbar=dict(title="Satisfaction", x=0.65),
                                opacity=0.6),
                      name='Customer Data',
                      hovertemplate='Age: %{x}<br>Spending: $%{y:.0f}<br>Satisfaction: %{marker.color:.1f}<extra></extra>'),
            row=2, col=1
        )

        # Add age trend line
        z_age = np.polyfit(self.customer_age, self.customer_spend, 1)
        p_age = np.poly1d(z_age)
        age_trend = np.linspace(self.customer_age.min(), self.customer_age.max(), 100)
        age_corr = np.corrcoef(self.customer_age, self.customer_spend)[0, 1]

        fig.add_trace(
            go.Scatter(x=age_trend, y=p_age(age_trend),
                      mode='lines',
                      line=dict(color=self.colors['danger'], width=2),
                      name=f'Age Trend (r={age_corr:.2f})'),
            row=2, col=1
        )

        # 5. Violin Plot
        performance_groups = ['Low', 'Medium', 'High']
        for i, group in enumerate(performance_groups):
            if group == 'Low':
                mask = self.sales_performance <= 70
            elif group == 'Medium':
                mask = (self.sales_performance > 70) & (self.sales_performance <= 85)
            else:
                mask = self.sales_performance > 85

            fig.add_trace(
                go.Violin(y=self.sales_revenue[mask],
                         name=f'{group} Performers',
                         box_visible=True,
                         meanline_visible=True,
                         fillcolor=self.colors['primary'] if i == 0 else
                                  self.colors['secondary'] if i == 1 else self.colors['success'],
                         opacity=0.6),
                row=2, col=2
            )

        # 6. Bubble Chart
        fig.add_trace(
            go.Scatter(x=self.product_cost, y=self.product_price,
                      mode='markers',
                      marker=dict(size=self.product_sales*2,  # Scale for visibility
                                color=self.product_sales,
                                colorscale='Plasma',
                                showscale=True,
                                colorbar=dict(title="Sales Volume", x=1.02),
                                opacity=0.7),
                      name='Products',
                      hovertemplate='Cost: $%{x:.0f}<br>Price: $%{y:.0f}<br>Sales: %{marker.color}<extra></extra>'),
            row=2, col=3
        )

        # Update layout
        fig.update_layout(
            title="Quantitative Data Visualization Types",
            height=800,
            showlegend=True,
            font=dict(size=10)
        )

        # Update axes
        fig.update_xaxes(title_text="Experience (years)", row=1, col=1)
        fig.update_yaxes(title_text="Performance (%)", row=1, col=1)
        fig.update_xaxes(title_text="Customer Spending ($)", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=1, col=2)
        fig.update_yaxes(title_text="Performance (%)", row=1, col=3)
        fig.update_xaxes(title_text="Age", row=2, col=1)
        fig.update_yaxes(title_text="Spending ($)", row=2, col=1)
        fig.update_yaxes(title_text="Revenue ($)", row=2, col=2)
        fig.update_xaxes(title_text="Product Cost ($)", row=2, col=3)
        fig.update_yaxes(title_text="Product Price ($)", row=2, col=3)

        return fig

    def create_temporal_plots(self):
        """Create comprehensive temporal plot examples"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Line Chart: Monthly Revenue Trend',
                'Area Chart: Revenue with Moving Average',
                'Multiple Lines: Revenue vs Costs vs Profit',
                'YoY Growth: Annual Comparison',
                'Seasonal Decomposition: Traffic Patterns',
                'Candlestick-style: Monthly Performance'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.08
        )

        # 1. Simple Line Chart
        fig.add_trace(
            go.Scatter(x=self.dates, y=self.monthly_revenue,
                      mode='lines+markers',
                      line=dict(color=self.colors['primary'], width=2),
                      marker=dict(size=4),
                      name='Monthly Revenue',
                      hovertemplate='%{x}<br>Revenue: $%{y:,.0f}<extra></extra>'),
            row=1, col=1
        )

        # Add trend line
        x_numeric = np.arange(len(self.dates))
        z_revenue = np.polyfit(x_numeric, self.monthly_revenue, 1)
        p_revenue = np.poly1d(z_revenue)

        fig.add_trace(
            go.Scatter(x=self.dates, y=p_revenue(x_numeric),
                      mode='lines',
                      line=dict(color=self.colors['danger'], width=2, dash='dash'),
                      name='Trend Line'),
            row=1, col=1
        )

        # 2. Area Chart with Moving Average
        ma_3 = pd.Series(self.monthly_revenue).rolling(window=3, center=True).mean()
        ma_12 = pd.Series(self.monthly_revenue).rolling(window=12, center=True).mean()

        fig.add_trace(
            go.Scatter(x=self.dates, y=self.monthly_revenue,
                      fill='tonexty',
                      mode='lines',
                      line=dict(color=self.colors['primary']),
                      fillcolor=self.colors['light_blue'],
                      name='Monthly Revenue',
                      opacity=0.7),
            row=1, col=2
        )

        fig.add_trace(
            go.Scatter(x=self.dates, y=ma_3,
                      mode='lines',
                      line=dict(color=self.colors['secondary'], width=2),
                      name='3-Month MA'),
            row=1, col=2
        )

        fig.add_trace(
            go.Scatter(x=self.dates, y=ma_12,
                      mode='lines',
                      line=dict(color=self.colors['danger'], width=3),
                      name='12-Month MA'),
            row=1, col=2
        )

        # 3. Multiple Lines
        fig.add_trace(
            go.Scatter(x=self.dates, y=self.monthly_revenue,
                      mode='lines',
                      line=dict(color=self.colors['primary'], width=2),
                      name='Revenue'),
            row=1, col=3
        )

        fig.add_trace(
            go.Scatter(x=self.dates, y=self.monthly_costs,
                      mode='lines',
                      line=dict(color=self.colors['danger'], width=2),
                      name='Costs'),
            row=1, col=3
        )

        fig.add_trace(
            go.Scatter(x=self.dates, y=self.monthly_profit,
                      mode='lines',
                      line=dict(color=self.colors['success'], width=2),
                      name='Profit'),
            row=1, col=3
        )

        # 4. YoY Growth
        yoy_dates = [d for i, d in enumerate(self.dates) if self.yoy_growth[i] != 0]
        yoy_values = [y for y in self.yoy_growth if y != 0]

        fig.add_trace(
            go.Scatter(x=yoy_dates, y=yoy_values,
                      mode='lines+markers',
                      line=dict(color=self.colors['accent'], width=2),
                      marker=dict(size=6),
                      name='YoY Growth %',
                      hovertemplate='%{x}<br>YoY Growth: %{y:.1f}%<extra></extra>'),
            row=2, col=1
        )

        # Add zero line and target
        fig.add_hline(y=0, line_dash="solid", line_color="black", row=2, col=1)
        fig.add_hline(y=10, line_dash="dash", line_color="green",
                     annotation_text="Target: 10%", row=2, col=1)

        # 5. Seasonal Pattern (Traffic)
        fig.add_trace(
            go.Scatter(x=self.dates, y=self.monthly_traffic,
                      mode='lines',
                      line=dict(color=self.colors['secondary'], width=2),
                      fill='tonexty',
                      fillcolor=self.colors['light_orange'],
                      name='Website Traffic'),
            row=2, col=2
        )

        # Add seasonal markers
        peak_months = [i for i, d in enumerate(self.dates) if d.month in [11, 12, 1]]  # Holiday season
        peak_traffic = [self.monthly_traffic[i] for i in peak_months]
        peak_dates = [self.dates[i] for i in peak_months]

        fig.add_trace(
            go.Scatter(x=peak_dates, y=peak_traffic,
                      mode='markers',
                      marker=dict(color=self.colors['danger'], size=8, symbol='star'),
                      name='Peak Season'),
            row=2, col=2
        )

        # 6. OHLC-style chart (using profit margin as example)
        quarterly_dates = self.dates[::3]  # Every 3 months
        quarterly_margins = [self.profit_margin[i:i+3] for i in range(0, len(self.profit_margin), 3)]

        ohlc_data = []
        for i, margins in enumerate(quarterly_margins[:len(quarterly_dates)]):
            if len(margins) > 0:
                ohlc_data.append({
                    'date': quarterly_dates[i],
                    'open': margins[0],
                    'high': max(margins),
                    'low': min(margins),
                    'close': margins[-1]
                })

        if ohlc_data:
            fig.add_trace(
                go.Candlestick(x=[d['date'] for d in ohlc_data],
                             open=[d['open'] for d in ohlc_data],
                             high=[d['high'] for d in ohlc_data],
                             low=[d['low'] for d in ohlc_data],
                             close=[d['close'] for d in ohlc_data],
                             name='Profit Margin %'),
                row=2, col=3
            )

        # Update layout
        fig.update_layout(
            title="Temporal Data Visualization Types",
            height=800,
            showlegend=True,
            font=dict(size=10)
        )

        # Update axes
        fig.update_yaxes(title_text="Revenue ($)", row=1, col=1)
        fig.update_yaxes(title_text="Revenue ($)", row=1, col=2)
        fig.update_yaxes(title_text="Amount ($)", row=1, col=3)
        fig.update_yaxes(title_text="YoY Growth (%)", row=2, col=1)
        fig.update_yaxes(title_text="Website Traffic", row=2, col=2)
        fig.update_yaxes(title_text="Profit Margin (%)", row=2, col=3)

        return fig

    def create_network_plots(self):
        """Create comprehensive network/relational plot examples"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Node-Link Network: Business Connections',
                'Centrality Analysis: Key Players',
                'Chord Diagram Style: Relationships',
                'Hierarchical Network: Organizational',
                'Bipartite Network: Customer-Product',
                'Network Metrics Comparison'
            ),
            specs=[[{}, {}, {}],
                   [{}, {}, {}]],
            vertical_spacing=0.15,
            horizontal_spacing=0.08
        )

        # 1. Basic Network
        G = self.network_graph
        pos = self.network_pos

        # Create edges
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        fig.add_trace(
            go.Scatter(x=edge_x, y=edge_y,
                      mode='lines',
                      line=dict(width=1, color='lightgray'),
                      showlegend=False, hoverinfo='none'),
            row=1, col=1
        )

        # Add nodes
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_size = [self.degree[node] * 3 + 5 for node in G.nodes()]

        fig.add_trace(
            go.Scatter(x=node_x, y=node_y,
                      mode='markers',
                      marker=dict(size=node_size,
                                color=self.colors['primary'],
                                line=dict(width=1, color='white')),
                      text=[f'Node {node}' for node in G.nodes()],
                      hovertemplate='%{text}<br>Degree: %{marker.size}<extra></extra>',
                      name='Business Units'),
            row=1, col=1
        )

        # 2. Centrality Analysis
        fig.add_trace(
            go.Scatter(x=edge_x, y=edge_y,
                      mode='lines',
                      line=dict(width=1, color='lightgray'),
                      showlegend=False, hoverinfo='none'),
            row=1, col=2
        )

        # Color nodes by betweenness centrality
        centrality_values = [self.betweenness[node] for node in G.nodes()]
        fig.add_trace(
            go.Scatter(x=node_x, y=node_y,
                      mode='markers',
                      marker=dict(size=[c * 1000 + 10 for c in centrality_values],
                                color=centrality_values,
                                colorscale='Viridis',
                                showscale=True,
                                colorbar=dict(title="Centrality", x=0.35)),
                      text=[f'Node {node}<br>Centrality: {self.betweenness[node]:.3f}' for node in G.nodes()],
                      hovertemplate='%{text}<extra></extra>',
                      name='Centrality'),
            row=1, col=2
        )

        # 3. Chord-style (Simplified as circular layout)
        circular_pos = nx.circular_layout(G)

        # Circular edges
        circ_edge_x, circ_edge_y = [], []
        for edge in list(G.edges())[:20]:  # Limit for clarity
            x0, y0 = circular_pos[edge[0]]
            x1, y1 = circular_pos[edge[1]]
            circ_edge_x.extend([x0, x1, None])
            circ_edge_y.extend([y0, y1, None])

        fig.add_trace(
            go.Scatter(x=circ_edge_x, y=circ_edge_y,
                      mode='lines',
                      line=dict(width=1, color=self.colors['accent']),
                      opacity=0.5,
                      showlegend=False, hoverinfo='none'),
            row=1, col=3
        )

        circ_node_x = [circular_pos[node][0] for node in G.nodes()]
        circ_node_y = [circular_pos[node][1] for node in G.nodes()]

        fig.add_trace(
            go.Scatter(x=circ_node_x, y=circ_node_y,
                      mode='markers+text',
                      marker=dict(size=15, color=self.colors['secondary']),
                      text=[str(node) for node in G.nodes()],
                      textposition='middle center',
                      textfont=dict(color='white', size=8),
                      name='Circular Layout'),
            row=1, col=3
        )

        # 4. Hierarchical (Tree-like)
        # Create a simple tree structure
        tree_nodes = list(range(15))
        tree_pos = {}

        # Root at top
        tree_pos[0] = (0, 1)

        # Level 1
        for i in range(1, 4):
            tree_pos[i] = ((i-2) * 0.6, 0.7)

        # Level 2
        level2_start = 4
        for parent in range(1, 4):
            for child in range(2):
                if level2_start < len(tree_nodes):
                    x_offset = (child - 0.5) * 0.3
                    tree_pos[level2_start] = (tree_pos[parent][0] + x_offset, 0.4)
                    level2_start += 1

        # Level 3
        level3_start = level2_start
        for parent in range(4, level2_start):
            for child in range(1):
                if level3_start < len(tree_nodes):
                    tree_pos[level3_start] = (tree_pos[parent][0], 0.1)
                    level3_start += 1

        # Tree edges
        tree_edges = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 6), (2, 7),
                     (3, 8), (3, 9), (4, 10), (5, 11), (6, 12), (7, 13), (8, 14)]

        tree_edge_x, tree_edge_y = [], []
        for edge in tree_edges:
            if edge[0] in tree_pos and edge[1] in tree_pos:
                x0, y0 = tree_pos[edge[0]]
                x1, y1 = tree_pos[edge[1]]
                tree_edge_x.extend([x0, x1, None])
                tree_edge_y.extend([y0, y1, None])

        fig.add_trace(
            go.Scatter(x=tree_edge_x, y=tree_edge_y,
                      mode='lines',
                      line=dict(width=2, color=self.colors['neutral']),
                      showlegend=False, hoverinfo='none'),
            row=2, col=1
        )

        tree_node_x = [tree_pos[node][0] for node in tree_nodes if node in tree_pos]
        tree_node_y = [tree_pos[node][1] for node in tree_nodes if node in tree_pos]

        fig.add_trace(
            go.Scatter(x=tree_node_x, y=tree_node_y,
                      mode='markers+text',
                      marker=dict(size=20, color=self.colors['success']),
                      text=[f'L{node}' for node in tree_nodes if node in tree_pos],
                      textposition='middle center',
                      textfont=dict(color='white', size=8),
                      name='Hierarchy'),
            row=2, col=1
        )

        # 5. Bipartite Network
        customers = self.customer_nodes
        products = self.product_nodes

        # Create bipartite layout
        bipartite_pos = {}
        for i, customer in enumerate(customers):
            bipartite_pos[customer] = (-1, (i - len(customers)/2) * 0.2)

        for i, product in enumerate(products):
            bipartite_pos[product] = (1, (i - len(products)/2) * 0.15)

        # Create some connections
        connections = [(c, p) for c in customers[:8] for p in products[:6] if np.random.random() > 0.7]

        bip_edge_x, bip_edge_y = [], []
        for customer, product in connections:
            x0, y0 = bipartite_pos[customer]
            x1, y1 = bipartite_pos[product]
            bip_edge_x.extend([x0, x1, None])
            bip_edge_y.extend([y0, y1, None])

        fig.add_trace(
            go.Scatter(x=bip_edge_x, y=bip_edge_y,
                      mode='lines',
                      line=dict(width=1, color=self.colors['accent']),
                      opacity=0.6,
                      showlegend=False, hoverinfo='none'),
            row=2, col=2
        )

        # Customer nodes
        cust_x = [bipartite_pos[c][0] for c in customers]
        cust_y = [bipartite_pos[c][1] for c in customers]

        fig.add_trace(
            go.Scatter(x=cust_x, y=cust_y,
                      mode='markers',
                      marker=dict(size=12, color=self.colors['primary'], symbol='circle'),
                      name='Customers',
                      text=[f'C{c}' for c in customers],
                      hovertemplate='%{text}<extra></extra>'),
            row=2, col=2
        )

        # Product nodes
        prod_x = [bipartite_pos[p][0] for p in products]
        prod_y = [bipartite_pos[p][1] for p in products]

        fig.add_trace(
            go.Scatter(x=prod_x, y=prod_y,
                      mode='markers',
                      marker=dict(size=12, color=self.colors['warning'], symbol='square'),
                      name='Products',
                      text=[f'P{p}' for p in products],
                      hovertemplate='%{text}<extra></extra>'),
            row=2, col=2
        )

        # 6. Network Metrics Comparison
        metrics = ['Degree', 'Betweenness', 'Closeness', 'Eigenvector']
        top_nodes = sorted(G.nodes(), key=lambda x: self.degree[x], reverse=True)[:8]

        degree_vals = [self.degree[node]/max(self.degree.values()) for node in top_nodes]
        between_vals = [self.betweenness[node]/max(self.betweenness.values()) for node in top_nodes]
        close_vals = [self.closeness[node]/max(self.closeness.values()) for node in top_nodes]
        eigen_vals = [self.eigenvector[node]/max(self.eigenvector.values()) for node in top_nodes]

        fig.add_trace(
            go.Scatter(x=top_nodes, y=degree_vals,
                      mode='lines+markers',
                      name='Degree (norm)',
                      line=dict(color=self.colors['primary'])),
            row=2, col=3
        )

        fig.add_trace(
            go.Scatter(x=top_nodes, y=between_vals,
                      mode='lines+markers',
                      name='Betweenness (norm)',
                      line=dict(color=self.colors['secondary'])),
            row=2, col=3
        )

        fig.add_trace(
            go.Scatter(x=top_nodes, y=close_vals,
                      mode='lines+markers',
                      name='Closeness (norm)',
                      line=dict(color=self.colors['accent'])),
            row=2, col=3
        )

        # Update layout
        fig.update_layout(
            title="Network/Relational Data Visualization Types",
            height=800,
            showlegend=True,
            font=dict(size=10)
        )

        # Hide axes for network plots
        for row in [1, 2]:
            for col in [1, 2]:
                fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False, row=row, col=col)
                fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False, row=row, col=col)

        # Keep axes for metrics comparison
        fig.update_xaxes(title_text="Node ID", row=2, col=3)
        fig.update_yaxes(title_text="Normalized Value", row=2, col=3)

        return fig

    def create_spatial_plots(self):
        """Create comprehensive spatial plot examples"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Choropleth Map: Sales per Capita',
                'Scatter Geo: Store Locations',
                'Bubble Map: Market Penetration',
                'Heatmap: Regional Performance',
                'Density Map Style: Customer Distribution',
                'Geographic Network: Supply Chain'
            ),
            specs=[[{"type": "geo"}, {"type": "geo"}, {"type": "geo"}],
                   [{"type": "xy"}, {"type": "xy"}, {"type": "geo"}]],
            vertical_spacing=0.15,
            horizontal_spacing=0.05
        )

        # 1. Choropleth Map
        states_list = list(self.sales_per_capita.keys())
        per_capita_values = list(self.sales_per_capita.values())

        fig.add_trace(
            go.Choropleth(
                locations=states_list,
                z=per_capita_values,
                locationmode='USA-states',
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="Sales per Capita", x=0.32),
                hovertemplate='%{locations}<br>Per Capita: $%{z:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )

        # 2. Scatter Geo (Store Locations)
        store_states = list(self.store_locations.keys())
        store_lats = [self.store_locations[state]['lat'] for state in store_states]
        store_lons = [self.store_locations[state]['lon'] for state in store_states]
        store_counts = [self.store_locations[state]['stores'] for state in store_states]

        fig.add_trace(
            go.Scattergeo(
                lat=store_lats,
                lon=store_lons,
                mode='markers',
                marker=dict(
                    size=[c*2 for c in store_counts],
                    color=self.colors['danger'],
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                text=[f'{state}: {count} stores' for state, count in zip(store_states, store_counts)],
                hovertemplate='%{text}<extra></extra>',
                name='Store Locations'
            ),
            row=1, col=2
        )

        # 3. Bubble Map (Market Penetration)
        # Create more realistic market penetration data
        market_penetration = [25, 18, 32, 15, 28, 22, 19, 35, 12, 30]  # Percentage penetration by state

        fig.add_trace(
            go.Scattergeo(
                lat=store_lats,
                lon=store_lons,
                mode='markers',
                marker=dict(
                    size=[p*2 + 15 for p in market_penetration],  # Reasonable bubble sizes
                    color=market_penetration,
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="Market<br>Penetration (%)", x=1.02, len=0.7),
                    opacity=0.8,
                    line=dict(width=2, color='darkblue'),
                    sizemode='diameter'
                ),
                text=[f'{state}<br>Penetration: {p}%<br>Stores: {stores}'
                      for state, p, stores in zip(store_states, market_penetration, store_counts)],
                hovertemplate='%{text}<extra></extra>',
                name='Market Penetration'
            ),
            row=1, col=3
        )

        # 4. Regional Performance Heatmap
        regions = ['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West']
        quarters = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023']

        # Generate performance matrix
        performance_matrix = np.random.uniform(70, 95, (len(regions), len(quarters)))

        fig.add_trace(
            go.Heatmap(
                z=performance_matrix,
                x=quarters,
                y=regions,
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Performance Score"),
                text=[[f'{val:.1f}' for val in row] for row in performance_matrix],
                texttemplate="%{text}",
                textfont={"size": 11},
                hovertemplate='%{y}<br>%{x}<br>Score: %{z:.1f}<extra></extra>'
            ),
            row=2, col=1
        )

        # 5. Density-style visualization (Customer Distribution)
        # Create synthetic customer density data
        x_coords = np.random.normal(0, 2, 500)
        y_coords = np.random.normal(0, 1.5, 500)

        fig.add_trace(
            go.Histogram2d(
                x=x_coords,
                y=y_coords,
                colorscale='Hot',
                showscale=True,
                colorbar=dict(title="Customer Density"),
                nbinsx=20,
                nbinsy=20,
                hovertemplate='Density: %{z}<extra></extra>'
            ),
            row=2, col=2
        )

        # 6. Geographic Network (Supply Chain)
        # Create supply chain connections
        supply_cities = {
            'Chicago': {'lat': 41.8781, 'lon': -87.6298, 'type': 'hub'},
            'Atlanta': {'lat': 33.7490, 'lon': -84.3880, 'type': 'hub'},
            'Dallas': {'lat': 32.7767, 'lon': -96.7970, 'type': 'hub'},
            'Los Angeles': {'lat': 34.0522, 'lon': -118.2437, 'type': 'distribution'},
            'New York': {'lat': 40.7128, 'lon': -74.0060, 'type': 'distribution'},
            'Seattle': {'lat': 47.6062, 'lon': -122.3321, 'type': 'distribution'}
        }

        # Add supply chain connections as lines
        connections = [
            ('Chicago', 'Atlanta'), ('Chicago', 'Dallas'),
            ('Atlanta', 'New York'), ('Dallas', 'Los Angeles'),
            ('Chicago', 'Seattle'), ('Atlanta', 'Los Angeles')
        ]

        for start, end in connections:
            fig.add_trace(
                go.Scattergeo(
                    lat=[supply_cities[start]['lat'], supply_cities[end]['lat']],
                    lon=[supply_cities[start]['lon'], supply_cities[end]['lon']],
                    mode='lines',
                    line=dict(width=2, color=self.colors['neutral']),
                    showlegend=False,
                    hoverinfo='skip'
                ),
                row=2, col=3
            )

        # Add supply chain nodes
        hub_cities = [city for city, info in supply_cities.items() if info['type'] == 'hub']
        dist_cities = [city for city, info in supply_cities.items() if info['type'] == 'distribution']

        # Hubs
        fig.add_trace(
            go.Scattergeo(
                lat=[supply_cities[city]['lat'] for city in hub_cities],
                lon=[supply_cities[city]['lon'] for city in hub_cities],
                mode='markers+text',
                marker=dict(size=15, color=self.colors['danger'], symbol='square'),
                text=hub_cities,
                textposition='top center',
                name='Hubs',
                hovertemplate='Hub: %{text}<extra></extra>'
            ),
            row=2, col=3
        )

        # Distribution centers
        fig.add_trace(
            go.Scattergeo(
                lat=[supply_cities[city]['lat'] for city in dist_cities],
                lon=[supply_cities[city]['lon'] for city in dist_cities],
                mode='markers+text',
                marker=dict(size=12, color=self.colors['primary'], symbol='circle'),
                text=dist_cities,
                textposition='top center',
                name='Distribution',
                hovertemplate='Distribution: %{text}<extra></extra>'
            ),
            row=2, col=3
        )

        # Update geo layouts
        fig.update_geos(scope="usa", showlakes=False, showrivers=False)

        # Update layout
        fig.update_layout(
            title="Spatial Data Visualization Types",
            height=800,
            showlegend=True,
            font=dict(size=10)
        )

        # Update heatmap axes
        fig.update_xaxes(title_text="Quarter", row=2, col=1)
        fig.update_yaxes(title_text="Region", row=2, col=1)
        fig.update_xaxes(title_text="Longitude", row=2, col=2)
        fig.update_yaxes(title_text="Latitude", row=2, col=2)

        return fig

    def save_figure_as_png(self, fig, filename):
        """Save figure as PNG with proper sizing"""
        filepath = os.path.join(self.output_dir, filename)
        fig.write_image(filepath, width=1600, height=1000, scale=1.2)
        return filepath

    def create_pdf_report(self):
        """Create comprehensive PDF report organized by plot types"""
        pdf_path = os.path.join(self.output_dir, "Visualization_Playbook_By_Plot_Type.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            spaceAfter=30,
            alignment=1,
            textColor=colors.darkblue
        )

        page_title_style = ParagraphStyle(
            'PageTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,
            textColor=colors.black
        )

        notes_style = ParagraphStyle(
            'Notes',
            parent=styles['Normal'],
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            leading=11
        )

        # Cover page
        story.append(Paragraph("Matthew Tonks's Visualization Guide", title_style))
        story.append(Spacer(1, 40))

        # Description
        story.append(Paragraph("Comprehensive Guide to Data Visualization Types", styles['Heading3']))
        story.append(Paragraph("This playbook demonstrates visualization techniques organized by plot type, following Edward Tufte's principles of graphical excellence and Stephen Few's perceptual accuracy guidelines. Each section emphasizes maximizing data-ink ratio, reducing chart junk, and leveraging human visual perception strengths.", styles['Normal']))
        story.append(Spacer(1, 15))

        # Core principles
        story.append(Paragraph("Core Visualization Principles", styles['Heading4']))
        story.append(Paragraph("<b>Tufte's Graphical Excellence:</b> Show the data. Induce the viewer to think about the substance rather than methodology. Avoid distorting what the data has to say. Present many numbers in a small space. Make large data sets coherent. Encourage comparison of different pieces of data.", styles['Normal']))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Few's Perceptual Guidelines:</b> Leverage pre-attentive visual processing. Use position over length, length over angle, angle over area. Design for the colorblind. Reduce cognitive load through direct labeling and intuitive layouts.", styles['Normal']))
        story.append(Spacer(1, 30))

        # Plot type descriptions
        plot_types = [
            ('Categorical Plots', 'Bar charts, pie charts, Pareto analysis for comparing categories and distributions'),
            ('Ordinal Plots', 'Ordered visualizations for ranked data, Likert scales, and progression analysis'),
            ('Quantitative Plots', 'Scatter plots, histograms, box plots for continuous numerical relationships'),
            ('Temporal Plots', 'Time series analysis, trend lines, seasonal patterns, and growth metrics'),
            ('Network Plots', 'Relationship mapping, centrality analysis, hierarchical structures'),
            ('Spatial Plots', 'Geographic visualization, density mapping, regional analysis')
        ]

        # Add page break after introduction
        story.append(PageBreak())

        detailed_notes = {
            'Categorical Plots': """<b>Purpose:</b> Compare discrete categories and their distributions.<br/><br/>
<b>Tufte's Data-Ink Ratio:</b> Maximize information content by removing chart junk. Use direct labeling instead of legends when possible. Eliminate unnecessary grid lines and decorative elements.<br/><br/>
<b>Few's Simplicity Principles:</b><br/>
• Waterfall charts excel at showing cumulative changes - more informative than stacked bars<br/>
• Funnel charts clearly communicate conversion processes<br/>
• Sunburst charts reveal hierarchical patterns impossible to see in flat bar charts<br/>
• Remove pie charts - human visual system poorly estimates angles and areas<br/><br/>
<b>Best Practices:</b> Sort categories by value (not alphabetically). Use consistent color schemes. Direct label values to reduce cognitive load. Start bars at zero baseline to avoid misleading comparisons.""",

            'Ordinal Plots': """<b>Purpose:</b> Visualize ordered categories, rankings, and scales with inherent sequence.<br/><br/>
<b>Tufte's Sparklines Concept:</b> Small multiples and slope charts show change more effectively than complex multi-series plots. Remove chart borders and excess annotation.<br/><br/>
<b>Few's Perceptual Guidelines:</b><br/>
• Slope charts reveal changes better than line charts for discrete time points<br/>
• Heatmaps encode magnitude through color intensity - use sequential color schemes<br/>
• Dot plots often superior to bar charts for ordered categories<br/>
• Violin plots show distribution shape that box plots cannot capture<br/><br/>
<b>Best Practices:</b> Maintain natural ordering. Use position over color for primary comparisons. Include reference lines for context (medians, targets). Gray out less important data to highlight key insights.""",

            'Quantitative Plots': """<b>Purpose:</b> Explore relationships, distributions, and patterns in continuous numerical data.<br/><br/>
<b>Tufte's Analytical Focus:</b> Show statistical relationships clearly. Use small multiples to compare distributions across groups. Minimize non-data ink - let the data patterns dominate.<br/><br/>
<b>Few's Accuracy Principles:</b><br/>
• Scatter plots reveal correlations that tables cannot show<br/>
• Box plots compress distribution information efficiently<br/>
• Histograms show shape - normal, skewed, bimodal distributions<br/>
• Avoid 3D effects and unnecessary depth that distort perception<br/><br/>
<b>Best Practices:</b> Include trend lines for relationships. Mark outliers clearly. Use logarithmic scales when data spans orders of magnitude. Add rug plots to show actual data points beneath density curves.""",

            'Temporal Plots': """<b>Purpose:</b> Reveal patterns, trends, cycles, and anomalies in time-ordered data.<br/><br/>
<b>Tufte's Time-Series Excellence:</b> Time moves left to right - never violate this convention. Remove unnecessary time axis labels. Use horizon charts for small multiples with many series.<br/><br/>
<b>Few's Temporal Clarity:</b><br/>
• Moving averages smooth noise to reveal underlying trends<br/>
• Multiple time series require careful color differentiation<br/>
• Seasonal patterns need consistent baseline years for comparison<br/>
• Event markers provide crucial business context<br/><br/>
<b>Best Practices:</b> Start time axis at meaningful baseline. Use aspect ratios that don't exaggerate volatility. Annotate significant events directly on timeline. Consider cycle charts for seasonal data.""",

            'Network Plots': """<b>Purpose:</b> Visualize relationships, connections, and structures between entities.<br/><br/>
<b>Tufte's Network Principles:</b> Minimize edge crossings. Use node size to encode importance. Keep layouts consistent for comparison. Remove isolated nodes unless specifically relevant.<br/><br/>
<b>Few's Relationship Clarity:</b><br/>
• Force-directed layouts reveal natural clustering<br/>
• Circular layouts work well for hierarchical relationships<br/>
• Bipartite networks separate entity types clearly<br/>
• Matrix representations often clearer than node-link for dense networks<br/><br/>
<b>Best Practices:</b> Color-code node types consistently. Use edge thickness for relationship strength. Include centrality measures for business relevance. Consider matrix view for complex networks with many connections.""",

            'Spatial Plots': """<b>Purpose:</b> Analyze geographic patterns, regional differences, and location-based business metrics.<br/><br/>
<b>Tufte's Geographic Accuracy:</b> Maintain geographic proportions. Use choropleth maps for normalized data only. Avoid misleading area distortions. Include per-capita adjustments for population-based metrics.<br/><br/>
<b>Few's Spatial Guidelines:</b><br/>
• Bubble maps better than choropleth for absolute values<br/>
• Density maps reveal patterns invisible in point data<br/>
• Supply chain networks show business flow geography<br/>
• Color schemes must be intuitive (red=bad, green=good)<br/><br/>
<b>Best Practices:</b> Normalize by population/area when appropriate. Use consistent geographic projections. Include reference points (major cities). Design for colorblind accessibility with diverging palettes."""
        }

        # Create figures and add to PDF
        plot_functions = [
            (self.create_categorical_plots, "Categorical Plots", "categorical_plots.png"),
            (self.create_ordinal_plots, "Ordinal Plots", "ordinal_plots.png"),
            (self.create_quantitative_plots, "Quantitative Plots", "quantitative_plots.png"),
            (self.create_temporal_plots, "Temporal Plots", "temporal_plots.png"),
            (self.create_network_plots, "Network Plots", "network_plots.png"),
            (self.create_spatial_plots, "Spatial Plots", "spatial_plots.png")
        ]

        png_paths = []

        for plot_func, title, filename in plot_functions:
            # Create figure
            fig = plot_func()

            # Save as PNG
            png_path = self.save_figure_as_png(fig, filename)
            png_paths.append(png_path)

            # Add page to PDF
            story.append(Paragraph(title, page_title_style))
            story.append(Spacer(1, 0.3*inch))

            # Add image
            img = Image(png_path, width=7.5*inch, height=4.7*inch)
            story.append(img)
            story.append(Spacer(1, 20))

            # Add detailed notes
            story.append(Paragraph("Plot Type Analysis:", styles['Heading4']))
            story.append(Paragraph(detailed_notes[title], notes_style))
            story.append(Spacer(1, 30))

            # Add page break after each plot type (except the last one)
            if title != "Spatial Plots":
                story.append(PageBreak())

        # Build PDF
        doc.build(story)

        print(f"Plot Type PDF created: {pdf_path}")
        print(f"PNG files created: {len(png_paths)} images in {self.output_dir}/")
        for png_path in png_paths:
            print(f"  - {os.path.basename(png_path)}")

        return pdf_path, png_paths

def main():
    """Main execution function for plot type playbook"""
    print("Creating Matthew Tonks's Visualization Guide...")
    print("Features: Comprehensive plot type examples with business context")
    print("Dependencies: plotly, kaleido, reportlab, networkx, numpy, pandas")
    print()

    # Create plot type playbook
    playbook = PlotTypeVisualizationPlaybook()

    # Generate PDF and PNGs
    pdf_path, png_paths = playbook.create_pdf_report()

    print()
    print("Plot Type Visualization Playbook created successfully!")
    print(f"PDF: {pdf_path}")
    print(f"PNG files: {len(png_paths)} comprehensive visualization examples")
    print()
    print("Organization:")
    print("- 6 major plot type categories")
    print("- 18 different visualization techniques")
    print("- Business-focused examples and use cases")
    print("- Professional styling and annotations")

if __name__ == "__main__":
    main()