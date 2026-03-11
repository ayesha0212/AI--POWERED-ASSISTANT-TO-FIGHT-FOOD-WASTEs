def predict_expiry(food):

    data = {
        "rice":12,
        "bread":6,
        "vegetables":8,
        "fruit":10,
        "pasta":24
    }

    return data.get(food,12)