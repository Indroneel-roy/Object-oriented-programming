import requests
import sys

# ==========================================
# CLASS 1: The Data Model
# Responsibility: Holding cleaned weather data in a neat structure.
# ==========================================
class WeatherData:
    """
    A simple class (like a container) to hold the specific weather details we care about.
    """
    def __init__(self, city, temp_celsius, condition, humidity, wind_speed):
        self.city = city
        self.temp_celsius = temp_celsius
        self.condition = condition
        self.humidity = humidity
        self.wind_speed = wind_speed

    def temp_fahrenheit(self):
        """A helper method to calculate Fahrenheit on demand."""
        return (self.temp_celsius * 9/5) + 32

    @classmethod
    def from_json(cls, json_data):
        """
        A special 'factory' method.
        It takes the messy raw JSON dictionary from the API and creates 
        a clean instance of the WeatherData class.
        """
        try:
            city_name = json_data['name']
            # API returns temp in Kelvin by default; convert to Celsius here.
            temp_k = json_data['main']['temp']
            temp_c = temp_k - 273.15
            
            # 'weather' is a list; usually the first item is primary condition.
            # .title() makes "light rain" look like "Light Rain".
            condition = json_data['weather'][0]['description'].title()
            humidity = json_data['main']['humidity']
            wind_speed = json_data['wind']['speed']

            # Return a new instance of this class initialized with clean data
            return cls(city_name, temp_c, condition, humidity, wind_speed)
        except (KeyError, IndexError) as e:
             print(f"Error parsing data structures: {e}")
             # If the JSON format changed unexpectedly, return None.
             return None


# ==========================================
# CLASS 2: The API Client
# Responsibility: Handling network requests and connection errors.
# ==========================================
class OpenWeatherClient:
    # The base URL for current weather data
    BASE_URL = "http://api.openweathermap.org/data/2.5/"

    def __init__(self, api_key):
        # The client needs the key to function
        self.api_key = api_key

    def get_current_weather_raw(self, city_name):
        """
        Connects to the internet to fetch raw data for a given city.
        Returns dictionary if successful, None if failed.
        """
        endpoint = f"{self.BASE_URL}weather"
        # These parameters are appended to the URL automatically by requests
        params = {
            'q': city_name,
            'appid': self.api_key
        }

        try:
            print(f"[Client] Connecting to API for {city_name}...")
            response = requests.get(endpoint, params=params, timeout=10)
            
            # This checks if the HTTP response code was bad (e.g., 404 or 500)
            # and raises an exception if it was.
            response.raise_for_status() 
            
            # If successful, return the Python dictionary derived from JSON
            return response.json()

        except requests.exceptions.HTTPError as errh:
            # Handle specific HTTP errors nicely
            if response.status_code == 404:
                 print(f"API Error: The city '{city_name}' was not found.")
            elif response.status_code == 401:
                 print("API Error: Your API Key is invalid or not yet active.")
            else:
                 print(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError:
            print("Connection Error: Could not reach the internet.")
        except requests.exceptions.Timeout:
            print("Connection Error: The request timed out.")
        except Exception as err:
            print(f"An Unexpected Error Occurred: {err}")
        
        # If anything went wrong, return None
        return None


# ==========================================
# CLASS 3: The User Interface
# Responsibility: Displaying data nicely to the console screen.
# ==========================================
class ConsoleUI:
    def display_header(self):
        """Just prints a nice title banner."""
        print("\n" + "="*40)
        print("       OOP PYTHON WEATHER APP       ")
        print("="*40)

    def display_weather_report(self, weather_data: WeatherData):
        """
        Takes a clean WeatherData object and prints out the results.
        It doesn't care where the data came from, only how to show it.
        """
        if weather_data is None:
             print("UI info: No valid data to display.")
             return

        print(f"\n--- Current Weather in {weather_data.city} ---")
        print(f"Condition:   {weather_data.condition}")
        # Showing the "different results" (C vs F) using the model's helper method
        print(f"Temperature: {weather_data.temp_celsius:.1f}°C  ({weather_data.temp_fahrenheit():.1f}°F)")
        print(f"Humidity:    {weather_data.humidity}%")
        print(f"Wind Speed:  {weather_data.wind_speed} m/s")
        print("------------------------------------\n")


# ==========================================
# CLASS 4: The Application Controller
# Responsibility: The boss. Tying the other classes together in a loop.
# ==========================================
class WeatherApp:
    def __init__(self, api_key):
        # Initialize the workers: the client and the UI
        self.client = OpenWeatherClient(api_key)
        self.ui = ConsoleUI()

    def run(self):
        """The main execution loop of the program."""
        self.ui.display_header()
        
        while True:
            # Get input from user
            city_input = input("Enter city name (or 'q' to quit): ").strip()

            if city_input.lower() == 'q':
                print("Exiting application. Goodbye!")
                break
            
            if not city_input:
                print("Please enter a city name.")
                continue

            # --- THE CORE OOP WORKFLOW ---
            
            # 1. Ask the Client to get raw data from the internet
            raw_json = self.client.get_current_weather_raw(city_input)
            
            if raw_json:
                # 2. Ask the Data Model to clean up that raw data
                clean_data = WeatherData.from_json(raw_json)

                if clean_data:
                    # 3. Pass the clean data to the UI to be displayed
                    self.ui.display_weather_report(clean_data)

# ==========================================
# Main Execution Block
# This runs only if you run the script directly (not imported)
# ==========================================
if __name__ == "__main__":
    # -----------------------------------------------------------
    # PASTE YOUR API KEY IN THE QUOTES BELOW
    # -----------------------------------------------------------
    YOUR_API_KEY = "4381f376eb55dc16d97b14bb798b6be3"
    # -----------------------------------------------------------
    
    # A quick check to ensure you pasted the key
    if "PASTE_YOUR_KEY" in YOUR_API_KEY:
         print("ERROR: You forgot to paste your API key at the bottom of the script!")
         sys.exit(1)

    # Create the app instance with your key and run it
    app = WeatherApp(YOUR_API_KEY)
    app.run()