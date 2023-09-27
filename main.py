# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import json
import csv
from bs4 import BeautifulSoup



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def get_cam_bat_size(path: str):
    headers = {
        'authority': 'business.ee.co.uk',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-GB,en;q=0.9',
        'cache-control': 'max-age=0',
        'if-modified-since': 'Wed, 27 Sep 2023 16:39:02 GMT',
        'if-none-match': '"318c4-60659d4346208-gzip"',
        'referer': 'https://business.ee.co.uk/',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    response = requests.get('https://business.ee.co.uk'+ path, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div with the specified class and get the data-config attribute
    div_element = soup.find('div', class_='component-product-herov2')
    size, cam, bat = '',',',''
    if div_element:
        data_config = div_element['data-config']

        # The data-config attribute contains JSON data, so we need to parse it as JSON
        config_dict = json.loads(data_config)

        # Extract the desired fields
        size = config_dict['characteristics'][0]['title']
        cam = config_dict['characteristics'][1]['title']
        bat = config_dict['characteristics'][2]['title']

    return size, cam, bat



def curl_single_mobile(path: str):
    headers = {
        'authority': 'business.ee.co.uk',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    response = requests.get(
        'https://business.ee.co.uk/content/ee/business/en' + path + '.eeb-details.json',
        headers=headers,
    )
    return response.json()


def get_images_and_colours(colours) -> str:
    # Initialize an empty dictionary to store the extracted information
    extracted_info_images = {}
    extracted_info_hex = {}

    # Iterate through the colours in the JSON data
    for colour_path, colour_data in colours.items():
        colour_name = colour_data["name"]
        image_base_paths = ['https://business.ee.co.uk'+image["base_path"] for image in colour_data["images"]]
        extracted_info_images[colour_name] = ", ".join(image_base_paths)
        extracted_info_hex[colour_name] = colour_data['hexCode']

    # Convert the extracted information to the desired format
    formatted_info_images = "; ".join([f"{colour}: {images}" for colour, images in extracted_info_images.items()])
    formatted_info_hex = "; ".join([f"{colour}: {hex}" for colour, hex in extracted_info_hex.items()])

    # Print the formatted information
    return formatted_info_images, formatted_info_hex



def get_all_mobiles():
    headers = {
        'authority': 'business.ee.co.uk',
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9',
        'referer': 'https://business.ee.co.uk/upgrade/upgrade-your-phone-on-ee/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    response = requests.get(
        'https://business.ee.co.uk/content/ee/business/en/upgrade/upgrade-your-phone-on-ee/jcr:content/root/responsivegrid/filter_copy.filter.common-mobile.json/f:empty.json',
        headers=headers,
    )
    mobiles_list = response.json()
    with open('/Users/kalicharanvemuru/PycharmProjects/EE-scraper/mobile-static.tsv', 'wt') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(['Brand', 'Mobile', 'Capacity', 'Sub-version', 'Description', 'Screen size', 'Camera',
                             'Battery', 'Colours', 'Image URLs', 'Article Id', 'Availability', 'Technology', 'OS'])
        for mobile in mobiles_list:
            brand = mobile['brand']
            handset = mobile['handset_name']
            # colours = ''
            # for colour in mobile['colours']:
            #     colours += f'{colour["key"]}:{colour["value"]},'
            technology = '4G'
            for tech in mobile['network_types']:
                if tech == '5G':
                    technology = '5G'
            mobile_details = curl_single_mobile(mobile['page_path'])
            os = next((detail['value'] for detail in mobile_details['specifications'] if detail['label'] == 'Operating system'), '')
            description = mobile_details['short_description']
            size, camera, battery = get_cam_bat_size(mobile['page_path'])
            image_urls, colours = get_images_and_colours(mobile_details['colours'])
            capacities = []
            availability = ''
            for key, value in mobile_details['stock'].items():
                capacities.append(key)
                availability = next(iter(value.items()))[1]['status_text']
            # first_item_1 = next(iter(mobile_details['stock'].items()))
            # first_item_2 = next(iter(first_item_1.items()))
            # availability = first_item_2['status_text']
            for capacity in capacities:
                tsv_writer.writerow(
                    [brand, handset, capacity, f'{handset} {technology} {capacity}', description, size, camera,
                     battery, colours, image_urls, '', availability, technology, os.lower()])

if __name__ == '__main__':
    get_all_mobiles()


