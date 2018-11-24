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


def jaccard_similarity(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality / float(union_cardinality)

def type_to_score(type):
    if type == "view_product":
        return 3
    if type == "add_to_cart":
        return 4
    if type == "purchase_item":
        return 5

def get_similarity(items_a, items_b):
    score = 0
    for x in items_a:
        for y in items_b:
            if x["product_id"] == y["product_id"]:
                score += type_to_score(x["type"]) * type_to_score(y["type"]);
            elif x["category_id"] == y["category_id"]:
                score += 1

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
    zoznam = load_from_file(events + "zoznam.txt",)
    #similar_users = {}
    similar_users = load_from_file("similar_users.txt")
    print("file loaded")
    pos = 0
    for customer_id_a, items_a in zoznam.items():
        pos += 1
        print(pos, " / ", len(zoznam))
        if (pos >= 1600) and (pos <= 2000):
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









def loadcsv(filename, event):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        user_product = {}
        for row in reader:
            if row['type'] == event:
                user_product.setdefault(row['customer_id'], []).append(row['product_id'])
    print("[OK] - "+ event +" [%d records]" % len(user_product))
    return user_product


def loadcsv(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
    return reader

# for every customer find top 5 similar customers
def makeSimilarity(view, add, buy):
    # [customer_id,list [similar customers id, score]]
    user_similarity = {}


minproducts = 5
events = "vi_dataset_events.csv"
catalog = "vi_dataset_catalog.csv"

# main
#loadbypandas(events,catalog,minproducts)

find_similarities()


#view = loadcsv("vi_dataset_events.csv","view_product")
#add = loadcsv("vi_dataset_events.csv","add_to_cart")
#buy = loadcsv("vi_dataset_events.csv","purchase_item")

#similarity = makeSimilarity(view, add, buy)
