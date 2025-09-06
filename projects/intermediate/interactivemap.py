#!/usr/bin/env python3
"""
Interactive Map with Folium
A comprehensive mapping application using Folium for geographical data visualization.

Features:
- Interactive world map with zoom and pan capabilities
- Multiple marker types and clustering
- Choropleth maps for data visualization  
- Custom overlays and controls
- Popup information and tooltips
- Export functionality

Requirements:
- folium
- pandas
- requests
- json

Author: Python Central Hub
Date: 2025-09-05
"""

import folium
import pandas as pd
import json
import requests
from folium import plugins
from folium.plugins import MarkerCluster, HeatMap
import webbrowser
import os
from datetime import datetime


class InteractiveMapGenerator:
    """Generate interactive maps with various features and visualizations."""
    
    def __init__(self):
        self.maps = {}
        self.default_location = [39.8283, -98.5795]  # Center of USA
        self.default_zoom = 4
        
    def create_basic_map(self, location=None, zoom=None, name="basic_map"):
        """Create a basic interactive map."""
        if location is None:
            location = self.default_location
        if zoom is None:
            zoom = self.default_zoom
            
        # Create base map
        m = folium.Map(
            location=location,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # Add different tile layers
        folium.TileLayer('Stamen Terrain').add_to(m)
        folium.TileLayer('Stamen Toner').add_to(m)
        folium.TileLayer('CartoDB positron').add_to(m)
        folium.TileLayer('CartoDB dark_matter').add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        self.maps[name] = m
        return m
    
    def add_markers(self, map_obj, locations_data):
        """Add various types of markers to the map."""
        # Create marker cluster
        marker_cluster = MarkerCluster().add_to(map_obj)
        
        for location in locations_data:
            lat, lon = location['coordinates']
            name = location.get('name', 'Unknown')
            description = location.get('description', '')
            marker_type = location.get('type', 'default')
            
            # Create popup content
            popup_html = f"""
            <div style="width: 200px;">
                <h4>{name}</h4>
                <p>{description}</p>
                <small>Coordinates: {lat:.4f}, {lon:.4f}</small>
            </div>
            """
            
            # Different marker styles based on type
            if marker_type == 'restaurant':
                icon = folium.Icon(color='red', icon='cutlery', prefix='fa')
            elif marker_type == 'hotel':
                icon = folium.Icon(color='blue', icon='bed', prefix='fa')
            elif marker_type == 'attraction':
                icon = folium.Icon(color='green', icon='camera', prefix='fa')
            else:
                icon = folium.Icon(color='gray', icon='info-sign')
            
            # Add marker to cluster
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=name,
                icon=icon
            ).add_to(marker_cluster)
    
    def add_heatmap(self, map_obj, heat_data, name="Heat Map"):
        """Add heatmap overlay to the map."""
        # Create feature group for heatmap
        heat_group = folium.FeatureGroup(name=name)
        
        # Add heatmap
        HeatMap(
            heat_data,
            min_opacity=0.2,
            max_zoom=18,
            radius=15,
            blur=10,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        ).add_to(heat_group)
        
        heat_group.add_to(map_obj)
    
    def add_choropleth(self, map_obj, geo_data, data_df, key_column, value_column):
        """Add choropleth layer for data visualization."""
        folium.Choropleth(
            geo_data=geo_data,
            name='Choropleth',
            data=data_df,
            columns=[key_column, value_column],
            key_on='feature.properties.NAME',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=value_column
        ).add_to(map_obj)
    
    def add_custom_controls(self, map_obj):
        """Add custom controls and plugins to the map."""
        # Add fullscreen button
        plugins.Fullscreen(
            position='topright',
            title='Expand me',
            title_cancel='Exit me',
            force_separate_button=True
        ).add_to(map_obj)
        
        # Add measure control
        plugins.MeasureControl().add_to(map_obj)
        
        # Add draw tools
        draw = plugins.Draw(export=True)
        draw.add_to(map_obj)
        
        # Add minimap
        minimap = plugins.MiniMap()
        map_obj.add_child(minimap)
        
        # Add mouse position
        fmtr = "function(num) {return L.Util.formatNum(num, 4) + ' º ';};"
        plugins.MousePosition(
            position='topright',
            separator=' | ',
            empty_string='NaN',
            lng_first=True,
            num_digits=20,
            prefix='Coordinates:',
            lat_formatter=fmtr,
            lng_formatter=fmtr,
        ).add_to(map_obj)
    
    def create_travel_map(self):
        """Create a travel-themed map with popular destinations."""
        travel_map = self.create_basic_map(name="travel_map")
        
        # Sample travel destinations
        destinations = [
            {
                'name': 'Eiffel Tower',
                'coordinates': [48.8584, 2.2945],
                'description': 'Iconic iron tower in Paris, France',
                'type': 'attraction'
            },
            {
                'name': 'Times Square',
                'coordinates': [40.7580, -73.9855],
                'description': 'Famous commercial intersection in NYC',
                'type': 'attraction'
            },
            {
                'name': 'Tokyo Tower',
                'coordinates': [35.6586, 139.7454],
                'description': 'Communications tower in Tokyo, Japan',
                'type': 'attraction'
            },
            {
                'name': 'Sydney Opera House',
                'coordinates': [-33.8568, 151.2153],
                'description': 'Multi-venue performing arts center',
                'type': 'attraction'
            },
            {
                'name': 'Machu Picchu',
                'coordinates': [-13.1631, -72.5450],
                'description': 'Ancient Incan citadel in Peru',
                'type': 'attraction'
            }
        ]
        
        self.add_markers(travel_map, destinations)
        self.add_custom_controls(travel_map)
        
        return travel_map
    
    def create_earthquake_map(self):
        """Create a map showing earthquake data with heatmap."""
        eq_map = self.create_basic_map(name="earthquake_map")
        
        # Sample earthquake data (latitude, longitude, magnitude)
        earthquake_data = [
            [37.7749, -122.4194, 4.5],  # San Francisco
            [34.0522, -118.2437, 3.2],  # Los Angeles
            [40.7128, -74.0060, 2.1],   # New York
            [35.6762, 139.6503, 5.1],   # Tokyo
            [-33.8688, 151.2093, 3.8],  # Sydney
            [55.7558, 37.6176, 2.9],    # Moscow
            [51.5074, -0.1278, 1.8],    # London
            [48.8566, 2.3522, 2.3],     # Paris
        ]
        
        self.add_heatmap(eq_map, earthquake_data, "Earthquake Activity")
        self.add_custom_controls(eq_map)
        
        return eq_map
    
    def create_population_map(self):
        """Create a choropleth map showing population data."""
        pop_map = self.create_basic_map(name="population_map")
        
        # Note: This would require actual GeoJSON data and population statistics
        # For demonstration, we'll add major cities with population markers
        cities = [
            {
                'name': 'Tokyo',
                'coordinates': [35.6762, 139.6503],
                'description': 'Population: ~37.4 million',
                'type': 'city'
            },
            {
                'name': 'Delhi',
                'coordinates': [28.7041, 77.1025],
                'description': 'Population: ~31.4 million',
                'type': 'city'
            },
            {
                'name': 'Shanghai',
                'coordinates': [31.2304, 121.4737],
                'description': 'Population: ~27.8 million',
                'type': 'city'
            },
            {
                'name': 'São Paulo',
                'coordinates': [-23.5505, -46.6333],
                'description': 'Population: ~22.4 million',
                'type': 'city'
            }
        ]
        
        # Add city markers with custom sizing based on population
        for city in cities:
            lat, lon = city['coordinates']
            folium.CircleMarker(
                location=[lat, lon],
                radius=15,  # Could be proportional to population
                popup=f"{city['name']}<br>{city['description']}",
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.6
            ).add_to(pop_map)
        
        self.add_custom_controls(pop_map)
        return pop_map
    
    def save_map(self, map_obj, filename):
        """Save map to HTML file."""
        filepath = f"{filename}.html"
        map_obj.save(filepath)
        return filepath
    
    def open_in_browser(self, filepath):
        """Open the saved map in default web browser."""
        webbrowser.open(f"file://{os.path.abspath(filepath)}")


