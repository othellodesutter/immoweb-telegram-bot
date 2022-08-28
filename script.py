import requests
import json
import time
import random
from config import config

class ImmowebScraper:
    def __init__(self, url):
        self.url = url
        self.last_result = ''
        self.last_results = []

    def get_source_from_url(self):
        source = str(requests.get(self.url).text)
        return source

    def get_results_from_source(self, source):
        json_data = json.loads(source)
        results = json_data['results']
        return results

# (TO DO) DONE: api search results do not refresh one by one, but some properties at once - make list of last result ids en check every result of new results if id is in last_result list
    def update(self):
        results = self.get_results_from_source(self.get_source_from_url())
        # check if the current newest result is the same as the last result
        for result in results:
            if result['id'] not in self.last_results:
                # wipe whole list if new result is found (otherwise the list will grow indefinitely)
                try:
                    self.last_results.append(result['id'])
                    #self.last_result = result['id']
                    # make it balances - now it give {'ok': False, 'error_code': 429, 'description': 'Too Many Requests: retry after 41', 'parameters': {'retry_after': 41}} if a lot of properties are send at same time 
                    self.notify(result)
                    time.sleep(60)
                except Exception as e:
                    print(e)
                    pass

        '''
        if results[0]['id'] != self.last_result:
            self.last_result = results[0]['id']
            try:
                self.notify(results[0])
            except Exception as e:
                print(e)
                pass
        '''
        # random sleep time in between refreshes
        random_time = random.randint(40,60)
        time.sleep(random_time)

    def notify(self, result):
        message = self.get_title(result) + self.get_address(result) + self.get_bedroomCount(result) + self.get_netHabitableSurface(result) + self.get_price(result) + ' \([Immoweb](https://www.immoweb.be/en/classified/' + str(result['id'])+ ')\)'
        if self.get_picture(result) != 'error':
            # if multiple pictures are avalable, send them as a a media group followed by the message
            try:
                media = json.dumps(self.get_pictures(result))
                if media == '[]':
                    raise
                print('------------------------------------------------------')
                print(media)
                print('------------------------------------------------------')
                response = requests.post(
                    url='https://api.telegram.org/bot{0}/sendMediaGroup'.format(token),
                    data={'chat_id': chat_id, 'media': media},
                ).json()
                print(response)
                response = requests.post(
                    url='https://api.telegram.org/bot{0}/sendMessage'.format(token),
                    data={'chat_id': chat_id, 'text': message, 'parse_mode': 'MarkdownV2', 'disable_web_page_preview': 'true'},
                ).json()
                print(response)
        
            # if only one picture is available, send it as a photo with the message as a caption
            except:
                response = requests.post(
                    url='https://api.telegram.org/bot{0}/sendPhoto'.format(token),
                    data={'chat_id': chat_id, 'photo': self.get_picture(result), 'caption': message, 'parse_mode': 'MarkdownV2'}
                ).json()
                print(response)
        
        # if no picture is available, send the message as a text message
        else:
            response = requests.post(
                url='https://api.telegram.org/bot{0}/sendMessage'.format(token),
                data={'chat_id': chat_id, 'text': message, 'parse_mode': 'MarkdownV2', 'disable_web_page_preview': 'true'},
            ).json()
            print(response)

# ------------------------------------- GETTERS --------------------------------------------------------------------------------------------------

    def get_title(self, result):
        try:
            property_type = str(result['property']['type'])
            transaction_type = self.get_transaction_type(result)
            return property_type + transaction_type + 'in ' + self.get_locality(result)
        except:
            return 'error'

    def get_transaction_type(self, result):
        try:
            transaction_type = str(result['transaction']['type'])
            if transaction_type == 'FOR_RENT':
                return ' for rent '
            elif transaction_type == 'FOR_SALE':
                return ' for sale '
            else:
                return ' '
        except:
            return 'error'

    # "Bad Request: can't parse entities: Character '-' is reserved and must be escaped with the preceding '\\'"} --> some localities have special character (eg.'-') in their name that have to be escaped
    def get_locality(self, result):
        try:
            locality = str(result['property']['location']['locality'])
            locality = locality.replace('-','\\-').replace('(','\\(').replace(')','\\)')
            return locality
        except:
            return 'error'


    def get_address(self, result):
        try:
            street = str(result['property']['location']['street'])
            number = str(result['property']['location']['number'])
            # "Bad Request: can't parse entities: Character '-' is reserved and must be escaped with the preceding '\\'"} --> to avoid problems with special characters in the address, we have to escape them
            street = street.replace('-','\\-').replace('(','\\(').replace(')','\\)')
            number = number.replace('-','\\-').replace('(','\\(').replace(')','\\)')
            if street != ('None' or 'null') and number != ('None' or 'null'):
                return ' \([' + street + ' ' + number + '](https://www.google.be/maps/place/' + street + ' ' + number + ' ' + self.get_locality(result) + ')\)\.'
            elif street != ('None' or 'null') and number != 'None':
                return ' \([' + street + ' ' + number + '](https://www.google.be/maps/place/' + street + ' ' + self.get_locality(result) + ')\)\.'
            else:
                return '\.'
        except:
            return 'error'
    
    def get_bedroomCount(self, result):
        try:
            bedroomCount = str(result['property']['bedroomCount'])
            if bedroomCount != 'None':
                if bedroomCount == '1':
                    return ' 1 bedroom\.'
                else:
                    return ' ' + bedroomCount + ' bedrooms\.'
            else:
                return ''
        except:
            return 'error'

    def get_netHabitableSurface(self, result):
        try:
            netHabitableSurface = str(result['property']['netHabitableSurface'])
            if netHabitableSurface != 'None':
                return ' ' + netHabitableSurface + ' m²\.'
            else:
                return ''
        except:
            return 'error'

    def get_price(self, result):
        try:
            price = str(result['price']['mainValue'])
            if self.get_transaction_type(result) == ' for rent ':
                return ' ' + price + ' euro per month\.'
            else:
                return ' ' + price + ' euro\.'
        except:
            return ''

    def get_picture(self, result):
        try:
            picture_url = str(result['media']['pictures'][0]['largeUrl'])
            if picture_url != 'None':
                return picture_url
            else:
                return 'error'
        except:
            return 'error'

    def get_pictures(self, result):
        pictures = []
        try:
            picture_url = str(result['media']['pictures'][0]['largeUrl'])
            picture_url = picture_url.split('_1.')[0]
            for i in range (1, 10):
                try:
                    # check if picture is not the same as the picture before (now sometimes it send media group with 10 same photos)
                    response = requests.get(picture_url + '_' + str(i) + '.jpg')
                    if response.status_code == 200:
                        photo = dict(type='photo', media=picture_url + '_' + str(i) + '.jpg')
                        pictures.append(photo)
                    else:
                        break
                except:
                    pass

        except:
            return 'error'
        return pictures






if __name__ == '__main__':
    token = config['token']
    chat_id = config['chat_id']
    url = config['url']

    scraper = ImmowebScraper(url)
    #scraper.last_result = scraper.get_results_from_source(scraper.get_source_from_url())[0]['id']
    for result in scraper.get_results_from_source(scraper.get_source_from_url()):
        scraper.last_results.append(result['id'])
    while True:
        scraper.update()