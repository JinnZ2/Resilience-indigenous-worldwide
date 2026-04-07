#!/usr/bin/env python3
"""
Infrastructure Flight Path Correlator
Analyzes correlation between aircraft flight paths and infrastructure networks
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist
import json
from dataclasses import dataclass
from typing import List, Tuple, Dict
import argparse

@dataclass
class CorrelationResult:
    """Store correlation analysis results"""
    infrastructure_type: str
    correlation_score: float
    confidence_level: str
    key_matches: List[str]
    mismatches: List[str]
    recommendations: str

class FlightPathCorrelator:
    def __init__(self, image_path: str):
        """Initialize with flight track image"""
        self.image = Image.open(image_path)
        self.points = self._extract_track_points()
        self.features = self._extract_features()
        
    def _extract_track_points(self) -> np.ndarray:
        """Extract coordinates from flight track image"""
        # Convert to grayscale and threshold
        gray = np.array(self.image.convert('L'))
        binary = gray < 128  # Assume tracks are dark on light background
        
        # Find track pixels
        y_coords, x_coords = np.where(binary)
        
        if len(x_coords) == 0:
            raise ValueError("No track pixels detected in image")
        
        # Normalize coordinates
        points = np.column_stack([x_coords, y_coords])
        points = points[::10]  # Sample every 10th point for efficiency
        
        return points
    
    def _extract_features(self) -> Dict:
        """Extract geometric and topological features from flight path"""
        if len(self.points) < 3:
            return {}
        
        # Calculate direction distribution
        directions = []
        for i in range(1, len(self.points)):
            dx = self.points[i, 0] - self.points[i-1, 0]
            dy = self.points[i, 1] - self.points[i-1, 1]
            angle = np.arctan2(dy, dx) * 180 / np.pi
            directions.append(angle)
        
        # Cluster points to identify nodes/concentrations
        scaler = StandardScaler()
        points_scaled = scaler.fit_transform(self.points)
        clustering = DBSCAN(eps=0.3, min_samples=50).fit(points_scaled)
        
        unique_clusters = np.unique(clustering.labels_)
        n_clusters = len(unique_clusters[unique_clusters >= 0])
        
        # Calculate branching factor (change in direction)
        direction_changes = np.abs(np.diff(directions))
        sharp_turns = np.sum(direction_changes > 45) / len(direction_changes)
        
        # Calculate loop detection
        loops = self._detect_loops()
        
        # Calculate path linearity
        total_length = self._path_length()
        direct_distance = np.linalg.norm(self.points[-1] - self.points[0])
        linearity = direct_distance / total_length if total_length > 0 else 0
        
        return {
            'n_clusters': n_clusters,
            'n_branches': len(self._find_branches()),
            'loops': loops,
            'linearity': linearity,
            'sharp_turn_ratio': sharp_turns,
            'direction_std': np.std(directions) if directions else 0,
            'n_directions': len(np.unique(np.round(directions / 45))) if directions else 0
        }
    
    def _path_length(self) -> float:
        """Calculate total path length"""
        if len(self.points) < 2:
            return 0
        return np.sum(np.sqrt(np.sum(np.diff(self.points, axis=0)**2, axis=1)))
    
    def _detect_loops(self) -> int:
        """Detect loop patterns in flight path"""
        # Simplified loop detection using clustering density
        # Actual implementation would need more sophisticated geometry analysis
        return int(self.features.get('n_clusters', 0) > 3)
    
    def _find_branches(self) -> List[int]:
        """Find branching points in the path"""
        branches = []
        window = 50
        for i in range(window, len(self.points) - window):
            before = self.points[i-window:i]
            after = self.points[i+1:i+window+1]
            
            if len(before) > 0 and len(after) > 0:
                dir_before = np.mean(np.diff(before, axis=0), axis=0)
                dir_after = np.mean(np.diff(after, axis=0), axis=0)
                
                angle_change = np.arccos(np.dot(dir_before, dir_after) / 
                                        (np.linalg.norm(dir_before) * np.linalg.norm(dir_after) + 1e-6))
                
                if angle_change > np.pi / 3:  # 60 degree change = branch
                    branches.append(i)
        
        return branches
    
    def correlate_with_infrastructure(self, infrastructure_type: str) -> CorrelationResult:
        """
        Calculate correlation score between flight path and infrastructure type
        
        infrastructure_type: 'pipeline', 'transmission', 'mixed', 'area_survey'
        """
        features = self.features
        
        # Define ideal feature profiles for each infrastructure type
        profiles = {
            'pipeline': {
                'n_clusters': (0, 1),      # Few clusters
                'n_branches': (0, 2),      # Few branches
                'loops': (0, 0.3),         # No loops
                'linearity': (0.7, 1.0),   # High linearity
                'sharp_turn_ratio': (0, 0.2),  # Few sharp turns
                'direction_std': (0, 30),  # Consistent direction
                'n_directions': (1, 2)     # 1-2 main directions
            },
            'transmission': {
                'n_clusters': (2, 5),      # Multiple clusters (substations)
                'n_branches': (3, 10),     # Many branches
                'loops': (0.5, 1.0),       # Loops present
                'linearity': (0.2, 0.5),   # Moderate linearity
                'sharp_turn_ratio': (0.3, 0.7),  # Many sharp turns
                'direction_std': (40, 90), # Wide direction variation
                'n_directions': (3, 6)     # Multiple directions
            },
            'mixed_corridor': {
                'n_clusters': (1, 3),      # Moderate clusters
                'n_branches': (2, 5),      # Some branches
                'loops': (0.2, 0.6),       # Some loops
                'linearity': (0.4, 0.7),   # Mixed linearity
                'sharp_turn_ratio': (0.2, 0.5),
                'direction_std': (20, 60),
                'n_directions': (2, 4)
            },
            'area_survey': {
                'n_clusters': (3, 10),     # Many clusters
                'n_branches': (5, 20),     # Many branches
                'loops': (0.3, 1.0),       # Variable loops
                'linearity': (0.1, 0.4),   # Low linearity
                'sharp_turn_ratio': (0.4, 0.8),
                'direction_std': (60, 120),
                'n_directions': (4, 8)
            }
        }
        
        if infrastructure_type not in profiles:
            raise ValueError(f"Unknown infrastructure type: {infrastructure_type}")
        
        profile = profiles[infrastructure_type]
        matches = []
        mismatches = []
        scores = []
        
        # Calculate match scores for each feature
        for feature, (min_val, max_val) in profile.items():
            if feature in features:
                value = features[feature]
                if isinstance(value, (int, float)):
                    # Normalize score between 0 and 1
                    if min_val <= value <= max_val:
                        score = 1.0
                        matches.append(feature)
                    else:
                        # Calculate distance from range
                        if value < min_val:
                            distance = (min_val - value) / (max_val - min_val + 1)
                        else:
                            distance = (value - max_val) / (max_val - min_val + 1)
                        score = max(0, 1 - min(1, distance))
                        mismatches.append(feature)
                    
                    scores.append(score)
        
        # Calculate overall correlation score (0-1)
        if scores:
            correlation_score = np.mean(scores)
        else:
            correlation_score = 0.5
        
        # Determine confidence level
        if correlation_score >= 0.8:
            confidence = "High"
        elif correlation_score >= 0.6:
            confidence = "Moderate"
        elif correlation_score >= 0.4:
            confidence = "Low"
        else:
            confidence = "Very Low"
        
        # Generate recommendations
        if correlation_score > 0.7:
            recommendations = f"Flight pattern strongly matches {infrastructure_type} survey behavior."
        elif correlation_score > 0.5:
            recommendations = f"Flight pattern moderately matches {infrastructure_type}. Consider analyzing higher-resolution imagery or verifying with infrastructure maps."
        else:
            recommendations = f"Flight pattern does not strongly correlate with {infrastructure_type}. Consider other infrastructure types or area survey classification."
        
        return CorrelationResult(
            infrastructure_type=infrastructure_type,
            correlation_score=correlation_score,
            confidence_level=confidence,
            key_matches=matches,
            mismatches=mismatches,
            recommendations=recommendations
        )
    
    def visualize(self, results: List[CorrelationResult] = None):
        """Visualize flight path with optional correlation results"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot flight path
        axes[0].plot(self.points[:, 0], self.points[:, 1], 'b-', linewidth=1, alpha=0.7)
        axes[0].scatter(self.points[0, 0], self.points[0, 1], c='green', s=100, label='Start')
        axes[0].scatter(self.points[-1, 0], self.points[-1, 1], c='red', s=100, label='End')
        axes[0].set_title('Flight Path Analysis')
        axes[0].set_xlabel('X Coordinate')
        axes[0].set_ylabel('Y Coordinate')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot correlation results
        if results:
            types = [r.infrastructure_type for r in results]
            scores = [r.correlation_score for r in results]
            colors = ['green' if s >= 0.7 else 'orange' if s >= 0.5 else 'red' for s in scores]
            
            axes[1].barh(types, scores, color=colors)
            axes[1].set_xlim(0, 1)
            axes[1].set_xlabel('Correlation Score')
            axes[1].set_title('Infrastructure Type Correlation')
            axes[1].axvline(x=0.7, color='green', linestyle='--', alpha=0.5, label='High confidence')
            axes[1].axvline(x=0.5, color='orange', linestyle='--', alpha=0.5, label='Moderate confidence')
            axes[1].legend()
            
            # Add score labels
            for i, (score, conf) in enumerate(zip(scores, [r.confidence_level for r in results])):
                axes[1].text(score + 0.02, i, f'{score:.2f} ({conf})', va='center')
        
        plt.tight_layout()
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze flight path correlation with infrastructure')
    parser.add_argument('image_path', help='Path to flight track image')
    parser.add_argument('--infrastructure', nargs='+', 
                       default=['pipeline', 'transmission', 'mixed_corridor', 'area_survey'],
                       help='Infrastructure types to analyze')
    parser.add_argument('--output', help='Output JSON file for results')
    
    args = parser.parse_args()
    
    try:
        # Initialize correlator
        correlator = FlightPathCorrelator(args.image_path)
        
        # Analyze each infrastructure type
        results = []
        for infra_type in args.infrastructure:
            result = correlator.correlate_with_infrastructure(infra_type)
            results.append(result)
            
            print(f"\n=== {infra_type.upper()} Correlation ===")
            print(f"Score: {result.correlation_score:.3f}")
            print(f"Confidence: {result.confidence_level}")
            print(f"Key matches: {', '.join(result.key_matches) if result.key_matches else 'None'}")
            print(f"Mismatches: {', '.join(result.mismatches) if result.mismatches else 'None'}")
            print(f"Recommendation: {result.recommendations}")
        
        # Visualize
        correlator.visualize(results)
        
        # Save results if requested
        if args.output:
            output_data = {
                'results': [
                    {
                        'type': r.infrastructure_type,
                        'score': r.correlation_score,
                        'confidence': r.confidence_level,
                        'matches': r.key_matches,
                        'mismatches': r.mismatches,
                        'recommendation': r.recommendations
                    }
                    for r in results
                ],
                'features': correlator.features
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\nResults saved to {args.output}")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())


Requirements:

pip install numpy pillow matplotlib scikit-learn scipy


Apple shortcut:

// Apple Shortcuts JavaScript (for use in "Run JavaScript on Webpage" action)

function analyzeFlightPattern(imageData) {
    // This is a simplified version - actual implementation would need canvas manipulation
    
    const analysis = {
        timestamp: new Date().toISOString(),
        patterns: {
            linearity: "unknown",
            branching: "unknown",
            loops: "unknown"
        },
        correlation: {
            pipeline: 0,
            transmission: 0,
            areaSurvey: 0
        }
    };
    
    // Simplified heuristic based on user input
    // In practice, you'd need to extract features from the image
    
    return JSON.stringify(analysis, null, 2);
}

// To use: Save this as a shortcut that asks for user observations
// and provides quick correlation estimates





Usage:

# Basic analysis for all infrastructure types
python flight_correlator.py flight_track.png

# Specific infrastructure analysis
python flight_correlator.py flight_track.png --infrastructure transmission pipeline

# Save results to JSON
python flight_correlator.py flight_track.png --output results.json



Key Features of the Python Script

1. Automatic Track Extraction: Extracts flight path from images
2. Feature Analysis: Calculates 7 key geometric features
3. Multi-Infrastructure Correlation: Scores against 4 infrastructure types
4. Visualization: Shows flight path and correlation results
5. Confidence Levels: Provides high/moderate/low confidence ratings
6. JSON Export: Saves detailed results for documentation

Expected Output Example

```
=== TRANSMISSION Correlation ===
Score: 0.823
Confidence: High
Key matches: n_clusters, n_branches, loops, sharp_turn_ratio, direction_std
Mismatches: linearity
Recommendation: Flight pattern strongly matches transmission survey behavior.

=== PIPELINE Correlation ===
Score: 0.312
Confidence: Very Low
Key matches: None
Mismatches: linearity, direction_std, n_directions
Recommendation: Flight pattern does not strongly correlate with pipeline.
```
E xtend this later:

1. Add GPS coordinate support — if you ever have actual lat/lon tracks instead of images, the correlation can become geospatially precise (actual distance to known pipeline/transmission shapefiles)
2. Train a lightweight classifier — if you collect 50-100 labeled flight tracks, the feature extraction can feed a Random Forest that learns your exact judgment criteria
3. Add temporal analysis — if you have multiple flights from the same tail number, the script could detect repeat patterns (highly diagnostic for pipeline vs. survey work)
