import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import seaborn as sns
import json
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the labor force survey data"""
    print("Loading data...")
    df = pd.read_csv('master_data_restricted.csv')
    
    # Clean and prepare variables
    # Employment status - check actual values first
    print("Employment status values:", df['employed'].value_counts())
    print("TVET values:", df['tvet'].value_counts())
    
    # Create binary employment variable
    df['employed_binary'] = (df['employed'] == 'Employed').astype(int)
    df['employed_label'] = df['employed_binary'].replace({1: 'Employed', 0: 'Not Employed'})
    
    # Create binary TVET variable
    df['tvet_binary'] = (df['tvet'] == 'Enrolled').astype(int)
    df['tvet_label'] = df['tvet_binary'].replace({1: 'TVET Enrolled', 0: 'Not Enrolled'})
    
    # Education level
    df['Education'] = df['Education'].fillna('Missing')
    
    # Gender
    df['EMP_HR03'] = df['EMP_HR03'].fillna('Missing')
    
    # Location (Rural/Urban)
    df['RU'] = df['RU'].fillna('Missing')
    
    return df

def create_cross_tabulation(df, var1, var2, var1_name, var2_name):
    """Create cross-tabulation with row percentages and chi-square test"""
    
    # Create contingency table
    crosstab = pd.crosstab(df[var1], df[var2], margins=True, margins_name='Total')
    
    # Calculate row percentages
    row_percentages = pd.crosstab(df[var1], df[var2], normalize='index') * 100
    
    # Chi-square test
    contingency_table = pd.crosstab(df[var1], df[var2])
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return crosstab, row_percentages, chi2, p_value, dof

def format_table(crosstab, row_percentages, chi2, p_value, dof, var1_name, var2_name):
    """Format the table for display"""
    
    print(f"\n{'='*80}")
    print(f"Table: {var1_name} by {var2_name}")
    print(f"{'='*80}")
    
    # Display frequency table
    print(f"\nFrequency Distribution:")
    print(f"{'':<20}", end="")
    for col in crosstab.columns:
        print(f"{col:<15}", end="")
    print()
    print("-" * 80)
    
    for idx, row in crosstab.iterrows():
        print(f"{idx:<20}", end="")
        for col in crosstab.columns:
            print(f"{row[col]:<15}", end="")
        print()
    
    # Display row percentages
    print(f"\nRow Percentages:")
    print(f"{'':<20}", end="")
    for col in row_percentages.columns:
        print(f"{col:<15}", end="")
    print()
    print("-" * 80)
    
    for idx, row in row_percentages.iterrows():
        print(f"{idx:<20}", end="")
        for col in row_percentages.columns:
            print(f"{row[col]:.1f}%{'':<10}", end="")
        print()
    
    # Display chi-square test results
    print(f"\nChi-Square Test for Independence:")
    print(f"Chi-square statistic: {chi2:.4f}")
    print(f"p-value: {p_value:.4f}")
    print(f"Degrees of freedom: {dof}")
    
    if p_value < 0.001:
        significance = "***"
    elif p_value < 0.01:
        significance = "**"
    elif p_value < 0.05:
        significance = "*"
    else:
        significance = "Not significant"
    
    print(f"Significance: {significance}")
    
    return {
        'frequencies': crosstab,
        'percentages': row_percentages,
        'chi2': chi2,
        'p_value': p_value,
        'significance': significance
    }

def save_table_image(table, name, title=None):
    fig, ax = plt.subplots(figsize=(min(20, 2 + 0.8*table.shape[1]), 1 + 0.5*table.shape[0]))
    ax.axis('off')
    tbl = ax.table(cellText=table.values,
                   colLabels=table.columns,
                   rowLabels=table.index,
                   loc='center',
                   cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 1.2)
    if title:
        plt.title(title, fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(f'{name}.jpg', bbox_inches='tight', dpi=200)
    plt.close()

def save_table(table, name, title=None):
    # Save as CSV
    table.to_csv(f'{name}.csv')
    # Save as JSON
    table.to_json(f'{name}.json', orient='split')
    # Save as JPG image
    save_table_image(table, name, title)

def plot_figure_1(df):
    # Bar chart of employment rate by TVET status
    rate = df.groupby('tvet_label')['employed_binary'].mean().reset_index()
    plt.figure(figsize=(6,4))
    sns.barplot(x='tvet_label', y='employed_binary', data=rate, palette='Set2')
    plt.ylabel('Employment Rate')
    plt.xlabel('TVET Status')
    plt.title('Employment Rate by TVET Status')
    plt.ylim(0,1)
    plt.savefig('figure1_employment_by_tvet.png', bbox_inches='tight')
    plt.close()

def plot_figure_2(df):
    # Education distribution by TVET status (only None and Primary)
    edu_order = ['0 - None', '1 - primary']
    df_filtered = df[df['Education'].isin(edu_order)]
    plt.figure(figsize=(8,6))
    sns.countplot(data=df_filtered, x='Education', hue='tvet_label', order=edu_order)
    plt.xlabel('Education Level')
    plt.ylabel('Count')
    plt.title('Education Distribution by TVET Status (None & Primary Only)')
    plt.legend(title='TVET Status')
    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    plt.savefig('figure2_education_by_tvet.png', bbox_inches='tight')
    plt.close()

def plot_figure_3(df):
    # Age distribution histogram
    plt.figure(figsize=(8,5))
    sns.histplot(df['EMP_HR04'].dropna(), bins=30, kde=True, color='skyblue')
    plt.xlabel('Age')
    plt.ylabel('Count')
    plt.title('Age Distribution (EMP_HR04)')
    plt.tight_layout()
    plt.savefig('figure3_age_distribution.png', bbox_inches='tight')
    plt.close()

def main():
    """Main analysis function"""
    
    # Load data
    df = load_and_clean_data()
    
    print(f"Data loaded successfully. Total observations: {len(df):,}")
    
    # Table 2: Employment Status by TVET Participation
    print("\n" + "="*80)
    print("TABLE 2: EMPLOYMENT STATUS BY TVET PARTICIPATION")
    print("="*80)
    
    table2 = create_cross_tabulation(df, 'employed_label', 'tvet_label', 
                                   'Employment Status', 'TVET Participation')
    results2 = format_table(*table2, 'Employment Status', 'TVET Participation')
    save_table(table2[0], 'table2_employment_by_tvet', 'Employment Status by TVET Participation')
    save_table(table2[1], 'table2_employment_by_tvet_rowpct', 'Employment Status by TVET Participation (Row %)')
    
    # Table 3: Education Level by TVET Participation
    print("\n" + "="*80)
    print("TABLE 3: EDUCATION LEVEL BY TVET PARTICIPATION")
    print("="*80)
    
    table3 = create_cross_tabulation(df, 'Education', 'tvet_label', 
                                   'Education Level', 'TVET Participation')
    results3 = format_table(*table3, 'Education Level', 'TVET Participation')
    save_table(table3[0], 'table3_education_by_tvet', 'Education Level by TVET Participation')
    save_table(table3[1], 'table3_education_by_tvet_rowpct', 'Education Level by TVET Participation (Row %)')
    
    # Table 4a: Employment Status by Gender
    print("\n" + "="*80)
    print("TABLE 4A: EMPLOYMENT STATUS BY GENDER")
    print("="*80)
    
    table4a = create_cross_tabulation(df, 'employed_label', 'EMP_HR03', 
                                    'Employment Status', 'Gender')
    results4a = format_table(*table4a, 'Employment Status', 'Gender')
    save_table(table4a[0], 'table4a_employment_by_gender', 'Employment Status by Gender')
    save_table(table4a[1], 'table4a_employment_by_gender_rowpct', 'Employment Status by Gender (Row %)')
    
    # Table 4b: Employment Status by Location (Rural/Urban)
    print("\n" + "="*80)
    print("TABLE 4B: EMPLOYMENT STATUS BY LOCATION")
    print("="*80)
    
    table4b = create_cross_tabulation(df, 'employed_label', 'RU', 
                                    'Employment Status', 'Location')
    results4b = format_table(*table4b, 'Employment Status', 'Location')
    save_table(table4b[0], 'table4b_employment_by_location', 'Employment Status by Location')
    save_table(table4b[1], 'table4b_employment_by_location_rowpct', 'Employment Status by Location (Row %)')

    # Figures
    plot_figure_1(df)
    plot_figure_2(df)
    plot_figure_3(df)

    # Summary of findings
    print("\n" + "="*80)
    print("SUMMARY OF FINDINGS")
    print("="*80)
    
    print("\nKey Findings:")
    print("1. Employment Status by TVET Participation:")
    print(f"   - Chi-square test: {results2['chi2']:.2f} (p = {results2['p_value']:.4f})")
    print(f"   - Relationship: {results2['significance']}")
    
    print("\n2. Education Level by TVET Participation:")
    print(f"   - Chi-square test: {results3['chi2']:.2f} (p = {results3['p_value']:.4f})")
    print(f"   - Relationship: {results3['significance']}")
    
    print("\n3. Employment Status by Gender:")
    print(f"   - Chi-square test: {results4a['chi2']:.2f} (p = {results4a['p_value']:.4f})")
    print(f"   - Relationship: {results4a['significance']}")
    
    print("\n4. Employment Status by Location:")
    print(f"   - Chi-square test: {results4b['chi2']:.2f} (p = {results4b['p_value']:.4f})")
    print(f"   - Relationship: {results4b['significance']}")
    
    print("\nNote: *** p<0.001, ** p<0.01, * p<0.05")

if __name__ == "__main__":
    main() 