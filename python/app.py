from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# --- Core Planner Logic (Moved from JS to Python) ---

def calculate_plan(data):
    """Calculates the budget allocation and itinerary based on user input."""
    
    user_name = data.get('user_name')
    destination = data.get('destination')
    budget = float(data.get('budget'))
    num_days = int(data.get('days'))
    travel_style = data.get('travel_style')
    age = int(data.get('age'))
    currency = data.get('currency')
    start_date_str = data.get('start_date')
    
    # 1. Budget Allocation Logic
    accommodation_ratio = 0.40
    if age < 30:
        accommodation_ratio = 0.30 
    if travel_style == 'Fast-paced':
        accommodation_ratio = 0.35 

    ratios = {
        'Lodging (Inns) 🏨': accommodation_ratio,
        'Transport (Brooms) ✈️': 0.20,
        'Feasts & Butterbeer 🍽️': 0.17,
        'Quests & Tours 🎟️': 0.12 + (0.40 - accommodation_ratio), 
        'Trinkets 🛍️': 0.06,
        'Dark Arts Defense (Savings) 💸': 0.05,
    }

    allocation = {}
    for category, ratio in ratios.items():
        allocation[category] = round(budget * ratio)

    est_total_cost = sum(allocation.values())
    
    # 2. Itinerary Generation Logic
    itinerary = generate_itinerary(destination, num_days, travel_style, allocation, start_date_str, currency)

    # 3. Summary Generation
    trip_title = f'⚡ {num_days}-Day {travel_style} Adventure to {destination}'
    brief_idea = (f'Greetings, **{user_name}**! The prophecy suggests a journey tailored to your {age} years. '
                  f'We have balanced your **{currency}{budget:,.0f}** to ensure maximum magic.')
    
    return {
        'trip_title': trip_title,
        'brief_idea': brief_idea,
        'estimated_cost': est_total_cost,
        'allocation': allocation,
        'itinerary': itinerary
    }

def generate_itinerary(destination, num_days, style, allocation, start_date_str, currency):
    """Generates a sample itinerary."""
    itinerary = []
    
    # Matching keys from the allocation dictionary
    food_key = 'Feasts & Butterbeer 🍽️'
    misc_key = 'Trinkets 🛍️'
    act_key = 'Quests & Tours 🎟️'
    stay_key = 'Lodging (Inns) 🏨'
    
    daily_food_misc = (allocation.get(food_key, 0) + allocation.get(misc_key, 0)) / num_days
    # Only budget accommodation for num_days - 1 nights
    daily_accommodation = allocation.get(stay_key, 0) / (num_days - 1) if num_days > 1 else allocation.get(stay_key, 0)
    
    try:
        current_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        current_date = datetime.now() # Fallback
        
    for i in range(1, num_days + 1):
        day_activities = []
        daily_cost = 0
        
        day_header = f'Day {i} ({current_date.strftime("%b %d")}): '

        if i == 1:
            day_header += 'Arrival via Portkey'
            day_activities.append({'time': 'Morning', 'desc': f'Apparate at {destination}. Check into lodgings.', 'cost': 0})
            day_activities.append({'time': 'Evening', 'desc': 'Visit the shoreline (Beach) for sunset.', 'cost': daily_food_misc * 0.5})
            daily_cost += daily_accommodation
        elif i == num_days:
            day_header += 'Departure (Mischief Managed)'
            day_activities.append({'time': 'Morning', 'desc': 'Final visit to shops.', 'cost': 500})
            day_activities.append({'time': 'Lunch', 'desc': 'The Leaving Feast.', 'cost': daily_food_misc * 0.6})
        else:
            day_header += f'{style} Exploration'
            activity_budget = round(allocation.get(act_key, 0) / (num_days - 2) if num_days > 2 else allocation.get(act_key, 0))
            day_activities.append({'time': 'Morning', 'desc': 'Major Quest (e.g., Kailasagiri or Temple).', 'cost': activity_budget * 0.5})
            day_activities.append({'time': 'Afternoon', 'desc': 'Leisure or Museum visit.', 'cost': 300})
            day_activities.append({'time': 'Evening', 'desc': 'Dinner and Night Life.', 'cost': daily_food_misc * 0.7})
            daily_cost += daily_accommodation

        daily_cost = round(daily_cost + sum(activity['cost'] for activity in day_activities))
        
        itinerary.append({
            'day': i, 
            'title': day_header, 
            'activities': day_activities, 
            'estCost': daily_cost
        })
        
        current_date += timedelta(days=1)
        
    return itinerary

# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the main planner page (index.html)."""
    return render_template('index.html')

@app.route('/api/generate_plan', methods=['POST'])
def generate_plan_api():
    """API endpoint for generating the trip plan."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No magic inputs provided.'}), 400
    
    try:
        plan_results = calculate_plan(data)
        return jsonify(plan_results)
    except Exception as e:
        app.logger.error(f"Error during plan generation: {e}")
        return jsonify({'error': f'A powerful Confundus Charm disrupted the plan: {e}'}), 500

@app.route('/api/convert_currency', methods=['POST'])
def convert_currency_api():
    """
    (Optional) API endpoint for real-time currency conversion. 
    This is not strictly necessary as the JS handles it with dummy data.
    """
    data = request.get_json()
    amount = float(data.get('amount', 0))
    from_currency = data.get('from', '₹')
    to_currency = data.get('to', '$')

    # Real-world integration would call an external financial API here.
    # For this project, we'll keep the dummy rates from the JS
    rates = {
        '₹': {'$': 0.012, 'G': 0.002},
        '$': {'₹': 83.0, 'G': 0.16},
        'G': {'₹': 500.0, '$': 6.0}
    }
    
    result = amount
    if from_currency != to_currency and from_currency in rates and to_currency in rates[from_currency]:
        result = amount * rates[from_currency][to_currency]
    
    return jsonify({
        'result': round(result, 2),
        'currency': to_currency
    })

if __name__ == '__main__':
    # Set debug=True for development.
    # On a production server (like a cloud instance), you would run with Gunicorn:
    # gunicorn app:app -w 4 -b 0.0.0.0:8000
    app.run(debug=True)

# Note: For production use, the Python currency conversion should use a real API like fixer.io or similar.