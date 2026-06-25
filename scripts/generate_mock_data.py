import pandas as pd
import numpy as np
import random
import os

def generate_mock_data(num_samples=1000):
    categories = ['Career', 'Health', 'Finance', 'Personal Development', 'Business']
    complex_words = ['scale', 'million', 'expert', 'global', 'enterprise', 'launch', 'transform', 'intensive']
    simple_words = ['start', 'learn', 'try', 'basic', 'daily', 'read', 'save']

    data = []
    for _ in range(num_samples):
        category = random.choice(categories)
        
        # Decide if this is a complex goal or simple goal
        is_complex = random.random() > 0.5
        
        if is_complex:
            title = f"{random.choice(complex_words).title()} my {category.lower()} project"
            desc_words = [random.choice(complex_words) for _ in range(random.randint(3, 8))]
            description = f"I want to fully {' '.join(desc_words)} and achieve massive success."
            difficulty = 'Hard' if random.random() > 0.3 else 'Medium'
        else:
            title = f"{random.choice(simple_words).title()} a new habit in {category.lower()}"
            desc_words = [random.choice(simple_words) for _ in range(random.randint(1, 4))]
            description = f"I am planning to {' '.join(desc_words)}."
            difficulty = 'Easy' if random.random() > 0.3 else 'Medium'

        data.append({
            'title': title,
            'description': description,
            'category': category,
            'difficulty': difficulty
        })

    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs('ml/data/raw', exist_ok=True)
    
    # Save to CSV
    output_path = 'ml/data/raw/goals_dataset.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} records and saved to {output_path}")

if __name__ == "__main__":
    generate_mock_data()
