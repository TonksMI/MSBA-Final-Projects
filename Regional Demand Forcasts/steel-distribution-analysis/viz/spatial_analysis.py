"""
Spatial Analysis and Geographic Visualizations
Creates heatmaps and spatial analytics for steel demand
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set up paths
BASE_DIR = Path(__file__).parent.parent
FEATURES_DIR = BASE_DIR / 'features'
MODELS_DIR = BASE_DIR / 'models'
VIZ_DIR = BASE_DIR / 'viz'

class SpatialAnalyzer:
    """Performs spatial analysis and creates geographic visualizations"""

    def __init__(self):
        pass

    def load_data(self) -> tuple:
        """Load necessary data"""
        print("Loading data...")

        # Load features
        df = pd.read_csv(FEATURES_DIR / 'msa_features_latest.csv')

        # Load cluster assignments
        try:
            df_clusters = pd.read_csv(MODELS_DIR / 'clustering' / 'msa_cluster_assignments.csv')
            df = df.merge(df_clusters[['msa_name', 'cluster', 'cluster_name']],
                         on='msa_name', how='left')
        except:
            print("  ! Cluster assignments not found, continuing without clusters")

        # Load momentum classifications
        try:
            df_momentum = pd.read_csv(MODELS_DIR / 'timeseries' / 'momentum_classification_latest.csv')
            df = df.merge(df_momentum[['msa_name', 'overall_momentum', 'momentum_regime']],
                         on='msa_name', how='left', suffixes=('', '_momentum'))
        except:
            print("  ! Momentum data not found, continuing without momentum")

        print(f"  Loaded {len(df)} MSAs")
        return df

    def create_state_aggregates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate MSA data to state level"""
        print("\nCreating state-level aggregates...")

        # Aggregate by state
        state_agg = df.groupby('state').agg({
            'msa_name': 'count',
            'population': 'sum',
            'manufacturing_emp': 'sum',
            'construction_emp': 'sum',
            'building_permits': 'sum',
            'demand_intensity_score': 'mean',
            'steel_demand_index': 'mean' if 'steel_demand_index' in df.columns else 'first',
        }).reset_index()

        state_agg.rename(columns={'msa_name': 'msa_count'}, inplace=True)

        print(f"  ✓ Aggregated to {len(state_agg)} states")
        return state_agg

    def create_regional_heatmap(self, df: pd.DataFrame):
        """Create heatmap showing demand intensity by region"""
        print("\nCreating regional heatmap...")

        # Create pivot table for heatmap
        if 'census_region' in df.columns and 'metro_size_category' in df.columns:
            pivot_data = df.pivot_table(
                values='demand_intensity_score',
                index='census_region',
                columns='metro_size_category',
                aggfunc='mean'
            )

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='YlOrRd',
                       cbar_kws={'label': 'Demand Intensity Score'}, ax=ax)
            ax.set_title('Demand Intensity by Region and Metro Size', fontsize=14, weight='bold')
            ax.set_xlabel('Metro Size Category')
            ax.set_ylabel('Census Region')

            plt.tight_layout()
            plt.savefig(VIZ_DIR / 'regional_heatmap.png', dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved heatmap: {VIZ_DIR / 'regional_heatmap.png'}")
            plt.close()

    def create_demand_intensity_map(self, df: pd.DataFrame):
        """Create choropleth-style visualization of demand intensity"""
        print("\nCreating demand intensity map...")

        # Sort by demand intensity
        df_sorted = df.sort_values('demand_intensity_score', ascending=True)

        # Create horizontal bar chart (simpler than actual map without geopandas)
        fig, ax = plt.subplots(figsize=(12, 10))

        colors = plt.cm.RdYlGn(
            (df_sorted['demand_intensity_score'] - df_sorted['demand_intensity_score'].min()) /
            (df_sorted['demand_intensity_score'].max() - df_sorted['demand_intensity_score'].min())
        )

        ax.barh(range(len(df_sorted)), df_sorted['demand_intensity_score'],
               color=colors, alpha=0.8)

        ax.set_yticks(range(len(df_sorted)))
        ax.set_yticklabels([name[:35] for name in df_sorted['msa_name'].values], fontsize=8)
        ax.set_xlabel('Demand Intensity Score', fontsize=12)
        ax.set_title('Steel Demand Intensity by MSA', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        # Add color bar
        sm = plt.cm.ScalarMappable(
            cmap='RdYlGn',
            norm=plt.Normalize(
                vmin=df_sorted['demand_intensity_score'].min(),
                vmax=df_sorted['demand_intensity_score'].max()
            )
        )
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Demand Intensity Score', rotation=270, labelpad=20)

        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'demand_intensity_map.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved demand map: {VIZ_DIR / 'demand_intensity_map.png'}")
        plt.close()

    def create_cluster_geographic_distribution(self, df: pd.DataFrame):
        """Visualize geographic distribution of clusters"""
        print("\nCreating cluster geographic distribution...")

        if 'cluster_name' not in df.columns:
            print("  ! Cluster data not available, skipping")
            return

        # Count clusters by region
        if 'census_region' in df.columns:
            cluster_by_region = pd.crosstab(
                df['census_region'],
                df['cluster_name'],
                normalize='index'
            ) * 100

            fig, ax = plt.subplots(figsize=(12, 6))
            cluster_by_region.plot(kind='bar', stacked=True, ax=ax, colormap='Set3')
            ax.set_xlabel('Census Region')
            ax.set_ylabel('Percentage of MSAs')
            ax.set_title('Cluster Distribution by Region', fontsize=14, weight='bold')
            ax.legend(title='Cluster Type', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.grid(True, alpha=0.3, axis='y')

            plt.tight_layout()
            plt.savefig(VIZ_DIR / 'cluster_geographic_dist.png', dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved cluster distribution: {VIZ_DIR / 'cluster_geographic_dist.png'}")
            plt.close()

    def create_competitive_landscape_map(self, df: pd.DataFrame):
        """Create visualization of competitive opportunities"""
        print("\nCreating competitive landscape map...")

        # Load competitor data if available
        try:
            df_competitors = pd.read_csv(BASE_DIR / 'data' / 'raw' / 'sample_competitor_locations.csv')

            # Count competitors by MSA
            competitor_counts = df_competitors.groupby('msa_name').size().reset_index(name='competitor_count')

            # Merge with main data
            df_competitive = df.merge(competitor_counts, on='msa_name', how='left')
            df_competitive['competitor_count'] = df_competitive['competitor_count'].fillna(0)

            # Calculate opportunity score: high demand, low competition
            df_competitive['opportunity_score'] = (
                df_competitive['demand_intensity_score'] /
                (df_competitive['competitor_count'] + 1)  # +1 to avoid division by zero
            )

            # Create scatter plot
            fig, ax = plt.subplots(figsize=(12, 8))

            scatter = ax.scatter(
                df_competitive['competitor_count'],
                df_competitive['demand_intensity_score'],
                s=df_competitive['population'] / 50000,
                c=df_competitive['opportunity_score'],
                cmap='RdYlGn',
                alpha=0.6,
                edgecolors='black',
                linewidth=0.5
            )

            ax.set_xlabel('Number of Competitors', fontsize=12)
            ax.set_ylabel('Demand Intensity Score', fontsize=12)
            ax.set_title('Competitive Landscape: Demand vs. Competition', fontsize=14, weight='bold')
            ax.grid(True, alpha=0.3)

            # Add quadrant lines
            median_competitors = df_competitive['competitor_count'].median()
            median_demand = df_competitive['demand_intensity_score'].median()
            ax.axvline(x=median_competitors, color='red', linestyle='--', alpha=0.5)
            ax.axhline(y=median_demand, color='red', linestyle='--', alpha=0.5)

            # Label quadrants
            ax.text(0.95, 0.95, 'High Demand\nLow Competition\n[BEST OPPORTUNITY]',
                   transform=ax.transAxes, ha='right', va='top',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5),
                   fontsize=9, weight='bold')

            ax.text(0.05, 0.05, 'Low Demand\nHigh Competition\n[AVOID]',
                   transform=ax.transAxes, ha='left', va='bottom',
                   bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5),
                   fontsize=9, weight='bold')

            # Color bar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Opportunity Score', rotation=270, labelpad=20)

            # Annotate top opportunities
            top_opportunities = df_competitive.nlargest(5, 'opportunity_score')
            for _, row in top_opportunities.iterrows():
                ax.annotate(
                    row['msa_name'][:20],
                    (row['competitor_count'], row['demand_intensity_score']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=7, alpha=0.7
                )

            plt.tight_layout()
            plt.savefig(VIZ_DIR / 'competitive_landscape.png', dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved competitive landscape: {VIZ_DIR / 'competitive_landscape.png'}")
            plt.close()

            # Save opportunity ranking
            df_competitive.sort_values('opportunity_score', ascending=False)[
                ['msa_name', 'state', 'demand_intensity_score', 'competitor_count', 'opportunity_score']
            ].to_csv(VIZ_DIR / 'opportunity_ranking.csv', index=False)

        except Exception as e:
            print(f"  ! Could not create competitive landscape: {e}")

    def create_state_summary_map(self, state_agg: pd.DataFrame):
        """Create state-level summary visualization"""
        print("\nCreating state summary visualization...")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Demand Intensity by State
        ax1 = axes[0, 0]
        top_states = state_agg.nlargest(15, 'demand_intensity_score')
        ax1.barh(range(len(top_states)), top_states['demand_intensity_score'],
                color='steelblue', alpha=0.7)
        ax1.set_yticks(range(len(top_states)))
        ax1.set_yticklabels(top_states['state'].values)
        ax1.set_xlabel('Average Demand Intensity Score')
        ax1.set_title('Top 15 States by Demand Intensity')
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.invert_yaxis()

        # Plot 2: Total Employment by State
        ax2 = axes[0, 1]
        state_agg['total_steel_emp'] = (
            state_agg['manufacturing_emp'] + state_agg['construction_emp']
        )
        top_emp_states = state_agg.nlargest(15, 'total_steel_emp')
        ax2.barh(range(len(top_emp_states)), top_emp_states['total_steel_emp'],
                color='coral', alpha=0.7)
        ax2.set_yticks(range(len(top_emp_states)))
        ax2.set_yticklabels(top_emp_states['state'].values)
        ax2.set_xlabel('Total Steel-Related Employment')
        ax2.set_title('Top 15 States by Steel-Related Employment')
        ax2.grid(True, alpha=0.3, axis='x')
        ax2.invert_yaxis()

        # Plot 3: Building Permits by State
        ax3 = axes[1, 0]
        top_permits = state_agg.nlargest(15, 'building_permits')
        ax3.barh(range(len(top_permits)), top_permits['building_permits'],
                color='forestgreen', alpha=0.7)
        ax3.set_yticks(range(len(top_permits)))
        ax3.set_yticklabels(top_permits['state'].values)
        ax3.set_xlabel('Total Building Permits')
        ax3.set_title('Top 15 States by Building Permits')
        ax3.grid(True, alpha=0.3, axis='x')
        ax3.invert_yaxis()

        # Plot 4: MSA Count by State
        ax4 = axes[1, 1]
        top_msa_count = state_agg.nlargest(15, 'msa_count')
        ax4.barh(range(len(top_msa_count)), top_msa_count['msa_count'],
                color='purple', alpha=0.7)
        ax4.set_yticks(range(len(top_msa_count)))
        ax4.set_yticklabels(top_msa_count['state'].values)
        ax4.set_xlabel('Number of MSAs')
        ax4.set_title('States by MSA Count')
        ax4.grid(True, alpha=0.3, axis='x')
        ax4.invert_yaxis()

        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'state_summary.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved state summary: {VIZ_DIR / 'state_summary.png'}")
        plt.close()

def main():
    """Main execution function"""
    print("=" * 70)
    print("Spatial Analysis and Geographic Visualizations")
    print("=" * 70)

    analyzer = SpatialAnalyzer()

    # Load data
    df = analyzer.load_data()

    # Create state aggregates
    state_agg = analyzer.create_state_aggregates(df)

    # Create visualizations
    analyzer.create_regional_heatmap(df)
    analyzer.create_demand_intensity_map(df)
    analyzer.create_cluster_geographic_distribution(df)
    analyzer.create_competitive_landscape_map(df)
    analyzer.create_state_summary_map(state_agg)

    print("\n" + "=" * 70)
    print("Spatial analysis complete!")
    print(f"Visualizations saved to: {VIZ_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
