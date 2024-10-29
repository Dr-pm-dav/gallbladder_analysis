import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import base64
from io import BytesIO

class GallbladderDashboard:
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            filename='dashboard.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize data containers
        self.processed_data = {}
        self.analysis_results = {}
        self.load_data()
        
        # Initialize Dash app
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()

    def load_data(self):
        """
        Load processed data and analysis results
        """
        try:
            # Load processed data
            for dataset in ['pubmed', 'hospital', 'statistics', 'analysis']:
                self.processed_data[dataset] = pd.read_csv(
                    f'data/processed_data/{dataset}_processed.csv'
                )
            
            # Load analysis results
            with open('data/analysis_results/analysis_results.json', 'r') as f:
                self.analysis_results = json.load(f)
                
            logging.info("Data loaded successfully")
            
        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            raise

    def setup_layout(self):
        """
        Set up the dashboard layout
        """
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Gallbladder Surgery Analysis Dashboard",
                        style={'textAlign': 'center'}),
                html.Hr()
            ]),
            
            # Main content
            html.Div([
                # Filters
                html.Div([
                    html.H3("Filters"),
                    dcc.Dropdown(
                        id='location-filter',
                        options=[
                            {'label': loc, 'value': loc}
                            for loc in self.processed_data['hospital']['location'].unique()
                        ],
                        multi=True,
                        placeholder="Select locations..."
                    ),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date=self.processed_data['hospital']['date'].min(),
                        end_date=self.processed_data['hospital']['date'].max()
                    )
                ], style={'width': '25%', 'float': 'left', 'padding': '20px'}),
                
                # Main charts area
                html.Div([
                    # Temporal Analysis
                    html.Div([
                        html.H3("Temporal Analysis"),
                        dcc.Graph(id='temporal-chart')
                    ]),
                    
                    # Geographical Analysis
                    html.Div([
                        html.H3("Geographical Analysis"),
                        dcc.Graph(id='geographical-chart')
                    ]),
                    
                    # Correlation Analysis
                    html.Div([
                        html.H3("Correlation Analysis"),
                        dcc.Graph(id='correlation-chart')
                    ]),
                    
                    # Cluster Analysis
                    html.Div([
                        html.H3("Cluster Analysis"),
                        dcc.Graph(id='cluster-chart')
                    ])
                ], style={'width': '75%', 'float': 'right'})
            ]),
            
            # Footer with export options
            html.Div([
                html.Hr(),
                html.Button('Generate PDF Report', id='generate-report'),
                html.Div(id='report-status')
            ])
        ])

    def setup_callbacks(self):
        """
        Set up interactive callbacks
        """
        @self.app.callback(
            [Output('temporal-chart', 'figure'),
             Output('geographical-chart', 'figure'),
             Output('correlation-chart', 'figure'),
             Output('cluster-chart', 'figure')],
            [Input('location-filter', 'value'),
             Input('date-range', 'start_date'),
             Input('date-range', 'end_date')]
        )
        def update_charts(locations, start_date, end_date):
            return (
                self.create_temporal_chart(locations, start_date, end_date),
                self.create_geographical_chart(locations),
                self.create_correlation_chart(),
                self.create_cluster_chart()
            )
        
        @self.app.callback(
            Output('report-status', 'children'),
            Input('generate-report', 'n_clicks')
        )
        def generate_report(n_clicks):
            if n_clicks:
                try:
                    self.create_pdf_report()
                    return "Report generated successfully!"
                except Exception as e:
                    return f"Error generating report: {str(e)}"
            return ""

    def create_temporal_chart(self, locations, start_date, end_date):
        """
        Create temporal analysis chart
        """
        df = self.processed_data['hospital']
        if locations:
            df = df[df['location'].isin(locations)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['surgery_count'],
            mode='lines+markers',
            name='Surgery Count'
        ))
        
        fig.update_layout(
            title='Surgery Count Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Surgeries'
        )
        
        return fig

    def create_geographical_chart(self, locations):
        """
        Create geographical analysis chart
        """
        df = self.processed_data['hospital']
        
        fig = px.box(
            df,
            x='location',
            y='surgery_count',
            title='Surgery Distribution by Location'
        )
        
        return fig

    def create_correlation_chart(self):
        """
        Create correlation analysis chart
        """
        corr_matrix = pd.DataFrame(self.analysis_results['correlation']['correlation_matrix'])
        
        fig = px.imshow(
            corr_matrix,
            title='Correlation Matrix',
            color_continuous_scale='RdBu'
        )
        
        return fig

    def create_cluster_chart(self):
        """
        Create cluster analysis chart
        """
        clusters = self.analysis_results['clustering']
        
        fig = px.scatter(
            self.processed_data['analysis'],
            x='surgery_count',
            y='mean_value',
            color='cluster_labels',
            title='Cluster Analysis'
        )
        
        return fig

    def create_pdf_report(self):
        """
        Generate PDF report with analysis results
        """
        doc = SimpleDocTemplate(
            "data/analysis_results/gallbladder_analysis_report.pdf",
            pagesize=letter
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph(
            "Gallbladder Surgery Analysis Report",
            styles['Title']
        ))
        elements.append(Spacer(1, 12))
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", styles['Heading1']))
        elements.append(Paragraph(
            "This report presents the analysis of gallbladder surgery data...",
            styles['Normal']
        ))
        
        # Add charts
        for chart_name in ['temporal', 'geographical', 'correlation', 'cluster']:
            elements.append(Paragraph(
                f"{chart_name.title()} Analysis",
                styles['Heading2']
            ))
            
            # Save chart as image and add to PDF
            img_path = f'data/analysis_results/figures/{chart_name}_analysis.png'
            if os.path.exists(img_path):
                elements.append(Image(img_path, width=400, height=300))
            
            elements.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(elements)
        logging.info("PDF report generated successfully")

def main():
    # Initialize dashboard
    dashboard = GallbladderDashboard()
    
    # Run server
    dashboard.app.run_server(debug=True)

if __name__ == "__main__":
    main()