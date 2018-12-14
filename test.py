import csv
import difflib
import pandas as pd
import numpy as np
import operator
import math
import pickle
from collections import Counter



def type_to_score(type):
    if type == "view_product":
        return 3
    if type == "add_to_cart":
        return 4
    if type == "purchase_item":
        return 5

def get_similarity(items_a, items_b,split_time):
    # vypocitaj score medzi produktami dvoch pouzivatelov
    # do prehladavania zahrnie aj timestamp < 80%
    score = 0
    for x in items_a:
        if int(x['timestamp']) < split_time:
            for y in items_b:
                if y['timestamp'] != 'timestamp' and int(y['timestamp']) < split_time:
                    if x["product_id"] == y["product_id"]:
                        score += type_to_score(x["type"]) * type_to_score(y["type"]);

                        # experimentalne pocitanie score na zaklade categorie.
                    #elif x["category_id"] == y["category_id"]:
                     #   score += 0.1
    return score

def save_to_file(filename, variable):
    with open(filename, 'wb') as handle:
        pickle.dump(variable, handle)

def load_from_file(filename):
    with open(filename, 'rb') as handle:
        return pickle.load(handle)


def find_diff_items(id1,id2,split_time,big_zoznam):
    # id1 = customer pre ktoreho hladam veci
    # id2 = customer podobny id1. medzi jeho vecali hladam veci navyse
    try:
        if id1 in big_zoznam:
            if id2 in big_zoznam:
                id1_items = big_zoznam[id1]
                id2_items = big_zoznam[id2]

                if len(id2_items) > 0:
                    # z id2_items odstranim vsetky rovnake - ostanu rozdielne itemy
                    for x in id1_items:
                        if x['timestamp'] != 'timestamp' and int(x['timestamp']) < split_time:
                            for q in id2_items:
                                if q['timestamp'] != 'timestamp' and int(q['timestamp']) < split_time:
                                    if q['product_id'] == x['product_id']:
                                        id2_items.remove(q)
                                        continue
                else:
                    pass
                    # podobny user nema ziadne itemy
                    # toto by nemalo nastat, lebo ak by nemal itemy, tak nemoze byt podobny


                similaritems = {}
                if len(id2_items) > 0:
                    # do noveho zoznamu dam iba itemy rovnakej kategorie

                    # ak ostava vela veci, berem posledne?
                    # ziskam iba veci z rovnakej kategorie
                    for x in id1_items:
                        if x['timestamp'] != 'timestamp' and int(x['timestamp']) < split_time:
                            for q in id2_items:
                                if q['timestamp'] != 'timestamp' and int(q['timestamp']) < split_time:
                                    if q['category_id'] == x['category_id']:
                                            similaritems.setdefault(q['timestamp'],q['product_id'])
                else:
                    pass
                    # nemam veci na doporucenie

                if len(similaritems) > 1:
                    return list(similaritems.values())[-1:]
                    # return posledne 2 itemy
    except Exception as e:
        print(e)


def get1(customer_id,zoznam):
    try:
        customer = zoznam[customer_id]
        time1 = customer[0]['timestamp']
        time2 = customer[len(customer) - 1]['timestamp']
        split_time = int(time1) + (int(time2) - int(time1)) * 0.8 # 80% timestampu

        if len(customer) >= 5:
            # ak mame 5 a viac eventov, tak zistim 80% timestampu a volam funkciu na hladanie podobnych userov
            # potom na zaklade podobnych userov doporucim predmet

            similar_users = {}
            for customer_id_b, items_b in zoznam.items():
                # prejdi vsetkych ostatnych userov
                if customer_id != customer_id_b:
                    # ziskaj score na zaklade ich predmetov
                    score_ab = get_similarity(zoznam[customer_id], items_b,split_time)
                    if score_ab > 0:
                        # ak je medzi usermi podobnost, pridaj ho do listu
                        similar_users.setdefault(customer_id, []).append([customer_id_b, score_ab])

            # zoradenie podobnych userov podla score
            sorted_similar = {}
            for index in similar_users:
                # prechadzaj vsetkych podobnych userov a zorad ich podla score
                data = sorted(similar_users[index], key=operator.itemgetter(1), reverse=True)
                sorted_similar.setdefault(index, data)
            for index in sorted_similar:
                # ak ma user viac ako 5 podobnych userov, nechaj prvych TOP 5, ostatnych vymaz
                if len(sorted_similar[index]) > 5:
                    del sorted_similar[index][5:]


            # najdenie odporucaneho predmetu, podla podobnych userov
            if customer_id in sorted_similar:
                # Pre kazdeho z TOP5 podobnych userov najdi 2 najlepsie predmety
                recommended_items = []
                for id, score in sorted_similar[customer_id]:
                    items = find_diff_items(customer_id,id,split_time,zoznam)   # vrati 2 TOP predmety pre daneho podobneho usera
                    if items is not None:
                        recommended_items += items  # prida 2 odporucane predmety do zoznamu odporucanych

                return list(recommended_items), split_time  # vrat zoznam odporucanych

            else:
                # ak nemam similar usera, tak odporucam TOP
                return topItems(split_time, zoznam), split_time
        else:
            # ak mam menej ako 5 eventov, tak
            return topItems(split_time,zoznam),split_time
    except Exception as e:
        print("Customer neexistuje:",e)