class MapDataManager:
    """Manage data sources for map visualizations."""
    
    def __init__(self):
        self.data_cache = {}
    
    def fetch_earthquake_data(self, days=7):
        """Fetch real earthquake data from USGS API."""
        try:
            url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching earthquake data: {e}")
        return None
    
    def load_sample_data(self):
        """Load sample geographical data for demonstration."""
        return {
            'world_cities': [
                {'name': 'London', 'lat': 51.5074, 'lon': -0.1278, 'population': 8982000},
                {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522, 'population': 2161000},
                {'name': 'Berlin', 'lat': 52.5200, 'lon': 13.4050, 'population': 3669000},
                {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038, 'population': 3223000},
                {'name': 'Rome', 'lat': 41.9028, 'lon': 12.4964, 'population': 2873000},
            ]
        }


def main():
    """Main function to demonstrate interactive map features."""
    print("🗺️  Interactive Map Generator")
    print("=" * 50)
    
    # Initialize map generator
    map_gen = InteractiveMapGenerator()
    data_manager = MapDataManager()
    
    while True:
        print("\nAvailable Maps:")
        print("1. Basic Interactive Map")
        print("2. Travel Destinations Map")
        print("3. Earthquake Activity Map")
        print("4. Population Centers Map")
        print("5. Custom Marker Map")
        print("6. Exit")
        
        choice = input("\nSelect map type (1-6): ").strip()
        
        if choice == '1':
            print("\n📍 Creating basic interactive map...")
            basic_map = map_gen.create_basic_map()
            map_gen.add_custom_controls(basic_map)
            filepath = map_gen.save_map(basic_map, "basic_interactive_map")
            print(f"✅ Map saved as {filepath}")
            
            if input("Open in browser? (y/n): ").lower() == 'y':
                map_gen.open_in_browser(filepath)
        
        elif choice == '2':
            print("\n✈️  Creating travel destinations map...")
            travel_map = map_gen.create_travel_map()
            filepath = map_gen.save_map(travel_map, "travel_destinations_map")
            print(f"✅ Map saved as {filepath}")
            
            if input("Open in browser? (y/n): ").lower() == 'y':
                map_gen.open_in_browser(filepath)
        
        elif choice == '3':
            print("\n🌍 Creating earthquake activity map...")
            eq_map = map_gen.create_earthquake_map()
            filepath = map_gen.save_map(eq_map, "earthquake_activity_map")
            print(f"✅ Map saved as {filepath}")
            
            if input("Open in browser? (y/n): ").lower() == 'y':
                map_gen.open_in_browser(filepath)
        
        elif choice == '4':
            print("\n🏙️  Creating population centers map...")
            pop_map = map_gen.create_population_map()
            filepath = map_gen.save_map(pop_map, "population_centers_map")
            print(f"✅ Map saved as {filepath}")
            
            if input("Open in browser? (y/n): ").lower() == 'y':
                map_gen.open_in_browser(filepath)
        
        elif choice == '5':
            print("\n📌 Creating custom marker map...")
            custom_map = map_gen.create_basic_map()
            
            # Get custom location from user
            try:
                lat = float(input("Enter latitude: "))
                lon = float(input("Enter longitude: "))
                name = input("Enter location name: ")
                description = input("Enter description: ")
                
                custom_locations = [{
                    'name': name,
                    'coordinates': [lat, lon],
                    'description': description,
                    'type': 'custom'
                }]
                
                map_gen.add_markers(custom_map, custom_locations)
                map_gen.add_custom_controls(custom_map)
                
                filepath = map_gen.save_map(custom_map, "custom_marker_map")
                print(f"✅ Map saved as {filepath}")
                
                if input("Open in browser? (y/n): ").lower() == 'y':
                    map_gen.open_in_browser(filepath)
                    
            except ValueError:
                print("❌ Invalid coordinates entered!")
        
        elif choice == '6':
            print("👋 Thank you for using Interactive Map Generator!")
            break
        
        else:
            print("❌ Invalid choice! Please select 1-6.")


if __name__ == "__main__":
    main()
