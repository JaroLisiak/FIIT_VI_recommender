import csv
import pandas as pd
import numpy as np
import operator
import pickle

def loadbypandas(filenameA,filenameB,min_products):
    cols1 = ['customer_id','product_id','type','timestamp']
    events = pd.read_csv(filenameA, low_memory=False,sep=',',names=cols1,usecols=range(4))
    cols2 = ['product_id','category_id']
    catalog = pd.read_csv(filenameB, low_memory=False,sep=',',names=cols2,usecols=range(2))
    print("files loaded")
    tables = pd.merge(events, catalog)
    print("files merged")

    try:

        sorted = pd.DataFrame
        sorted = tables.sort_values(by=['customer_id','timestamp'])
        print("table sorted")
        zoznam = {}
        for index, row in sorted.iterrows():
            zoznam.setdefault(row['customer_id'],[]).append({'product_id' : row['product_id'],'type' : row['type'],'timestamp' : row['timestamp'],'category_id' : row['category_id']})
        print(len(zoznam))
        #save_to_file("big_zoznam.txt",zoznam)
        removed = {}    # list vymyzanych zaznamov
        for index, data in list(zoznam.items()):
            if len(data) >= min_products:
                # ak mame 5 a viac eventov vymazem event
                x = data.pop()
                removed.setdefault(index,[]).append(x)
            else:
                # ak mam menej ako 5 eventov zmazem cely zaznam
                removed.setdefault(index,data)
                zoznam.pop(index,None)

        print("Job Done! Saving to file")
        save_to_file(filenameA + "zoznam.txt", zoznam)
        print("first file saved!")
        save_to_file(filenameA + "removed.txt",removed)
        print("second file saved!")
    except Exception as e:
        print(e)

def type_to_score(type):
    if type == "view_product":
        return 3
    if type == "add_to_cart":
        return 4
    if type == "purchase_item":
        return 5

def get_similarity(items_a, items_b,split_time):
    score = 0
    for x in items_a:
        if int(x['timestamp']) < split_time:
            for y in items_b:
                if y['timestamp'] != 'timestamp' and int(y['timestamp']) < split_time:
                    if x["product_id"] == y["product_id"]:
                        score += type_to_score(x["type"]) * type_to_score(y["type"]);


    return score

def save_to_file(filename, variable):
    with open(filename, 'wb') as handle:
        pickle.dump(variable, handle)

def load_from_file(filename):
    with open(filename, 'rb') as handle:
        return pickle.load(handle)

def find_similarities():
    # load files
    print("finding similarities")
    zoznam = load_from_file(events + "zoznam.txt")
    #similar_users = {}
    similar_users = load_from_file("similar_users.txt")
    print("file loaded")
    pos = 0
    for customer_id_a, items_a in zoznam.items():
        pos += 1
        print(pos, " / ", len(zoznam))
        if (pos >= 3300) and (pos <= 3500):
            for customer_id_b, items_b in zoznam.items():
                # select two different customers
                if customer_id_a != customer_id_b:
                    # get score for their items
                    score_ab = get_similarity(items_a, items_b)
                    if score_ab > 0:
                        # if user has some similarity, add it to list
                        similar_users.setdefault(customer_id_a,[]).append([customer_id_b,score_ab])
        else:
            pass

    sort_and_save("similar_users.txt", similar_users)
    print("done")
    return



def sort_and_save(filename,similar_users):
    try:
        sorted_similar = {}
        for index in similar_users:
            data = sorted(similar_users[index], key=operator.itemgetter(1),reverse=True)
            sorted_similar.setdefault(index,data)
        for index in sorted_similar:
            # if user has more then 5 similar users, remove others
            if len(sorted_similar[index]) > 5:
                del sorted_similar[index][5:]
        save_to_file(filename,sorted_similar)
    except Exception as e:
        print(e)

def find_similar_customer(customer_id):
    zoznam = load_from_file(events + "zoznam.txt")
    similar_users = load_from_file("similar_users.txt")


    for customer_id_b, items_b in zoznam.items():
        # select two different customers
        if customer_id != customer_id_b:
            # get score for their items
            score_ab = get_similarity(zoznam[customer_id], items_b)
            if score_ab > 0:
                # if user has some similarity, add it to list
                similar_users.setdefault(customer_id,[]).append([customer_id_b,score_ab])


    sort_and_save("similar_users.txt", similar_users)