def topItems(split_time,zoznam):
    # najdi najcastejsie produkty do daneho casu
    try:
        dd = []
        for items in zoznam.values():
            # strav zoznam vsetkych predmetov, vsetkych userov
            for y in items:
                if y['timestamp'] != 'timestamp' and int(y['timestamp']) < split_time:
                    dd.append(int(y['product_id']))
        # zoorad a vyber 5 najcastejsich produktov
        #ss = sorted(dd,key=dd.count,reverse=True)
        ss = Counter(dd).most_common(5)
        sa = []
        for w,e in ss:
            sa.append(w)


        return sa
    except Exception as e:
        print(e)


def unique_no_sort(list1):
    # intilize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        x = int(x)
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def unique(list1):
    # intilize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        x = int(x)
        if x not in unique_list:
            unique_list.append(x)
    return sorted(unique_list)

def getfuture(customer_id,split_time,zoznam,count):
    # ziskaj produkty PO 80% timestampe
    items = zoznam[customer_id]
    future_list = []
    a = 0
    for x in items:
        if int(x['timestamp']) >= split_time and a <= count:
            future_list.append(x['product_id'])
            a +=1
    return unique(future_list)



def isTheSame(c1,c2,catalog):
    # povodne vyhodnocovanie
    #return c1 == c2 # zakomentovat ak chceme pouzit vylepsene vyhodnocovanie

    # vypelsene vyhodnocovanie
    if c1 == c2:
        return True
    try:
        it1 = catalog[str(c1)]
        it2 = catalog[str(c2)]

        if it1[0]['category_id'] == it2[0]['category_id'] and it1[0]['category_path'] == it2[0]['category_path'] and it1[0]['brand'] == it2[0]['brand'] and it1[0]['gender'] == it2[0]['gender'] and it1[0]['price'] == it2[0]['price']:
            return True
        else:
            return False

    except Exception as e:
        print(e)



def vyhodnot(recommended,future,catalog):
    if len(recommended) == 0 or len(future) == 0:
        return 0,0
    hit = 0

    for r1 in recommended:
        for f1 in future:
            if isTheSame(r1,f1,catalog):
                hit +=1
    return hit/len(recommended) , hit/len(future)

def x():
    # pomocny kod na vygenerovanie katalogu predmetov
    try:
        cols = ['product_id','category_id','category_path','brand','gender', 'description','price']
        catalog = pd.read_csv("vi_dataset_catalog.csv", low_memory=False, sep=',', names=cols, usecols=range(7))

        cat = {}
        for index, i in catalog.iterrows():
            cat.setdefault(i['product_id'],[]).append({'category_id' : i['category_id'],'category_path' : i['category_path'],'brand' : i['brand'],'gender' : i['gender'],'description' : i['description'],'price' : i['price']})

        save_to_file("catalog.txt", cat)
        print("done")
    except Exception as e:
        print(e)
#x()



#3, 4, 10, 21,23, 28
# presne 25, 26, 29, 31

users = []

