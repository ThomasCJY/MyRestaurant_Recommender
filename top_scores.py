from __future__ import division
__author__ = 'vinoblade'

import sqlite3,collections,json,math,random

def scoreComputing(star,population,incomes,review_count):
    income = sum(map(lambda x:float(x[0])*float(x[1]),incomes))
    star = float(star)
    population = float(population)
    review_count = float(review_count)
    score = math.exp(-1/income)*math.log(population)+math.exp(star/review_count+random.random())*6
    return score

def topScore(city):
    def get_stars():
        conn = sqlite3.connect('flask.db')
        c = conn.cursor()
        stars = collections.defaultdict(list)
        for row in c.execute("select stars,restaurant_categories.name,full_address,review_count,restaurants.city from (restaurants \
 inner join restaurants_categories on restaurants.id = restaurants_categories.restaurant_id)\
  inner join restaurant_categories on restaurant_categories.id = restaurants_categories.category_id \
    ;"):
            row = list(row)
            try:
                row = map(lambda x:str(x),row)
            except:
                continue
            row[2] = row[2][-5:]
            if 'None' in row:
                continue
            stars[row[4]].append(tuple(row[:4]))
        return stars
    def getIncPop():
        conn = sqlite3.connect('flask.db')
        c = conn.cursor()
        incPop = collections.defaultdict(list)
        for row in c.execute("select level,percentage,zip_codes_income_levels.zip_code,population from zip_codes_income_levels left outer join zip_codes_population on\
                         zip_codes_population.zip_code = zip_codes_income_levels.zip_code"):
            row =list(row)
            row = map(lambda x:str(x),row)
            if 'None' in row:
                continue
            incPop[(row[2],row[3])].append(tuple(row[:2]))
        return incPop
    scores,incPop,stars = [],getIncPop(),get_stars()
    for zipcode in incPop:
        for zipC in stars[city]:
            if zipcode[0] == zipC[2]:
                score = scoreComputing(zipC[0],zipcode[0],incPop[zipcode],zipC[-1])
                scores.append((zipC[1],score,zipC[2]))
    top10 = json.dumps(sorted(scores,key = lambda x:x[1],reverse=True)[:10])
    return top10

if __name__ == '__main__':
    print topScore('Las Vegas')
