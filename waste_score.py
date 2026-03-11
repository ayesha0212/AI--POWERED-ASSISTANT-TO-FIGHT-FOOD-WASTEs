def calculate_score(quantity,expiry):

    score = 100

    if quantity > 10:
        score -= 20

    if expiry < 5:
        score -= 30

    return score