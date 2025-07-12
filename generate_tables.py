import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np
import json
import os

def create_high_quality_table_image(data, title, filename, figsize=(12, 8)):
    """Create a high-quality table image with better formatting"""
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # Prepare data for table
    if isinstance(data, dict):
        # Handle JSON data
        df = pd.DataFrame(data['data'], columns=data['columns'], index=data['index'])
    else:
        df = data
    
    # Get table dimensions
    n_rows, n_cols = df.shape
    
    # Create table
    table = ax.table(cellText=df.values.tolist(),
                    colLabels=df.columns.tolist(),
                    rowLabels=df.index.tolist(),
                    cellLoc='center',
                    loc='center')
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    
    # Color the header row
    for i in range(n_cols):
        table[(0, i)].set_facecolor('#4A90E2')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color the index column
    for i in range(n_rows):
        table[(i+1, -1)].set_facecolor('#F5F5F5')
        table[(i+1, -1)].set_text_props(weight='bold')
    
    # Color alternating rows
    for i in range(n_rows):
        if i % 2 == 0:
            for j in range(n_cols):
                table[(i+1, j)].set_facecolor('#F9F9F9')
    
    # Add borders (simplified)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    
    # Add title
    plt.title(title, fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save with high DPI
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def main():
    """Generate all table images"""
    
    # Load the data
    df = pd.read_csv('master_data_restricted.csv')
    
    # Clean and prepare variables
    df['employed_binary'] = (df['employed'] == 'Employed').astype(int)
    df['employed_label'] = df['employed_binary'].replace({1: 'Employed', 0: 'Not Employed'})
    df['tvet_binary'] = (df['tvet'] == 'Enrolled').astype(int)
    df['tvet_label'] = df['tvet_binary'].replace({1: 'TVET Enrolled', 0: 'Not Enrolled'})
    df['Education'] = df['Education'].fillna('Missing')
    df['EMP_HR03'] = df['EMP_HR03'].fillna('Missing')
    df['RU'] = df['RU'].fillna('Missing')
    
    # Table 2: Employment Status by TVET Participation
    print("Generating Table 2...")
    table2_freq = pd.crosstab(df['employed_label'], df['tvet_label'], margins=True, margins_name='Total')
    create_high_quality_table_image(
        table2_freq, 
        'Table 2: Employment Status by TVET Participation\n(Frequency Distribution)', 
        'table2_employment_by_tvet.jpg',
        figsize=(10, 6)
    )
    
    table2_pct = pd.crosstab(df['employed_label'], df['tvet_label'], normalize='index') * 100
    table2_pct = table2_pct.round(1)
    create_high_quality_table_image(
        table2_pct, 
        'Table 2: Employment Status by TVET Participation\n(Row Percentages)', 
        'table2_employment_by_tvet_rowpct.jpg',
        figsize=(8, 3)
    )
    
    # Table 3: Education Level by TVET Participation (Only None and Primary)
    print("Generating Table 3...")
    # Filter for only None and Primary education
    df_filtered = df[df['Education'].isin(['0 - None', '1 - primary'])]
    
    table3_freq = pd.crosstab(df_filtered['Education'], df_filtered['tvet_label'], margins=True, margins_name='Total')
    create_high_quality_table_image(
        table3_freq, 
        'Table 3: Education Level by TVET Participation\n(Frequency Distribution - None & Primary Only)', 
        'table3_education_by_tvet.jpg',
        figsize=(10, 6)
    )
    
    table3_pct = pd.crosstab(df_filtered['Education'], df_filtered['tvet_label'], normalize='index') * 100
    create_high_quality_table_image(
        table3_pct, 
        'Table 3: Education Level by TVET Participation\n(Row Percentages - None & Primary Only)', 
        'table3_education_by_tvet_rowpct.jpg',
        figsize=(10, 6)
    )
    
    # Table 4A: Employment Status by Gender
    print("Generating Table 4A...")
    table4a_freq = pd.crosstab(df['employed_label'], df['EMP_HR03'], margins=True, margins_name='Total')
    create_high_quality_table_image(
        table4a_freq, 
        'Table 4A: Employment Status by Gender\n(Frequency Distribution)', 
        'table4a_employment_by_gender.jpg',
        figsize=(12, 6)
    )
    
    table4a_pct = pd.crosstab(df['employed_label'], df['EMP_HR03'], normalize='index') * 100
    create_high_quality_table_image(
        table4a_pct, 
        'Table 4A: Employment Status by Gender\n(Row Percentages)', 
        'table4a_employment_by_gender_rowpct.jpg',
        figsize=(12, 6)
    )
    
    # Table 4B: Employment Status by Location
    print("Generating Table 4B...")
    table4b_freq = pd.crosstab(df['employed_label'], df['RU'], margins=True, margins_name='Total')
    create_high_quality_table_image(
        table4b_freq, 
        'Table 4B: Employment Status by Location\n(Frequency Distribution)', 
        'table4b_employment_by_location.jpg',
        figsize=(12, 6)
    )
    
    table4b_pct = pd.crosstab(df['employed_label'], df['RU'], normalize='index') * 100
    create_high_quality_table_image(
        table4b_pct, 
        'Table 4B: Employment Status by Location\n(Row Percentages)', 
        'table4b_employment_by_location_rowpct.jpg',
        figsize=(12, 6)
    )
    
    print("All table images generated successfully!")

if __name__ == "__main__":
    main() 