users10 = [25, 46753, 82470, 43182, 6, 11207, 60958, 1192, 72282, 58889]
users50 = [9783, 12565, 1162, 20612, 48250, 37206, 27347, 31335, 26, 65184, 256, 67081, 29172, 84603, 10946, 61830, 79471, 52667, 17915, 73966, 18515, 35207, 42914, 52400, 26159, 31327, 84593, 45175, 20250, 69253, 81219, 62604, 717, 60359, 19790, 85001, 66114, 54015, 31130, 82660, 55272, 26223, 26613, 49206, 73482, 25773, 62247, 1670, 19060, 30945, 59480]
users100 = [5257, 84614, 47996, 39305, 58085, 33244, 8660, 26321, 85115, 43797, 69969, 54358, 21970, 29, 34174, 14007, 44570, 4997, 39795, 48559, 31564, 58674, 65602, 22944, 81901, 1071, 76577, 5660, 33181, 2965, 32373, 49754, 44236, 10477, 26860, 27061, 3310, 1912, 45937, 59167, 33474, 48340, 25715, 66820, 33894, 2745, 36120, 4751, 19839, 44981, 58168, 31972, 60368, 69686, 49605, 83618, 71934, 35207, 61095, 71761, 57212, 47973, 36555, 19072, 54285, 33069, 53961, 9866, 16345, 33813, 64745, 43978, 69465, 61869, 43111, 52703, 69481, 45326, 73265, 41135, 680, 2342, 81882, 3048, 6539, 78099, 78597, 27171, 21678, 2690, 56692, 13072, 42894, 48977, 24198, 34728, 38192, 33826, 80207, 11, 30348]
users500 = [58737, 16347, 17475, 47295, 49489, 13725, 81862, 68108, 31022, 40547, 7571, 76917, 60254, 310, 10872, 18818, 28189, 769, 29657, 31, 23457, 77872, 83353, 152, 56020, 3375, 35902, 51797, 56875, 56103, 36832, 61485, 43597, 76537, 45844, 72389, 39058, 7454, 16182, 71767, 35121, 35975, 20012, 35818, 60185, 8107, 67301, 31997, 55980, 38267, 36220, 46737, 77713, 33977, 35463, 81485, 60297, 75503, 52906, 85519, 45415, 85447, 83821, 47185, 21280, 43426, 74009, 76953, 32776, 20509, 23211, 62415, 71149, 20484, 29660, 44139, 13635, 58378, 34196, 38322, 34559, 24526, 31838, 55402, 11204, 62074, 76253, 75086, 55043, 14822, 35749, 29670, 35949, 58737, 52430, 74290, 75867, 73660, 48238, 29692, 76460, 67382, 51630, 53151, 80003, 79059, 24782, 57140, 62192, 64427, 34242, 72735, 46918, 46527, 1149, 53026, 23658, 34852, 82508, 20400, 66586, 9803, 36034, 64295, 81144, 10218, 48311, 80890, 34633, 55556, 26570, 66868, 19528, 7866, 36883, 83783, 11653, 43153, 26396, 42754, 29880, 45918, 6310, 83699, 23917, 44511, 17299, 11753, 36955, 22252, 12980, 50829, 29672, 15371, 54302, 32716, 6964, 61680, 52129, 17014, 52580, 70817, 64983, 82937, 47072, 10634, 12601, 24109, 1725, 21085, 83282, 78394, 75861, 54299, 34488, 70400, 6840, 49722, 40783, 19298, 12615, 69607, 69654, 85668, 30365, 71241, 16918, 67193, 6789, 18790, 32772, 82759, 28725, 15133, 46963, 41155, 46426, 45550, 33438, 8101, 45897, 27968, 336, 24298, 59141, 13446, 1802, 34142, 20504, 27117, 31867, 31883, 23404, 52899, 68340, 40628, 83808, 18777, 30674, 12906, 42872, 34798, 41774, 36185, 69407, 25331, 55950, 83722, 38663, 66155, 3946, 18971, 60738, 64944, 60225, 59887, 60145, 43611, 52196, 31257, 21024, 47427, 16376, 64055, 1823, 5918, 30043, 45138, 47346, 26917, 31483, 60295, 29721, 80902, 48326, 67041, 15132, 53678, 23347, 22103, 69522, 10068, 52367, 52642, 75629, 22961, 18797, 42146, 39106, 74387, 84792, 50609, 31280, 1389, 54045, 15701, 20714, 71547, 79482, 28740, 49205, 60324, 45681, 18557, 60201, 63747, 85946, 22819, 62382, 73402, 28214, 2528, 68266, 10279, 8012, 29868, 53553, 55254, 66952, 60779, 78697, 4646, 80304, 61376, 83407, 35075, 34751, 9206, 72628, 19505, 9628, 31550, 85907, 63418, 84547, 22554, 85366, 47473, 73591, 36721, 51195, 36492, 70726, 13459, 27178, 10178, 8040, 43053, 7041, 63814, 50911, 42675, 49103, 39603, 28435, 45050, 31628, 11008, 38491, 72574, 63330, 29515, 45945, 73983, 12878, 60952, 57896, 55539, 6361, 34849, 85379, 37851, 25303, 19392, 33507, 7035, 66855, 1210, 33388, 2383, 39987, 15420, 10609, 38767, 72927, 78989, 17830, 67420, 71676, 58267, 36647, 46860, 76122, 7583, 10736, 19269, 2805, 67804, 38262, 65215, 23582, 37726, 35414, 69433, 71683, 10608, 76112, 26995, 14298, 23697, 46758, 77699, 27432, 42273, 23809, 3461, 25231, 53236, 75381, 81195, 24204, 57642, 9880, 48240, 31426, 11483, 9339, 7909, 82107, 16653, 77411, 81033, 42670, 42597, 50840, 63095, 21261, 75421, 25734, 23820, 76601, 49960, 72565, 15287, 76465, 67078, 45003, 70615, 83575, 43890, 54666, 67468, 71526, 83359, 53011, 16307, 60486, 83092, 31760, 15722, 63162, 58620, 55703, 46996, 41580, 72248, 22938, 63418, 50208, 15367, 75015, 8870, 36498, 15910, 8070, 4012, 51653, 42727, 25683, 85907, 975, 57021, 23229, 59627, 42021, 50514, 5519, 59591, 14975, 38812, 20266, 2639, 56548, 53131, 22055, 6802, 79262, 51891, 39888, 41026, 43453, 1694, 25607, 74590, 38025, 38824, 81878, 75347, 54465, 40329, 82077, 70380, 83356, 70774, 84772, 18307, 51870, 43407]
users1000 = [70646, 51451, 63540, 13704, 3600, 30752, 29126, 78752, 42779, 56526, 6954, 16533, 7932, 16410, 1438, 81417, 20091, 7476, 85071, 73700, 43200, 72755, 80074, 9982, 80567, 2839, 82816, 428, 11532, 47168, 353, 67995, 24746, 44279, 21205, 66563, 52787, 57835, 20668, 70586, 2686, 62654, 11578, 71830, 82618, 66599, 27408, 11187, 67905, 48960, 75438, 45510, 78220, 7804, 47071, 11874, 27939, 84504, 33237, 14347, 38420, 37221, 81200, 78297, 76030, 85610, 33793, 66979, 57372, 20197, 78130, 6487, 6787, 53913, 9461, 32917, 32621, 80343, 56405, 31722, 69864, 28430, 46523, 81645, 8604, 55030, 74222, 12744, 11441, 43095, 77734, 50297, 14881, 65042, 24183, 83604, 58898, 49539, 36020, 29984, 46376, 65099, 5150, 78279, 4369, 31856, 6274, 50717, 18278, 51525, 4549, 5293, 13165, 80587, 74478, 61344, 48190, 43636, 16874, 38971, 303, 49355, 67762, 67082, 41411, 54380, 76448, 83312, 60147, 11712, 9434, 3922, 61476, 10218, 43532, 39316, 82044, 70788, 54436, 45504, 63752, 27220, 17896, 71997, 54138, 58149, 78272, 12644, 18179, 67446, 49708, 57693, 63170, 54876, 25891, 10872, 48108, 67835, 83638, 37513, 13064, 67300, 29395, 51543, 24614, 28064, 6060, 70577, 19155, 66654, 81851, 80649, 63431, 34090, 63158, 15138, 21321, 47242, 48671, 42236, 35110, 22043, 42531, 5933, 44977, 1567, 54846, 45227, 12172, 70706, 66866, 13998, 68128, 3906, 18383, 37114, 81449, 74455, 5954, 34361, 51840, 1706, 16693, 24229, 14047, 28683, 39988, 66907, 2338, 45608, 50854, 6320, 9999, 29708, 56512, 52189, 71807, 51870, 13566, 10230, 90, 26306, 59910, 78887, 62152, 15295, 43923, 75933, 25821, 4084, 70831, 17723, 45213, 48391, 32810, 30131, 67976, 70229, 71520, 73327, 19306, 63322, 65903, 7696, 44304, 55891, 56105, 54502, 47574, 36148, 79341, 23756, 7487, 40660, 52375, 16406, 1172, 28742, 42773, 84985, 44148, 66918, 21608, 49723, 43492, 17130, 20569, 39414, 42695, 2728, 46977, 31380, 15317, 65646, 9048, 909, 60766, 62001, 17937, 27113, 22966, 35963, 85870, 45827, 80980, 69461, 66245, 32449, 27882, 7217, 36108, 8811, 66709, 34289, 37196, 3167, 36356, 14337, 72830, 76625, 3129, 57854, 50515, 68265, 50871, 14279, 40291, 20076, 40819, 65834, 62807, 84768, 3885, 32142, 7414, 60981, 57963, 84176, 68602, 60854, 67091, 23611, 83286, 62310, 55663, 18899, 12158, 22107, 79320, 55159, 75557, 72372, 53671, 18081, 11455, 59259, 18978, 61044, 39291, 19482, 39609, 18929, 38962, 76920, 82398, 40949, 82029, 83481, 31308, 73560, 44613, 47123, 32514, 48832, 76706, 31301, 22846, 6163, 53387, 79819, 51726, 39640, 48145, 76697, 13631, 60023, 43894, 21912, 71671, 79412, 25229, 13908, 62397, 39830, 50207, 12320, 19994, 35860, 7266, 59870, 69583, 47861, 82297, 81813, 37690, 52940, 48230, 61703, 16340, 74152, 10241, 32040, 82537, 83717, 8604, 49593, 1946, 2022, 2840, 52510, 82360, 68934, 57217, 80154, 74239, 60650, 35034, 30784, 85490, 42298, 64875, 8289, 59017, 9567, 28665, 79002, 16323, 30701, 58292, 71503, 73817, 25764, 30201, 79953, 9023, 22253, 19774, 23458, 7117, 62050, 2823, 42592, 5603, 72853, 32732, 57811, 7853, 59957, 73541, 9166, 8772, 48385, 39114, 29830, 28898, 26799, 71559, 5419, 45279, 56862, 6244, 40815, 19595, 13032, 65586, 43756, 27131, 57361, 7168, 5696, 69073, 66777, 46558, 37443, 63250, 25632, 25022, 5322, 21284, 79306, 48732, 46615, 66200, 49262, 78775, 16051, 10060, 60330, 20759, 29191, 59073, 11057, 21127, 52249, 81453, 29177, 40079, 17834, 17551, 37034, 14344, 16160, 34386, 76075, 49704, 53788, 73599, 73786, 74242, 74299, 47002, 74920, 82546, 22619, 19422, 8588, 7192, 63668, 76324, 49689, 10993, 73947, 51344, 81624, 44252, 17719, 47530, 1595, 73998, 12521, 67835, 32837, 23629, 84682, 54453, 79671, 39970, 59473, 56622, 3269, 4809, 10537, 7844, 13993, 21296, 24260, 80912, 15905, 78038, 10260, 84514, 76319, 36773, 19451, 54689, 72630, 66502, 58923, 25986, 79648, 42618, 28068, 21440, 8278, 6295, 37986, 31873, 31787, 79309, 74118, 61538, 46782, 23743, 80196, 80170, 8081, 49162, 51248, 78399, 72721, 8630, 6399, 69493, 65499, 33786, 3903, 34351, 82116, 13919, 82554, 61669, 60220, 20773, 61080, 52696, 11112, 60405, 55173, 54334, 2755, 38619, 715, 36380, 53171, 63473, 69291, 83589, 10330, 78328, 4361, 16006, 27497, 75074, 34811, 59623, 16649, 49141, 39330, 355, 61617, 10971, 48949, 11084, 53284, 36015, 11511, 74715, 11427, 71869, 84773, 25773, 46941, 35214, 81523, 48777, 24800, 20080, 46394, 17525, 51780, 7558, 61467, 78809, 51023, 65912, 29781, 42639, 40486, 1749, 77178, 58358, 59453, 23813, 19182, 40279, 30214, 31756, 52874, 24392, 80371, 63859, 41095, 22974, 51535, 4982, 34981, 29551, 39046, 30184, 22531, 75229, 37032, 51946, 36437, 70211, 56682, 69793, 38418, 11875, 49951, 51751, 78490, 53798, 55480, 50926, 35580, 5551, 51284, 16664, 25297, 53453, 46152, 55419, 67465, 14790, 19017, 36793, 34501, 5263, 85555, 73353, 13657, 79146, 63062, 38783, 2334, 78414, 39365, 41387, 14334, 26114, 10150, 71849, 59712, 66386, 46722, 62888, 79317, 21031, 49706, 71383, 25067, 45089, 11047, 12106, 4450, 5500, 77646, 27148, 3947, 8931, 9557, 10920, 24811, 5501, 55690, 69467, 52481, 67862, 15561, 54797, 85619, 20876, 68802, 61753, 65353, 60994, 52129, 4437, 867, 36305, 50428, 11923, 35212, 18218, 50695, 36932, 6515, 67312, 50254, 22259, 17484, 9775, 41409, 78541, 20103, 30443, 33291, 22424, 26789, 1559, 77268, 74438, 50771, 73184, 45785, 3122, 77909, 29895, 35564, 85772, 4397, 31934, 85222, 10701, 4672, 70017, 12301, 49471, 74408, 23011, 6643, 63620, 64076, 33979, 85052, 55165, 46018, 75177, 49958, 56769, 41343, 1193, 52804, 57047, 16872, 38283, 17371, 48004, 78497, 23679, 42220, 15259, 56285, 55135, 60194, 80271, 9955, 83738, 60934, 73004, 78677, 65310, 60260, 74988, 55412, 7548, 48475, 15642, 54515, 81698, 28807, 66573, 54093, 58070, 4875, 15530, 45260, 41817, 6538, 81744, 18633, 77728, 39146, 25941, 74899, 75588, 67645, 63030, 30632, 7506, 73656, 4473, 54206, 64846, 79633, 69519, 32924, 55526, 61914, 33501, 49708, 40563, 12473, 83590, 7351, 33437, 22154, 9159, 17774, 41537, 35916, 40670, 31005, 26563, 81665, 29937, 8192, 6828, 37258, 85067, 79356, 55663, 37779, 37594, 3985, 32117, 83073, 48777, 21284, 68885, 36369, 39348, 59642, 16498, 48458, 56827, 35891, 30744, 15292, 48410, 68348, 73492, 38396, 69665, 31617, 16960, 73029, 41484, 57824, 15437, 17074, 25751, 5291, 83157, 52434, 39664, 79187, 32204, 35700, 81045, 23285, 33450, 18714, 84152, 78676, 46152, 65997, 36623, 18573, 30475, 30373, 24377, 14009, 27496, 30227, 30768, 46101, 83976, 34124, 21424, 77584, 84180, 54615, 31212, 2338, 23476, 4067, 856, 14632, 56983, 38020, 12672, 27670, 17716, 78115, 28440, 48800, 25609, 187, 75612, 7643, 63832, 2444, 79674, 12934, 7767, 17789, 42958, 65553, 23377, 77548, 22831, 47176, 1066, 23299, 80284, 9709, 84107, 13375, 43666, 29192, 55690, 71345, 8368, 5348, 53970, 57621, 19541, 38356, 46324, 73136, 47315, 46257, 72478, 62236, 66724, 62140, 37896, 67432, 52257, 42160, 66197, 46340]

#import random
#for x in range(1000):
#    # generovanie random userov pre potreby testovania
#    if x not in users:
#        users.append(random.randint(1,86016))
#print(users)

presnost = 0
recall = 0
zoznam = load_from_file("big_zoznam.txt")
catalog = load_from_file("catalog.txt")
cn = 1
for u in users50:
    user = str(u)

    recommended = get1(user,zoznam) # odporuc predmety
    if recommended == None:
        continue

    future = getfuture(user,recommended[1],zoznam,10)   # ziskaj nasledujuce eventy pre porovnanie/vyhodnotenie
    recommended = unique(list(recommended[0]))

    vysledok = vyhodnot(recommended,future,catalog)     # vyhodnot uspesnost

    presnost += vysledok[0]
    recall += vysledok[1]
    print(cn)
    print("Presnost:", presnost / cn)
    print("Recall:", recall / cn)
    print("\n\n")
    cn += 1

print("Test Done!")

