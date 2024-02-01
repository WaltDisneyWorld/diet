from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

def calculate_amr(age, weight, height, gender, activity_level):
    if gender.lower() == 'female':
        bmr = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)
    elif gender.lower() == 'male':
        bmr = 66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
    else:
        raise ValueError("Invalid gender. Please enter 'male' or 'female'.")

    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }

    amr = bmr * activity_multipliers.get(activity_level.lower(), 1.2)

    return amr

def calculate_meal_calories(amr, percentage):
    calories = amr * (percentage / 100)
    return round(calories / 50) * 50

def filter_meal_options(meal_data, target_calories):
    return meal_data[meal_data['calories'] == target_calories]['meal_name'].tolist()

@app.route('/generate_meals', methods=['POST'])
def generate_meals():
    try:
        # Get user input from JSON request
        user_input = request.json
        age = int(user_input['age'])
        weight = float(user_input['weight'])
        height = float(user_input['height'])
        gender = user_input['gender']
        activity_level = user_input['activity_level']
        weight_goal = user_input['weight_goal']

        # Percentages for meal distribution
        breakfast_percentage = 22
        lunch_percentage = 31
        dinner_percentage = 35

        # Calculate AMR
        amr = calculate_amr(age, weight, height, gender, activity_level)

        # Adjust AMR based on weight goal
        if weight_goal == 'loss':
            amr -= 200
        elif weight_goal == 'gain':
            amr += 200

        # Calculate meal calories based on percentages
        breakfast_calories = calculate_meal_calories(amr, breakfast_percentage)
        lunch_calories = calculate_meal_calories(amr, lunch_percentage)
        dinner_calories = calculate_meal_calories(amr, dinner_percentage)

        # Load meal data from CSV files
        breakfast_data = pd.read_csv('breakfast.csv')
        lunch_data = pd.read_csv('lunch.csv')
        dinner_data = pd.read_csv('dinner.csv')
        nvbreakfast_data = pd.read_csv('nvbreakfast.csv')
        nvlunch_data = pd.read_csv('nvlunch.csv')
        nvdinner_data = pd.read_csv('nvdinner.csv')

        # Filter meal options
        filtered_breakfast_options = filter_meal_options(breakfast_data, breakfast_calories)
        filtered_lunch_options = filter_meal_options(lunch_data, lunch_calories)
        filtered_dinner_options = filter_meal_options(dinner_data, dinner_calories)
        filtered_nbreakfast_options = filter_meal_options(nvbreakfast_data, breakfast_calories)
        filtered_nlunch_options = filter_meal_options(nvlunch_data, lunch_calories)
        filtered_ndinner_options = filter_meal_options(nvdinner_data, dinner_calories)

        # Create JSON response
        response = {
            'calories': {
                'calories-per-day' : amr,
                'breakfast-calories-per-day' : amr*0.22,
                'lunch-calories-per-day' : amr*0.31,
                'dinner-calories-per-day' : amr*0.35

            },
            'veg': {
                'breakfast': filtered_breakfast_options,
                'lunch': filtered_lunch_options,
                'dinner': filtered_dinner_options,
            },
            'non_veg': {
                'breakfast': filtered_nbreakfast_options,
                'lunch': filtered_nlunch_options,
                'dinner': filtered_ndinner_options,
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
