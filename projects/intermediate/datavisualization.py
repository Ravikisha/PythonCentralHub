# Data Visualization with Matplotlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import seaborn as sns
import json
from typing import List, Dict, Optional
import random

class DataVisualizer:
    def __init__(self):
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Sample data
        self.sample_data = self.generate_sample_data()
        
    def generate_sample_data(self) -> Dict:
        """Generate sample data for visualization"""
        # Sales data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        sales_2022 = [random.randint(10000, 50000) for _ in months]
        sales_2023 = [random.randint(12000, 55000) for _ in months]
        
        # Student scores
        students = [f"Student {i}" for i in range(1, 21)]
        math_scores = [random.randint(60, 100) for _ in students]
        science_scores = [random.randint(55, 95) for _ in students]
        english_scores = [random.randint(65, 100) for _ in students]
        
        # Stock data
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        stock_prices = []
        price = 100
        for _ in dates:
            price += random.uniform(-5, 5)
            stock_prices.append(max(price, 10))  # Ensure positive price
        
        # Survey data
        age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        responses = [random.randint(50, 200) for _ in age_groups]
        
        # Weather data
        days = [f"Day {i}" for i in range(1, 8)]
        temperatures = [random.randint(15, 35) for _ in days]
        humidity = [random.randint(30, 80) for _ in days]
        
        return {
            'sales': {'months': months, '2022': sales_2022, '2023': sales_2023},
            'students': {'names': students, 'math': math_scores, 'science': science_scores, 'english': english_scores},
            'stock': {'dates': dates, 'prices': stock_prices},
            'survey': {'age_groups': age_groups, 'responses': responses},
            'weather': {'days': days, 'temperature': temperatures, 'humidity': humidity}
        }
    
    def create_line_chart(self, save=True):
        """Create a line chart showing sales trends"""
        plt.figure(figsize=(12, 6))
        
        months = self.sample_data['sales']['months']
        sales_2022 = self.sample_data['sales']['2022']
        sales_2023 = self.sample_data['sales']['2023']
        
        plt.plot(months, sales_2022, marker='o', linewidth=2, label='2022', color='#3498db')
        plt.plot(months, sales_2023, marker='s', linewidth=2, label='2023', color='#e74c3c')
        
        plt.title('Monthly Sales Comparison (2022 vs 2023)', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Sales ($)', fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        
        # Format y-axis to show values in thousands
        plt.ticklabel_format(style='plain', axis='y')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save:
            plt.savefig('sales_comparison.png', dpi=300, bbox_inches='tight')
            print("Line chart saved as 'sales_comparison.png'")
        
        plt.show()
    
    def create_bar_chart(self, save=True):
        """Create a bar chart showing student scores"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        students = self.sample_data['students']['names'][:10]  # First 10 students
        math_scores = self.sample_data['students']['math'][:10]
        science_scores = self.sample_data['students']['science'][:10]
        english_scores = self.sample_data['students']['english'][:10]
        
        # Grouped bar chart
        x = np.arange(len(students))
        width = 0.25
        
        ax1.bar(x - width, math_scores, width, label='Math', color='#3498db', alpha=0.8)
        ax1.bar(x, science_scores, width, label='Science', color='#e74c3c', alpha=0.8)
        ax1.bar(x + width, english_scores, width, label='English', color='#2ecc71', alpha=0.8)
        
        ax1.set_title('Student Scores by Subject', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Students', fontsize=12)
        ax1.set_ylabel('Scores', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(students, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Average scores bar chart
        subjects = ['Math', 'Science', 'English']
        avg_scores = [
            np.mean(self.sample_data['students']['math']),
            np.mean(self.sample_data['students']['science']),
            np.mean(self.sample_data['students']['english'])
        ]
        
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        bars = ax2.bar(subjects, avg_scores, color=colors, alpha=0.8)
        
        ax2.set_title('Average Scores by Subject', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Average Score', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, score in zip(bars, avg_scores):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            plt.savefig('student_scores.png', dpi=300, bbox_inches='tight')
            print("Bar chart saved as 'student_scores.png'")
        
        plt.show()
    
    def create_pie_chart(self, save=True):
        """Create pie charts showing survey data"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Age group responses
        age_groups = self.sample_data['survey']['age_groups']
        responses = self.sample_data['survey']['responses']
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(age_groups)))
        
        wedges, texts, autotexts = ax1.pie(responses, labels=age_groups, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        
        ax1.set_title('Survey Responses by Age Group', fontsize=14, fontweight='bold')
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Market share pie chart (example data)
        companies = ['Company A', 'Company B', 'Company C', 'Company D', 'Others']
        market_share = [30, 25, 20, 15, 10]
        
        explode = (0.1, 0, 0, 0, 0)  # explode 1st slice
        
        wedges2, texts2, autotexts2 = ax2.pie(market_share, labels=companies, autopct='%1.1f%%',
                                             explode=explode, shadow=True, startangle=90)
        
        ax2.set_title('Market Share Distribution', fontsize=14, fontweight='bold')
        
        # Make percentage text bold
        for autotext in autotexts2:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        if save:
            plt.savefig('pie_charts.png', dpi=300, bbox_inches='tight')
            print("Pie charts saved as 'pie_charts.png'")
        
        plt.show()
    
    def create_scatter_plot(self, save=True):
        """Create scatter plots showing correlations"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Student scores correlation
        math_scores = self.sample_data['students']['math']
        science_scores = self.sample_data['students']['science']
        english_scores = self.sample_data['students']['english']
        
        ax1.scatter(math_scores, science_scores, alpha=0.6, s=60, color='#3498db', label='Math vs Science')
        ax1.scatter(math_scores, english_scores, alpha=0.6, s=60, color='#e74c3c', label='Math vs English')
        
        ax1.set_xlabel('Math Scores', fontsize=12)
        ax1.set_ylabel('Other Subject Scores', fontsize=12)
        ax1.set_title('Student Scores Correlation', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Temperature vs Humidity
        temperature = self.sample_data['weather']['temperature']
        humidity = self.sample_data['weather']['humidity']
        
        # Create color map based on temperature
        colors = plt.cm.coolwarm(np.linspace(0, 1, len(temperature)))
        
        scatter = ax2.scatter(temperature, humidity, c=temperature, cmap='coolwarm', 
                             s=100, alpha=0.7, edgecolors='black', linewidth=1)
        
        ax2.set_xlabel('Temperature (°C)', fontsize=12)
        ax2.set_ylabel('Humidity (%)', fontsize=12)
        ax2.set_title('Temperature vs Humidity', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Temperature (°C)', fontsize=10)
        
        plt.tight_layout()
        
        if save:
            plt.savefig('scatter_plots.png', dpi=300, bbox_inches='tight')
            print("Scatter plots saved as 'scatter_plots.png'")
        
        plt.show()
    
    def create_histogram(self, save=True):
        """Create histograms showing data distribution"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Math scores distribution
        math_scores = self.sample_data['students']['math']
        ax1.hist(math_scores, bins=10, alpha=0.7, color='#3498db', edgecolor='black')
        ax1.set_title('Math Scores Distribution', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Score')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Add mean line
        mean_math = np.mean(math_scores)
        ax1.axvline(mean_math, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_math:.1f}')
        ax1.legend()
        
        # Stock prices distribution
        stock_prices = self.sample_data['stock']['prices']
        ax2.hist(stock_prices, bins=15, alpha=0.7, color='#2ecc71', edgecolor='black')
        ax2.set_title('Stock Prices Distribution', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Price ($)')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        # Temperature distribution
        temperature = self.sample_data['weather']['temperature']
        ax3.hist(temperature, bins=8, alpha=0.7, color='#e74c3c', edgecolor='black')
        ax3.set_title('Temperature Distribution', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Temperature (°C)')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)
        
        # Combined scores distribution
        all_scores = (self.sample_data['students']['math'] + 
                     self.sample_data['students']['science'] + 
                     self.sample_data['students']['english'])
        
        ax4.hist(all_scores, bins=20, alpha=0.7, color='#9b59b6', edgecolor='black')
        ax4.set_title('All Scores Distribution', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Score')
        ax4.set_ylabel('Frequency')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            plt.savefig('histograms.png', dpi=300, bbox_inches='tight')
            print("Histograms saved as 'histograms.png'")
        
        plt.show()
    
    def create_heatmap(self, save=True):
        """Create a heatmap showing correlation matrix"""
        # Create correlation data
        students_df = pd.DataFrame({
            'Math': self.sample_data['students']['math'],
            'Science': self.sample_data['students']['science'],
            'English': self.sample_data['students']['english']
        })
        
        # Calculate correlation matrix
        correlation_matrix = students_df.corr()
        
        plt.figure(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8})
        
        plt.title('Subject Scores Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
        
        if save:
            plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
            print("Heatmap saved as 'correlation_heatmap.png'")
        
        plt.show()
    
    def create_time_series(self, save=True):
        """Create time series plot for stock prices"""
        plt.figure(figsize=(14, 8))
        
        dates = self.sample_data['stock']['dates']
        prices = self.sample_data['stock']['prices']
        
        plt.plot(dates, prices, linewidth=2, color='#3498db', marker='o', markersize=4)
        
        # Fill area under the curve
        plt.fill_between(dates, prices, alpha=0.3, color='#3498db')
        
        plt.title('Stock Price Movement (30 Days)', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format dates on x-axis
        plt.xticks(rotation=45)
        
        # Add trend line
        x_numeric = np.arange(len(dates))
        z = np.polyfit(x_numeric, prices, 1)
        p = np.poly1d(z)
        plt.plot(dates, p(x_numeric), "r--", alpha=0.8, linewidth=2, label=f'Trend')
        
        plt.legend()
        plt.tight_layout()
        
        if save:
            plt.savefig('stock_timeseries.png', dpi=300, bbox_inches='tight')
            print("Time series plot saved as 'stock_timeseries.png'")
        
        plt.show()
    
    def create_subplots_dashboard(self, save=True):
        """Create a comprehensive dashboard with multiple plots"""
        fig = plt.figure(figsize=(16, 12))
        
        # Layout: 3x3 grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Sales line chart
        ax1 = fig.add_subplot(gs[0, :2])
        months = self.sample_data['sales']['months']
        sales_2022 = self.sample_data['sales']['2022']
        sales_2023 = self.sample_data['sales']['2023']
        
        ax1.plot(months, sales_2022, marker='o', label='2022', color='#3498db')
        ax1.plot(months, sales_2023, marker='s', label='2023', color='#e74c3c')
        ax1.set_title('Monthly Sales Trend', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Age group pie chart
        ax2 = fig.add_subplot(gs[0, 2])
        age_groups = self.sample_data['survey']['age_groups']
        responses = self.sample_data['survey']['responses']
        ax2.pie(responses, labels=age_groups, autopct='%1.0f%%', textprops={'fontsize': 8})
        ax2.set_title('Age Distribution', fontweight='bold')
        
        # 3. Scores bar chart
        ax3 = fig.add_subplot(gs[1, :2])
        subjects = ['Math', 'Science', 'English']
        avg_scores = [
            np.mean(self.sample_data['students']['math']),
            np.mean(self.sample_data['students']['science']),
            np.mean(self.sample_data['students']['english'])
        ]
        
        bars = ax3.bar(subjects, avg_scores, color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7)
        ax3.set_title('Average Subject Scores', fontweight='bold')
        ax3.set_ylabel('Score')
        
        # Add value labels
        for bar, score in zip(bars, avg_scores):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Temperature scatter
        ax4 = fig.add_subplot(gs[1, 2])
        temperature = self.sample_data['weather']['temperature']
        humidity = self.sample_data['weather']['humidity']
        ax4.scatter(temperature, humidity, c=temperature, cmap='coolwarm', s=50, alpha=0.7)
        ax4.set_title('Temp vs Humidity', fontweight='bold')
        ax4.set_xlabel('Temperature')
        ax4.set_ylabel('Humidity')
        
        # 5. Stock prices
        ax5 = fig.add_subplot(gs[2, :])
        dates = self.sample_data['stock']['dates']
        prices = self.sample_data['stock']['prices']
        ax5.plot(dates, prices, color='#2ecc71', linewidth=2)
        ax5.fill_between(dates, prices, alpha=0.3, color='#2ecc71')
        ax5.set_title('Stock Price Movement', fontweight='bold')
        ax5.set_xlabel('Date')
        ax5.set_ylabel('Price ($)')
        ax5.tick_params(axis='x', rotation=45)
        ax5.grid(True, alpha=0.3)
        
        plt.suptitle('Data Visualization Dashboard', fontsize=20, fontweight='bold', y=0.95)
        
        if save:
            plt.savefig('dashboard.png', dpi=300, bbox_inches='tight')
            print("Dashboard saved as 'dashboard.png'")
        
        plt.show()
    
    def load_custom_data(self, filename: str) -> Optional[pd.DataFrame]:
        """Load custom data from CSV file"""
        try:
            df = pd.read_csv(filename)
            print(f"Loaded data from {filename}")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def save_sample_data(self):
        """Save sample data to CSV files for user to experiment with"""
        try:
            # Save sales data
            sales_df = pd.DataFrame({
                'Month': self.sample_data['sales']['months'],
                'Sales_2022': self.sample_data['sales']['2022'],
                'Sales_2023': self.sample_data['sales']['2023']
            })
            sales_df.to_csv('sample_sales_data.csv', index=False)
            
            # Save student data
            students_df = pd.DataFrame({
                'Student': self.sample_data['students']['names'],
                'Math': self.sample_data['students']['math'],
                'Science': self.sample_data['students']['science'],
                'English': self.sample_data['students']['english']
            })
            students_df.to_csv('sample_student_data.csv', index=False)
            
            # Save stock data
            stock_df = pd.DataFrame({
                'Date': [d.strftime('%Y-%m-%d') for d in self.sample_data['stock']['dates']],
                'Price': self.sample_data['stock']['prices']
            })
            stock_df.to_csv('sample_stock_data.csv', index=False)
            
            print("Sample data saved to CSV files:")
            print("- sample_sales_data.csv")
            print("- sample_student_data.csv")
            print("- sample_stock_data.csv")
            
        except Exception as e:
            print(f"Error saving sample data: {e}")

def main():
    """Main function to run the data visualization app"""
    visualizer = DataVisualizer()
    
    while True:
        print("\n=== Data Visualization with Matplotlib ===")
        print("1. Line Chart (Sales Trends)")
        print("2. Bar Chart (Student Scores)")
        print("3. Pie Chart (Survey Data)")
        print("4. Scatter Plot (Correlations)")
        print("5. Histogram (Data Distribution)")
        print("6. Heatmap (Correlation Matrix)")
        print("7. Time Series (Stock Prices)")
        print("8. Dashboard (Multiple Plots)")
        print("9. Save Sample Data to CSV")
        print("10. Load Custom Data")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                visualizer.create_line_chart()
                
            elif choice == '2':
                visualizer.create_bar_chart()
                
            elif choice == '3':
                visualizer.create_pie_chart()
                
            elif choice == '4':
                visualizer.create_scatter_plot()
                
            elif choice == '5':
                visualizer.create_histogram()
                
            elif choice == '6':
                visualizer.create_heatmap()
                
            elif choice == '7':
                visualizer.create_time_series()
                
            elif choice == '8':
                visualizer.create_subplots_dashboard()
                
            elif choice == '9':
                visualizer.save_sample_data()
                
            elif choice == '10':
                filename = input("Enter CSV filename: ").strip()
                if filename:
                    df = visualizer.load_custom_data(filename)
                    if df is not None:
                        print("\nFirst 5 rows:")
                        print(df.head())
                        print("\nData types:")
                        print(df.dtypes)
                
            elif choice == '0':
                print("Thank you for using the Data Visualization app!")
                break
                
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
