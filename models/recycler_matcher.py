import json
import math
from typing import List, Dict, Tuple
from geopy.distance import geodesic
import os

class RecyclerMatcher:
    """
    Matches waste materials with nearby recyclers based on location and material compatibility
    """
    
    def __init__(self, recyclers_file_path: str = "../data/recyclers.json"):
        """
        Initialize the recycler matcher with recycler data
        
        Args:
            recyclers_file_path: Path to JSON file containing recycler information
        """
        # Handle different possible file paths
        possible_paths = [
            recyclers_file_path,
            os.path.join(os.path.dirname(__file__), "..", "data", "recyclers.json"),
            os.path.join(os.path.dirname(__file__), "data", "recyclers.json"),
            os.path.join(os.getcwd(), "data", "recyclers.json"),
            "data/recyclers.json"
        ]
        
        self.recyclers = []
        for path in possible_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.recyclers = json.load(f)
                    print(f"Loaded recyclers data from: {path}")
                    break
            except FileNotFoundError:
                continue
            except json.JSONDecodeError:
                print(f"Could not parse JSON from {path}")
                continue
        
        if not self.recyclers:
            print("Warning: Could not load recyclers data. Using empty list.")
    
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        Calculate distance between two GPS coordinates in kilometers
        
        Args:
            point1: (latitude, longitude) of first point
            point2: (latitude, longitude) of second point
            
        Returns:
            Distance in kilometers
        """
        return geodesic(point1, point2).kilometers
    
    def find_nearby_recyclers(self, 
                             user_location: Tuple[float, float], 
                             material_type: str, 
                             max_distance: float = 20.0,
                             max_results: int = 5) -> List[Dict]:
        """
        Find recyclers near the user location that accept the specified material
        
        Args:
            user_location: (latitude, longitude) of user
            material_type: Type of material to recycle (e.g., 'PET', 'HDPE', 'hazardous')
            max_distance: Maximum distance in km to search (default 20km)
            max_results: Maximum number of results to return (default 5)
            
        Returns:
            List of recyclers sorted by distance
        """
        if not self.recyclers:
            return []
        
        # Normalize material type
        material_type = material_type.upper().strip()
        
        # Filter recyclers that accept the material and are within distance
        matching_recyclers = []
        
        for recycler in self.recyclers:
            # Check if recycler accepts this material
            materials_accepted = [mat.upper() for mat in recycler.get('materials', [])]
            
            # For hazardous materials, look for recyclers that handle hazardous materials
            if material_type in ['HAZARDOUS', 'CHEMICAL', 'MEDICAL', 'BATTERY'] or \
               'HAZARDOUS' in materials_accepted or 'CHEMICAL' in materials_accepted:
                # These recyclers handle hazardous materials
                if any(hazard in materials_accepted for hazard in ['HAZARDOUS', 'CHEMICAL', 'MEDICAL', 'BATTERIES', 'E-WASTE']):
                    recycler_location = (
                        recycler['location']['latitude'], 
                        recycler['location']['longitude']
                    )
                    distance = self.calculate_distance(user_location, recycler_location)
                    
                    if distance <= max_distance:
                        recycler_copy = recycler.copy()
                        recycler_copy['distance'] = round(distance, 2)
                        
                        # Set appropriate rate for hazardous materials
                        if 'rates' in recycler and material_type in recycler['rates']:
                            recycler_copy['rate'] = recycler['rates'][material_type]
                        else:
                            recycler_copy['rate'] = 'Varies by material'
                            
                        matching_recyclers.append(recycler_copy)
            
            # For regular materials, check if it's in accepted materials
            elif material_type in materials_accepted:
                recycler_location = (
                    recycler['location']['latitude'], 
                    recycler['location']['longitude']
                )
                distance = self.calculate_distance(user_location, recycler_location)
                
                if distance <= max_distance:
                    recycler_copy = recycler.copy()
                    recycler_copy['distance'] = round(distance, 2)
                    
                    # Set the rate for this specific material
                    if 'rates' in recycler and material_type in recycler['rates']:
                        recycler_copy['rate'] = recycler['rates'][material_type]
                    else:
                        recycler_copy['rate'] = 'Rate available on inquiry'
                        
                    matching_recyclers.append(recycler_copy)
        
        # Sort by distance
        matching_recyclers.sort(key=lambda x: x['distance'])
        
        # Return top N results
        return matching_recyclers[:max_results]
    
    def get_best_recycler_by_criteria(self, 
                                   user_location: Tuple[float, float],
                                   material_type: str,
                                   criteria: str = 'distance') -> List[Dict]:
        """
        Get recyclers sorted by different criteria
        
        Args:
            user_location: (latitude, longitude) of user
            material_type: Type of material to recycle
            criteria: Sorting criteria ('distance', 'rate', 'capacity')
            
        Returns:
            List of recyclers sorted by specified criteria
        """
        nearby_recyclers = self.find_nearby_recyclers(user_location, material_type)
        
        if criteria == 'distance':
            # Already sorted by distance
            return nearby_recyclers
        elif criteria == 'rate':
            # Sort by highest rate first
            return sorted(nearby_recyclers, key=lambda x: 
                         x.get('rate', 0) if isinstance(x.get('rate'), (int, float)) else 0, 
                         reverse=True)
        elif criteria == 'capacity':
            # Sort by capacity (parse capacity string to get numeric value)
            def extract_capacity(capacity_str):
                import re
                # Extract number from string like "15 tons/day"
                match = re.search(r'(\d+)', str(capacity_str))
                return int(match.group(1)) if match else 0
            
            return sorted(nearby_recyclers, 
                         key=lambda x: extract_capacity(x.get('capacity', '0')),
                         reverse=True)
        else:
            return nearby_recyclers
    
    def get_material_specific_recyclers(self, 
                                      user_location: Tuple[float, float],
                                      material_category: str) -> List[Dict]:
        """
        Get recyclers based on broader material categories
        
        Args:
            user_location: (latitude, longitude) of user
            material_category: Broader category ('plastic', 'metal', 'paper', 'hazardous', 'electronic')
            
        Returns:
            List of recyclers that handle the category
        """
        category_mappings = {
            'plastic': ['PET', 'HDPE', 'LDPE', 'PP', 'PS', 'PVC', 'PLASTIC'],
            'metal': ['METAL', 'STEEL', 'ALUMINIUM', 'IRON'],
            'paper': ['PAPER', 'CARDBOARD', 'NEWSPAPER', 'MAGAZINE'],
            'hazardous': ['HAZARDOUS', 'CHEMICAL', 'MEDICAL', 'BATTERY', 'PESTICIDE'],
            'electronic': ['ELECTRONICS', 'E-WASTE', 'COMPUTER', 'PHONE', 'CIRCUIT']
        }
        
        if material_category.lower() not in category_mappings:
            return []
        
        materials_in_category = category_mappings[material_category.lower()]
        
        # Find recyclers that accept any material in this category
        matching_recyclers = []
        for recycler in self.recyclers:
            recycler_materials = [mat.upper() for mat in recycler.get('materials', [])]
            
            # Check if there's any overlap between materials
            if any(mat in recycler_materials for mat in materials_in_category):
                recycler_location = (
                    recycler['location']['latitude'], 
                    recycler['location']['longitude']
                )
                distance = self.calculate_distance(user_location, recycler_location)
                
                if distance <= 20.0:  # Within 20km
                    recycler_copy = recycler.copy()
                    recycler_copy['distance'] = round(distance, 2)
                    recycler_copy['materials_match'] = [
                        mat for mat in recycler_materials 
                        if mat in materials_in_category
                    ]
                    matching_recyclers.append(recycler_copy)
        
        # Sort by distance
        matching_recyclers.sort(key=lambda x: x['distance'])
        return matching_recyclers[:5]  # Return top 5
    
    def get_recycler_details(self, recycler_id: str) -> Dict:
        """
        Get detailed information about a specific recycler
        
        Args:
            recycler_id: Unique identifier for the recycler
            
        Returns:
            Detailed information about the recycler
        """
        for recycler in self.recyclers:
            if recycler.get('id') == recycler_id:
                return recycler
        
        return {}

# Example usage and testing
def test_recycler_matcher():
    """
    Test function to verify RecyclerMatcher works correctly
    """
    # Use a location in Delhi for testing
    delhi_location = (28.6139, 77.2090)
    
    matcher = RecyclerMatcher()
    
    # Test finding recyclers for PET plastic
    pet_recyclers = matcher.find_nearby_recyclers(delhi_location, 'PET')
    print(f"Found {len(pet_recyclers)} recyclers for PET in Delhi area:")
    for recycler in pet_recyclers:
        print(f"- {recycler['name']} ({recycler['distance']} km, ₹{recycler['rate']}/kg)")
    
    # Test finding recyclers for hazardous materials
    hazardous_recyclers = matcher.find_nearby_recyclers(delhi_location, 'HAZARDOUS')
    print(f"\nFound {len(hazardous_recyclers)} hazardous waste handlers in Delhi area:")
    for recycler in hazardous_recyclers:
        print(f"- {recycler['name']} ({recycler['distance']} km)")
    
    return matcher

if __name__ == "__main__":
    test_recycler_matcher()