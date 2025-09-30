from parsers.place_parser import PlaceParser

# sample_queries = [
#         "small business Bergen County NJ",
#         "local business Bergen County NJ",
#         "shop Bergen County NJ",
#         "store Bergen County NJ",
#         "retail Bergen County NJ",
#         "boutique Bergen County NJ",
#         "artisan Bergen County NJ",
#         "handmade Bergen County NJ",
#         "crafts Bergen County NJ",
#         "gift shop Bergen County NJ",
#         "bakery Bergen County NJ",
#         "cafe Bergen County NJ",
#         "restaurant Bergen County NJ",
#         "florist Bergen County NJ",
#         "jewelry Bergen County NJ",
#         "home decor Bergen County NJ",
#         "toy store Bergen County NJ",
#         "stationery Bergen County NJ",
#         "beauty salon Bergen County NJ",
#         "barber shop Bergen County NJ",
#         "fitness studio Bergen County NJ",
#         "gallery Bergen County NJ",
#         "thrift store Bergen County NJ",
#         "clothing store Bergen County NJ",
#         "market Bergen County NJ",
#     ]

p = PlaceParser()
p.search("gift shop Bergen County NJ")
places = list(p.places.values())
print(places[0])