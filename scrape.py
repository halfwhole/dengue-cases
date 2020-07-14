from bs4 import BeautifulSoup
import difflib
import json
import requests


MAP_URL = 'https://www.nea.gov.sg/api/OneMap/GetMapData/DENGUE_CLUSTER'
INFO_URL = 'https://www.nea.gov.sg/dengue-zika/dengue/dengue-clusters'
OUTPUT_JSON_FILE_FORMAT = 'data-%s.json'
OUTPUT_JSON_LATEST_FILE = 'data-latest.json'


def get_map_clusters_date():
    page = requests.get(MAP_URL)
    data = json.loads(json.loads(page.text))
    data = data['SrchResults']
    metadata = data[0]
    clusters = data[1:]
    date = metadata['DateTime']['date'].split(' ')[0]
    return clusters, date


## RANT: I'd initially wanted to scrape both data sources (map & info table), then put the two together to get a more complete dataset.
##       But as it turns out, the two data sources don't line up at all. They're independent of each other, and updated separately.
##       The numbers aren't the same, the case counts are off, and even the cluster names are different. The map's also broken.
##       Shame on you, NEA. >:(

# def get_info_dict():
#     ## Split rows based on 'hashlink' class
#     ## ['hashlink'. 'A', 'B', 'hashlink', 'C', 'hashlink', 'D', 'E', 'F'] ==> ['A', 'B'], ['C'], ['D', 'E', 'F']
#     def split_rows(rows):
#         groups = []
#         current_group = []
#         for row in rows:
#             if 'hashlink' in row.get('class'):
#                 if current_group: groups.append(current_group)
#                 current_group = []
#             else:
#                 current_group.append(row)
#         groups.append(current_group)
#         return groups
#
#     def format_group(group):
#         alert_color        = group[0].findAll('td')[1].find('div').get('class')[0]
#         description        = group[0].findAll('td')[2].text
#         cases_last_2_weeks = int(group[0].findAll('td')[3].text)
#         cases_since_start  = int(group[0].findAll('td')[4].text)
#         breakdown = [{'location': entry.findAll('td')[-2].text, 'cases': int(entry.findAll('td')[-1].text)} for entry in group]
#         formatted_group = {
#             'alert_color': alert_color,
#             'cases_last_2_weeks': cases_last_2_weeks,
#             'cases_since_start': cases_since_start,
#             'breakdown': breakdown
#         }
#         return description, formatted_group
#
#     page = requests.get(INFO_URL)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     table = soup.findAll('table')[-1]  # Get the last table
#     rows = [row for row in table.findAll('tr') if row.get('class') is not None] # Filter out the first 2 non-data rows, which have no 'class' attribute
#     groups = split_rows(rows)
#     formatted_groups = [format_group(group) for group in groups]
#     info_dict = dict(formatted_groups)
#     return info_dict


def format_geojson(clusters):
    # def get_matching_info_for_cluster(description, info_dict):
    #     info_dict_keys = info_dict.keys()
    #     matches = difflib.get_close_matches(description, info_dict.keys(), n=1)
    #     if len(matches) == 0:
    #         print('Could not find a match for cluster %s' % description)
    #         return {}
    #     info = info_dict[matches[0]]
    #     return info

    def format_cluster(cluster):
        description = cluster['DESCRIPTION']
        coordinates = [[float(coord) for coord in latlng.split(',')][::-1] for latlng in cluster['LatLng'].split('|')]
        # info = get_matching_info_for_cluster(description, info_dict)
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [coordinates]
            },
            'properties': {
                'description': description,
                'case_size': int(cluster['CASE_SIZE']),
                'homes': cluster.get('HOMES', None),
                'public_places': cluster.get('PUBLIC_PLACES', None),
                'construction_sites': cluster.get('CONSTRUCTION_SITES', None),
                # 'cases_last_2_weeks': info.get('cases_last_2_weeks', None),
                # 'cases_since_start': info.get('cases_since_start', None),
                # 'breakdown': info.get('breakdown', None),
            }
        }

    features = [format_cluster(cluster) for cluster in clusters]
    geojson = {'type': 'FeatureCollection', 'features': features}
    return geojson


if __name__ == '__main__':
    clusters, date = get_map_clusters_date()
    # info_dict = get_info_dict()
    geojson = format_geojson(clusters)
    json.dump(geojson, open(OUTPUT_JSON_FILE_FORMAT % date, 'w'))
    json.dump(geojson, open(OUTPUT_JSON_LATEST_FILE, 'w'))
