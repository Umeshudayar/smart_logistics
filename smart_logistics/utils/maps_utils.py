import googlemaps
import folium
from googlemaps.convert import decode_polyline

# Replace with your Google Maps API key
GOOGLE_API_KEY = "AIzaSyCKL0Ci-lcTDZEHmC52sStOCGvAYe6dGGk"
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

def get_distance_time(pickup, delivery):
    """
    Get distance, time, and route polyline between two locations using Google Maps API
    """
    try:
        directions = gmaps.directions(pickup, delivery, mode="driving", alternatives=True)
        if directions:
            # Get the shortest route based on distance
            shortest_route = min(directions, key=lambda x: x['legs'][0]['distance']['value'])
            legs = shortest_route['legs'][0]
            
            # Get distance in km and duration in minutes
            distance = legs['distance']['value'] / 1000  # Convert to km
            duration = legs['duration']['value'] / 60    # Convert to minutes
            
            # Get polyline for route visualization
            polyline_str = shortest_route['overview_polyline']['points']
            
            return distance, duration, polyline_str
        else:
            raise Exception("No route found")
    except Exception as e:
        print(f"Google Maps API error: {e}")
        # Fallback to a simple distance estimation
        return estimate_distance_time(pickup, delivery)

def estimate_distance_time(pickup, delivery):
    """
    Fallback method to estimate distance and time when API fails
    """
    try:
        # Geocode the pickup and delivery addresses
        pickup_geocode = gmaps.geocode(pickup)
        delivery_geocode = gmaps.geocode(delivery)
        
        if pickup_geocode and delivery_geocode:
            pickup_lat, pickup_lng = pickup_geocode[0]['geometry']['location'].values()
            delivery_lat, delivery_lng = delivery_geocode[0]['geometry']['location'].values()
            
            # Calculate straight-line distance (air distance)
            from math import sin, cos, sqrt, atan2, radians
            
            R = 6371  # Earth radius in kilometers
            
            lat1, lon1 = radians(pickup_lat), radians(pickup_lng)
            lat2, lon2 = radians(delivery_lat), radians(delivery_lng)
            
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            distance = R * c
            
            # Rough estimate: assume average speed of 50 km/h
            duration = (distance / 50) * 60  # Convert to minutes
            
            # Create a dummy polyline (direct line)
            polyline_str = None
            
            return distance, duration, polyline_str
        else:
            # Last resort fallback
            return 10, 20, None  # Assume 10 km, 20 min
    except Exception as e:
        print(f"Distance estimation error: {e}")
        return 10, 20, None  # Assume 10 km, 20 min

def generate_map(pickup, delivery, polyline_str, output_path):
    """
    Generate a map visualization with the route between pickup and delivery
    """
    try:
        # Geocode the pickup and delivery addresses
        pickup_geocode = gmaps.geocode(pickup)
        delivery_geocode = gmaps.geocode(delivery)
        
        if pickup_geocode and delivery_geocode:
            pickup_lat, pickup_lng = pickup_geocode[0]['geometry']['location'].values()
            delivery_lat, delivery_lng = delivery_geocode[0]['geometry']['location'].values()
            
            # Create a map
            center_lat = (pickup_lat + delivery_lat) / 2
            center_lng = (pickup_lng + delivery_lng) / 2
            m = folium.Map(location=[center_lat, center_lng], zoom_start=10)
            
            # Add markers for pickup and delivery locations
            folium.Marker([pickup_lat, pickup_lng], 
                          popup=pickup, 
                          icon=folium.Icon(color="blue")).add_to(m)
            
            folium.Marker([delivery_lat, delivery_lng], 
                          popup=delivery, 
                          icon=folium.Icon(color="red")).add_to(m)
            
            # Add route polyline if available
            if polyline_str:
                try:
                    decoded_polyline = decode_polyline(polyline_str)
                    polyline_tuples = [(point['lat'], point['lng']) for point in decoded_polyline]
                    folium.PolyLine(locations=polyline_tuples, 
                                   color="green", 
                                   weight=5).add_to(m)
                except Exception as e:
                    print(f"Polyline decoding error: {e}")
            else:
                # If no polyline, draw a straight line
                folium.PolyLine(locations=[[pickup_lat, pickup_lng], [delivery_lat, delivery_lng]],
                               color="orange",
                               weight=5,
                               dash_array="10,10").add_to(m)
            
            # Save the map
            m.save(output_path)
            return True
        else:
            raise Exception("Could not geocode addresses")
    except Exception as e:
        print(f"Map generation error: {e}")
        # Create a simple fallback map
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Center of India
        m.save(output_path)
        return False