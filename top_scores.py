from __future__ import division
__author__ = 'vinoblade'

import sqlite3,collections,json,math,random
def get_stars():
    conn = sqlite3.connect('flask.db')
    c = conn.cursor()
    city_restaurants = collections.defaultdict(list)
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
        city_restaurants[row[4]].append(tuple(row[:4]))
    return city_restaurants

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

def scoreComputing(star,population,incomes,review_count):
    income = sum(map(lambda x:float(x[0])*float(x[1]),incomes))
    star = float(star)
    population = float(population)
    review_count = float(review_count)
    score = math.exp(-(income*math.log(population))+random.random())*review_count+random.random()*10+math.exp(star)
    return score

def topScore(incPop,stars,city):
    new_stars,scores = [],[]
    for zipcode in incPop:
        for zipC in stars[city]:
            if zipcode[0] == zipC[2]:
                score = scoreComputing(zipC[0],zipcode[0],incPop[zipcode],zipC[-1])
                scores.append((zipC[1],score,zipC[2]))
    top10 = json.dumps(sorted(scores,key = lambda x:x[1],reverse=True)[:10])
    return top10

if __name__ == '__main__':
    print topScore(getIncPop(),get_stars(),'Las Vegas')
