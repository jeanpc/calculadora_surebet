def custom_round(value):
    n = int(value)
    decimal = value - n
    if decimal < 0.25:
        return float(n)
    elif decimal < 0.75:
        return float(n) + 0.5
    else:
        return float(n + 1)
import difflib

def compute_surebet_three_way(odds_a, odds_b, odds_c, investment=1000):
    implied_prob_a = 1 / odds_a
    implied_prob_b = 1 / odds_b
    implied_prob_c = 1 / odds_c
    total_implied_prob = implied_prob_a + implied_prob_b + implied_prob_c
    profit_percentage = (1 / total_implied_prob - 1) * 100
    bet_a = (investment * implied_prob_a) / total_implied_prob
    bet_b = (investment * implied_prob_b) / total_implied_prob
    bet_c = (investment * implied_prob_c) / total_implied_prob
    return round(profit_percentage, 2), custom_round(bet_a), custom_round(bet_b), custom_round(bet_c)

def compute_surebet_two_way(odds_a, odds_b, investment=1000):
    implied_prob_a = 1 / odds_a
    implied_prob_b = 1 / odds_b
    total_implied_prob = implied_prob_a + implied_prob_b
    profit_percentage = (1 / total_implied_prob - 1) * 100
    bet_a = (investment * implied_prob_a) / total_implied_prob
    bet_b = (investment * implied_prob_b) / total_implied_prob
    return round(profit_percentage, 2), custom_round(bet_a), custom_round(bet_b)

def compute_surebet_two_way_with_max(odds_a, odds_b, max_a=None, max_b=None):
    implied_prob_a = 1 / odds_a
    implied_prob_b = 1 / odds_b
    total_implied_prob = implied_prob_a + implied_prob_b
    profit_percentage = (1 / total_implied_prob - 1) * 100
    if max_a is not None:
        bet_a = max_a
        bet_b = (bet_a * implied_prob_b) / implied_prob_a
    elif max_b is not None:
        bet_b = max_b
        bet_a = (bet_b * implied_prob_a) / implied_prob_b
    else:
        return round(profit_percentage, 2), None, None, None
    bet_a_r = custom_round(bet_a)
    bet_b_r = custom_round(bet_b)
    total_investment = custom_round(bet_a_r + bet_b_r)
    return round(profit_percentage, 2), bet_a_r, bet_b_r, total_investment

def compute_surebet_three_way_with_max(odds_a, odds_b, odds_c, max_a=None, max_b=None, max_c=None):
    implied_prob_a = 1 / odds_a
    implied_prob_b = 1 / odds_b
    implied_prob_c = 1 / odds_c
    total_implied_prob = implied_prob_a + implied_prob_b + implied_prob_c
    profit_percentage = (1 / total_implied_prob - 1) * 100
    if max_a is not None:
        bet_a = max_a
        bet_b = (bet_a * implied_prob_b) / implied_prob_a
        bet_c = (bet_a * implied_prob_c) / implied_prob_a
    elif max_b is not None:
        bet_b = max_b
        bet_a = (bet_b * implied_prob_a) / implied_prob_b
        bet_c = (bet_b * implied_prob_c) / implied_prob_b
    elif max_c is not None:
        bet_c = max_c
        bet_a = (bet_c * implied_prob_a) / implied_prob_c
        bet_b = (bet_c * implied_prob_b) / implied_prob_c
    else:
        return round(profit_percentage, 2), None, None, None, round(total_investment)
    bet_a_r = custom_round(bet_a)
    bet_b_r = custom_round(bet_b)
    bet_c_r = custom_round(bet_c)
    total_investment = custom_round(bet_a_r + bet_b_r + bet_c_r)
    return round(profit_percentage, 2), bet_a_r, bet_b_r, bet_c_r, total_investment

def compute_surebet_five_way_with_max(odds_a, odds_b, odds_c, odds_d, odds_e, max_a=None, max_b=None, max_c=None, max_d=None, max_e=None):
    implied_prob_a = 1 / odds_a
    implied_prob_b = 1 / odds_b
    implied_prob_c = 1 / odds_c
    implied_prob_d = 1 / odds_d
    implied_prob_e = 1 / odds_e
    total_implied_prob = implied_prob_a + implied_prob_b + implied_prob_c + implied_prob_d + implied_prob_e
    profit_percentage = (1 / total_implied_prob - 1) * 100
    if max_a is not None:
        bet_a = max_a
        bet_b = (bet_a * implied_prob_b) / implied_prob_a
        bet_c = (bet_a * implied_prob_c) / implied_prob_a
        bet_d = (bet_a * implied_prob_d) / implied_prob_a
        bet_e = (bet_a * implied_prob_e) / implied_prob_a
    elif max_b is not None:
        bet_b = max_b
        bet_a = (bet_b * implied_prob_a) / implied_prob_b
        bet_c = (bet_b * implied_prob_c) / implied_prob_b
        bet_d = (bet_b * implied_prob_d) / implied_prob_b
        bet_e = (bet_b * implied_prob_e) / implied_prob_b
    elif max_c is not None:
        bet_c = max_c
        bet_a = (bet_c * implied_prob_a) / implied_prob_c
        bet_b = (bet_c * implied_prob_b) / implied_prob_c
        bet_d = (bet_c * implied_prob_d) / implied_prob_c
        bet_e = (bet_c * implied_prob_e) / implied_prob_c
    elif max_d is not None:
        bet_d = max_d
        bet_a = (bet_d * implied_prob_a) / implied_prob_d
        bet_b = (bet_d * implied_prob_b) / implied_prob_d
        bet_c = (bet_d * implied_prob_c) / implied_prob_d
        bet_e = (bet_d * implied_prob_e) / implied_prob_d
    elif max_e is not None:
        bet_e = max_e
        bet_a = (bet_e * implied_prob_a) / implied_prob_e
        bet_b = (bet_e * implied_prob_b) / implied_prob_e
        bet_c = (bet_e * implied_prob_c) / implied_prob_e
        bet_d = (bet_e * implied_prob_d) / implied_prob_e
    else:
        return round(profit_percentage, 2), None, None, None, None, None, None
    bet_a_r = custom_round(bet_a)
    bet_b_r = custom_round(bet_b)
    bet_c_r = custom_round(bet_c)
    bet_d_r = custom_round(bet_d)
    bet_e_r = custom_round(bet_e)
    total_investment = custom_round(bet_a_r + bet_b_r + bet_c_r + bet_d_r + bet_e_r)
    return round(profit_percentage, 2), bet_a_r, bet_b_r, bet_c_r, bet_d_r, bet_e_r, total_investment