def find_diff_items(id1,id2,split_time,big_zoznam):
    # id1 = customer pre ktoreho hladam veci
    # id2 = customer podobny id1. medzi jeho vecali hladam veci navyse
    print(id1,id2)
    if id1 in big_zoznam:
        if id2 in big_zoznam:
            id1_items = big_zoznam[id1]
            id2_items = big_zoznam[id2]
            print(len(id2_items))

            if len(id2_items) > 0:
                for x in id1_items:
                    if x['timestamp'] != 'timestamp' and int(x['timestamp']) < split_time:
                        for q in id2_items:
                            if q['timestamp'] != 'timestamp' and int(q['timestamp']) < split_time:
                                if q['product_id'] == x['product_id']:
                                    id2_items.remove(q)
                                    continue
            else:
                # podobny user nema ziadne itemy
                # toto by nemalo nastat, lebo ak by nemal itemy, tak nemoze byt podobny



            print(len(id2_items))
            if len(id2_items) > 0:
                similaritems = {}
                # ak ostava vela veci, berem posledne?
                # ziskam iba veci z rovnakej kategorie
                for x in id1_items:
                    if x['timestamp'] != 'timestamp' and int(x['timestamp']) < split_time:
                        for q in id2_items:
                            if q['timestamp'] != 'timestamp' and int(q['timestamp']) < split_time:
                                if q['category_id'] == x['category_id']:
                                    similaritems.setdefault(q['product_id'])
            else:
                # nemam veci na doporucenie

            if len(similaritems) > 1:
                # return posledne 2 itemy)

def get_recommended(customer_id):
    similar_users = load_from_file("similar_users.txt") # cust_id + similar_cust_id + score (sorted)
    zoznam = load_from_file(events + "zoznam.txt")
    big_zoznam = load_from_file("big_zoznam.txt") # all customers with all products

    try:
        #response = similar_users.get(customer_id,None)
        if customer_id in similar_users: # mam similar usera, doporucujem item medzi podobnymi a hlavnym userom.
            recommended_items = {}
            for id, score in similar_users[customer_id]:
                items = find_diff_items(customer_id,id)
                recommended_items.setdefault(id,[]).append(items)
            return recommended_items

        else: # ak nemam similar usera, tak volam funkciu na najdenie similar usera
            print("customer nema podobneho customera - hladam noveho")
            if customer_id in zoznam: # je na zozname(), ma dost zaznamoov, ale nema podobneho
                #find_similar_customer(customer_id)
                pass
            get_recommended(customer_id)

    except Exception as e:
        print(e)


minproducts = 5
events = "vi_dataset_events.csv"
catalog = "vi_dataset_catalog.csv"

# main
#loadbypandas(events,catalog,minproducts)

#find_similarities()
# doporuc pre konkretneho usera predmet/predmety


#recommended = get_recommended("1000")


#view = loadcsv("vi_dataset_events.csv","view_product")
#add = loadcsv("vi_dataset_events.csv","add_to_cart")
#buy = loadcsv("vi_dataset_events.csv","purchase_item")

#similarity = makeSimilarity(view, add, buy)


def get1(customer_id):
    # save_to_file("big_zoznam.txt",zoznam)
    zoznam = load_from_file("big_zoznam.txt")

    customer = zoznam[customer_id]
    if len(customer) >= 5:
        # ak mame 5 a viac eventov, tak zistim 80% timestampu a volam funkciu na hladanie podobnych userov
        # potom na zaklade podobnych userov doporucim predmet
        time1 = customer[0]['timestamp']
        time2 = customer[len(customer)-1]['timestamp']
        split_time = int(time1) + (int(time2) - int(time1)) * 0.8

        similar_users = {}
        for customer_id_b, items_b in zoznam.items():
            # select two different customers
            if customer_id != customer_id_b:
                # get score for their items
                score_ab = get_similarity(zoznam[customer_id], items_b,split_time)
                if score_ab > 0:
                    # if user has some similarity, add it to list
                    similar_users.setdefault(customer_id, []).append([customer_id_b, score_ab])

        # zoradenie podobnych userov podla score
        sorted_similar = {}
        for index in similar_users:
            data = sorted(similar_users[index], key=operator.itemgetter(1), reverse=True)
            sorted_similar.setdefault(index, data)
        for index in sorted_similar:
            # if user has more then 5 similar users, remove others
            if len(sorted_similar[index]) > 5:
                del sorted_similar[index][5:]


        # najdenie odporucaneho predmetu, podla podobnych userov
        if customer_id in sorted_similar: # mam similar usera, doporucujem item medzi podobnymi a hlavnym userom.
            recommended_items = {}
            for id, score in sorted_similar[customer_id]:
                items = find_diff_items(customer_id,id,split_time,zoznam)
                recommended_items.setdefault(id,[]).append(items)
            return recommended_items

        else: # ak nemam similar usera, tak volam funkciu na najdenie similar usera
            print("customer %d nema podobneho customera - hladam noveho",customer_id)
            print("Odporucam na základe top")
    else:
        # ak mam menej ako 5 eventov, tak
        print("Customer nema dostatocny pocet zaznamov.")
        print("Odporucam na základe top")











get1("1000")

























