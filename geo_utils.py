from ip2geotools.databases.noncommercial import DbIpCity


def get_details(ip):
    res = DbIpCity.get(ip, api_key="free")
    print(res.country)
    return res.city


print(get_details("20.68.197.52"))
