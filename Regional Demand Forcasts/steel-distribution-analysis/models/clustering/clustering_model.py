"""
Regional Archetype Clustering Analysis
Identifies distinct types of metropolitan markets
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist

# Set up paths
BASE_DIR = Path(__file__).parent.parent.parent
FEATURES_DIR = BASE_DIR / 'features'
MODELS_DIR = BASE_DIR / 'models' / 'clustering'
VIZ_DIR = BASE_DIR / 'viz'
MODELS_DIR.mkdir(parents=True, exist_ok=True)
VIZ_DIR.mkdir(parents=True, exist_ok=True)

class RegionalArchetypeClustering:
    """Performs clustering to identify regional market archetypes"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans_model = None
        self.hierarchical_model = None
        self.optimal_k = None

    def load_data(self) -> pd.DataFrame:
        """Load latest year feature data for clustering"""
        print("Loading feature data for clustering...")
        df = pd.read_csv(FEATURES_DIR / 'msa_features_latest.csv')
        print(f"  Loaded {len(df)} MSAs")
        return df

    def select_clustering_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select features most relevant for regional archetypes"""
        print("\nSelecting clustering features...")

        # Features that define regional character
        clustering_features = [
            'mfg_emp_per_capita',              # Manufacturing intensity
            'constr_emp_per_capita',           # Construction activity
            'infra_spending_per_capita',       # Infrastructure investment
            'population_growth',               # Demographic momentum
            'median_income',                   # Economic affluence
            'industry_diversity_index',        # Economic diversification
            'building_permits_growth',         # Construction momentum
            'demand_intensity_score',          # Overall demand
        ]

        # Ensure all features exist
        clustering_features = [f for f in clustering_features if f in df.columns]

        X = df[clustering_features].copy()

        # Handle any missing values
        X = X.fillna(X.median())

        print(f"  ✓ Selected {len(clustering_features)} features")
        print(f"  Features: {', '.join(clustering_features)}")

        return X, clustering_features

    def find_optimal_clusters(self, X: pd.DataFrame, max_k: int = 10) -> int:
        """Use elbow method and silhouette score to find optimal k"""
        print(f"\nFinding optimal number of clusters (testing k=2 to {max_k})...")

        # Standardize features
        X_scaled = self.scaler.fit_transform(X)

        inertias = []
        silhouette_scores = []
        k_range = range(2, max_k + 1)

        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)

            inertias.append(kmeans.inertia_)
            sil_score = silhouette_score(X_scaled, labels)
            silhouette_scores.append(sil_score)

            print(f"  k={k}: Inertia={kmeans.inertia_:.2f}, Silhouette={sil_score:.3f}")

        # Plot elbow curve and silhouette scores
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Elbow plot
        ax1.plot(k_range, inertias, 'bo-')
        ax1.set_xlabel('Number of Clusters (k)')
        ax1.set_ylabel('Inertia')
        ax1.set_title('Elbow Method')
        ax1.grid(True, alpha=0.3)

        # Silhouette plot
        ax2.plot(k_range, silhouette_scores, 'ro-')
        ax2.set_xlabel('Number of Clusters (k)')
        ax2.set_ylabel('Silhouette Score')
        ax2.set_title('Silhouette Analysis')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'clustering_optimization.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved optimization plot: {VIZ_DIR / 'clustering_optimization.png'}")

        # Choose k with best silhouette score
        optimal_k = k_range[np.argmax(silhouette_scores)]
        print(f"\n  → Optimal k = {optimal_k} (highest silhouette score: {max(silhouette_scores):.3f})")

        return optimal_k

    def fit_kmeans(self, X: pd.DataFrame, k: int) -> np.ndarray:
        """Fit K-Means clustering model"""
        print(f"\nFitting K-Means with k={k}...")

        X_scaled = self.scaler.fit_transform(X)

        self.kmeans_model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = self.kmeans_model.fit_predict(X_scaled)

        # Calculate metrics
        sil_score = silhouette_score(X_scaled, labels)
        ch_score = calinski_harabasz_score(X_scaled, labels)

        print(f"  ✓ K-Means fitted")
        print(f"  Silhouette Score: {sil_score:.3f}")
        print(f"  Calinski-Harabasz Score: {ch_score:.2f}")

        return labels

    def fit_hierarchical(self, X: pd.DataFrame, k: int) -> np.ndarray:
        """Fit Hierarchical clustering model"""
        print(f"\nFitting Hierarchical Clustering with k={k}...")

        X_scaled = self.scaler.transform(X)

        self.hierarchical_model = AgglomerativeClustering(
            n_clusters=k,
            linkage='ward'
        )
        labels = self.hierarchical_model.fit_predict(X_scaled)

        print(f"  ✓ Hierarchical clustering fitted")

        # Create dendrogram
        plt.figure(figsize=(12, 6))
        linkage_matrix = linkage(X_scaled, method='ward')
        dendrogram(linkage_matrix, truncate_mode='lastp', p=20)
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('Sample Index or (Cluster Size)')
        plt.ylabel('Distance')
        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'hierarchical_dendrogram.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved dendrogram: {VIZ_DIR / 'hierarchical_dendrogram.png'}")

        return labels

    def analyze_clusters(self, df: pd.DataFrame, X: pd.DataFrame,
                        labels: np.ndarray, feature_names: list) -> pd.DataFrame:
        """Analyze and profile each cluster"""
        print("\nAnalyzing cluster profiles...")

        df_clustered = df.copy()
        df_clustered['cluster'] = labels

        # Calculate cluster statistics
        cluster_profiles = df_clustered.groupby('cluster').agg({
            'msa_name': 'count',
            **{f: ['mean', 'std'] for f in feature_names}
        })

        print("\nCluster Sizes:")
        print(df_clustered['cluster'].value_counts().sort_index())

        # Assign interpretable names to clusters based on profiles
        cluster_names = self._assign_cluster_names(df_clustered, feature_names)
        df_clustered['cluster_name'] = df_clustered['cluster'].map(cluster_names)

        print("\nCluster Names:")
        for cluster_id, name in cluster_names.items():
            print(f"  Cluster {cluster_id}: {name}")

        return df_clustered, cluster_profiles, cluster_names

    def _assign_cluster_names(self, df: pd.DataFrame, features: list) -> dict:
        """Assign interpretable names to clusters based on their characteristics"""
        cluster_means = df.groupby('cluster')[features].mean()

        cluster_names = {}

        for cluster_id in cluster_means.index:
            profile = cluster_means.loc[cluster_id]

            # Decision rules for naming (simplified - customize based on actual data)
            if profile['mfg_emp_per_capita'] > cluster_means['mfg_emp_per_capita'].median():
                if profile['constr_emp_per_capita'] > cluster_means['constr_emp_per_capita'].median():
                    name = "Manufacturing & Construction Hubs"
                else:
                    name = "Industrial Manufacturing Centers"
            elif profile['constr_emp_per_capita'] > cluster_means['constr_emp_per_capita'].median():
                if profile['building_permits_growth'] > 0.05:
                    name = "Construction Boomtowns"
                else:
                    name = "Steady Construction Markets"
            elif profile['population_growth'] > cluster_means['population_growth'].median():
                name = "Emerging Growth Markets"
            elif profile['median_income'] > cluster_means['median_income'].median():
                name = "Affluent Mature Markets"
            else:
                name = "Slow Growth / Legacy Markets"

            cluster_names[cluster_id] = name

        return cluster_names

    def visualize_clusters(self, df: pd.DataFrame, X: pd.DataFrame,
                          feature_names: list, cluster_names: dict):
        """Create visualizations of cluster characteristics"""
        print("\nCreating cluster visualizations...")

        # 1. Cluster profile heatmap
        cluster_means = df.groupby('cluster')[feature_names].mean()

        # Normalize for visualization
        cluster_means_norm = (cluster_means - cluster_means.min()) / (cluster_means.max() - cluster_means.min())

        plt.figure(figsize=(12, 6))
        sns.heatmap(cluster_means_norm.T, annot=True, fmt='.2f', cmap='YlOrRd', cbar_kws={'label': 'Normalized Value'})
        plt.title('Cluster Profiles - Feature Heatmap')
        plt.xlabel('Cluster')
        plt.ylabel('Feature')
        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'cluster_profiles_heatmap.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved heatmap: {VIZ_DIR / 'cluster_profiles_heatmap.png'}")
        plt.close()

        # 2. Radar/spider charts for each cluster
        from math import pi

        categories = [f.replace('_', ' ').title()[:20] for f in feature_names]
        N = len(categories)

        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        fig, axes = plt.subplots(2, 3, figsize=(18, 12), subplot_kw=dict(projection='polar'))
        axes = axes.flatten()

        for idx, cluster_id in enumerate(sorted(df['cluster'].unique())):
            ax = axes[idx]

            values = cluster_means_norm.loc[cluster_id].values.tolist()
            values += values[:1]

            ax.plot(angles, values, 'o-', linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, size=8)
            ax.set_ylim(0, 1)
            ax.set_title(f"Cluster {cluster_id}: {cluster_names[cluster_id]}", size=10, weight='bold', pad=20)
            ax.grid(True)

        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'cluster_radar_charts.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved radar charts: {VIZ_DIR / 'cluster_radar_charts.png'}")
        plt.close()

    def save_model(self, df_clustered: pd.DataFrame, cluster_profiles: pd.DataFrame, cluster_names: dict):
        """Save clustering model and results"""
        print("\nSaving clustering model and results...")

        # Save model objects
        with open(MODELS_DIR / 'kmeans_model.pkl', 'wb') as f:
            pickle.dump(self.kmeans_model, f)

        with open(MODELS_DIR / 'scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)

        # Save cluster assignments
        df_clustered[['msa_name', 'state', 'cluster', 'cluster_name']].to_csv(
            MODELS_DIR / 'msa_cluster_assignments.csv', index=False
        )

        # Save cluster profiles
        cluster_profiles.to_csv(MODELS_DIR / 'cluster_profiles.csv')

        # Save cluster names
        pd.DataFrame.from_dict(cluster_names, orient='index', columns=['cluster_name']).to_csv(
            MODELS_DIR / 'cluster_names.csv'
        )

        print(f"  ✓ Saved to {MODELS_DIR}")

def main():
    """Main execution function"""
    print("=" * 70)
    print("Regional Archetype Clustering Analysis")
    print("=" * 70)

    clusterer = RegionalArchetypeClustering()

    # Load data
    df = clusterer.load_data()

    # Select features
    X, feature_names = clusterer.select_clustering_features(df)

    # Find optimal clusters
    optimal_k = clusterer.find_optimal_clusters(X, max_k=8)
    clusterer.optimal_k = optimal_k

    # Fit models
    kmeans_labels = clusterer.fit_kmeans(X, optimal_k)
    # hierarchical_labels = clusterer.fit_hierarchical(X, optimal_k)

    # Analyze clusters (using K-Means results)
    df_clustered, cluster_profiles, cluster_names = clusterer.analyze_clusters(
        df, X, kmeans_labels, feature_names
    )

    # Visualize
    clusterer.visualize_clusters(df_clustered, X, feature_names, cluster_names)

    # Save
    clusterer.save_model(df_clustered, cluster_profiles, cluster_names)

    print("\n" + "=" * 70)
    print("Clustering analysis complete!")
    print(f"Optimal clusters: {optimal_k}")
    print(f"Results saved to: {MODELS_DIR}")
    print(f"Visualizations saved to: {VIZ_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
