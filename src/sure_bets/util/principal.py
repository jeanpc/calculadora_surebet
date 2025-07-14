from calculadora_surebet import compute_surebet_three_way, compute_surebet_two_way, compute_surebet_two_way_with_max, compute_surebet_three_way_with_max

# Ejemplo de uso con los datos proporcionados
# Apostar en A (1.93): 800.00 | B (4.3): 359.00 | C (4.05): 381.00

odds_a = 1.93
odds_b = 4.3
odds_c = 4.05

investment = 10000  # Monto total a invertir
max_a = 800 #271.62  #100/(odds_a-1)   # Monto máximo que puedes colocar en odds_a
max_b = None  #49.38  # No se especifica un monto máximo para odds_b
max_c = None # No se especifica un monto máximo para odds_c

profit_percentage = 0.3
#odds_a = odds_a*(1+profit_percentage)-profit_percentage#2*odds_a-1 # Aumentar el valor de odds_a

bet_c = None
#profit_percentage, bet_a, bet_b, investment = compute_surebet_two_way_with_max(odds_a, odds_b, max_a=max_a, max_b=max_b)
#profit_percentage, bet_a, bet_b, bet_c, investment = compute_surebet_three_way_with_max(odds_a, odds_b, odds_c, max_a=max_a, max_b=max_b, max_c=max_c)

profit_percentage, bet_a, bet_b, bet_c = compute_surebet_three_way(odds_a, odds_b, odds_c, investment)
#profit_percentage, bet_a, bet_b = compute_surebet_two_way(odds_a, odds_b, investment)

print(f"Inversion: {investment} soles")
print(f"Ganacia neta: {round(investment*profit_percentage/100,2)} ({profit_percentage}%)")
print(f"Apostar en odds_a {odds_a}: {bet_a} soles")
print(f"Apostar en odds_b {odds_b}: {bet_b} soles")
print(f"Apostar en odds_c {odds_c}: {bet_c} soles")

#print(f"Apostar en odds_d {odds_d}: {bet_d} soles")
#print(f"Apostar en odds_e {odds_e}: {bet_e} soles")

#print(f"E1: {bet_a+bet_b} soles")
#print(f"E2: {bet_a+bet_c} soles")
#print(f"E3: {bet_b+bet_c} soles")