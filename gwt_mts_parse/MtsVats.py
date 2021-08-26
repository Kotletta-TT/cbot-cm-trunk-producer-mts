import asyncio
import logging
import re
import string

import aiohttp

from gwt_mts_parse.long_string_requests import TRUNKS_LIST_PAYLOAD, \
    TRUNK_INFO_PAYLOAD, TRUNK_ADD_SIP, TRUNK_DESTROY_SIP


class VATS:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(threadName)s %(message)s")

    def __init__(self, address, user, password, contract_url_abonents) -> None:
        self.unique_payloads_links = []
        self.dirt_trunks = []
        self.trunk_json = {}
        self.address = address
        self.user = user
        self.contract_url_abonents = contract_url_abonents
        self.pagination = self.calc_pagination(301)
        self.password = password
        self.part_auth_url = 'j_spring_security_check'
        self.base_api_url = f'https://{address}/vpbxGwt/'
        self.trunk_codes = ''

    def calc_pagination(self, count_sim):
        alphabet = string.ascii_uppercase
        return alphabet[0: count_sim // 100 + 1]

    async def get_x_gwt_permutation(self):
        url = f'{self.base_api_url}vpbxGwt.nocache.js'
        raw_data = await self.query(method='GET', url=url)
        return re.search(r"bc='(\w{32})'", raw_data).group(1)

    async def get_trunk_codes(self, x_gwt_permutation):
        trunk_codes = {}
        url = f'{self.base_api_url}{x_gwt_permutation}.cache.js'
        raw_data = await self.query(method='GET', url=url)
        trunk_codes['trunk_info_code'] = re.search(r"'DispatcherGwtService','(\w{32})", raw_data).group(1)
        trunk_codes['trunk_list_code'] = re.search(r"'AbonentBrowserGwtService','(\w{32})", raw_data).group(1)
        return trunk_codes

    async def get_login(self):
        conn = aiohttp.TCPConnector(limit=1)
        self.session = aiohttp.ClientSession(connector=conn)
        url = f'https://{self.address}/{self.part_auth_url}'
        data = aiohttp.FormData()
        data.add_fields(['j_username', self.user],
                        ['j_password', self.password])
        await self.query(url=url, payload=data)
        x_gwt_permutation = await self.get_x_gwt_permutation()
        self.trunk_codes = await self.get_trunk_codes(x_gwt_permutation)
        self.headers = {'X-GWT-Module-Base': self.base_api_url,
                        'X-GWT-Permutation': x_gwt_permutation,
                        'Content-Type': 'text/x-gwt-rpc; charset=UTF-8'}

    async def get_list_trunks(self, page):
        contract_inner_link = f'|-2|7|0|8|{self.contract_url_abonents}|0|0|8|{page}|8|Bk|0|'
        url = f'{self.base_api_url}AbonentBrowserGwtService'
        payload = TRUNKS_LIST_PAYLOAD.format(trunk_list_code=self.trunk_codes['trunk_list_code'], contract=contract_inner_link)
        response = await self.query(url=url, payload=payload,
                                    headers=self.headers)
        online_trunks = set(re.findall(r"C.{5}',2,0,0",
                                       response))  # '2,0,0,\d,8,\d,\d,0,\d,0,0,0'
        links_trunks = [link.split("'")[0] for link in online_trunks]
        for link in links_trunks:
            self.unique_payloads_links.append(link)
        self.unique_payloads_links = list(set(self.unique_payloads_links))

    async def get_trunk(self, link):
        url = f'{self.base_api_url}DispatcherGwtService'
        payload = TRUNK_INFO_PAYLOAD.format(trunk_info_code=self.trunk_codes['trunk_info_code'], link=link, num_func='31')
        response = await self.query(url=url, payload=payload,
                                    headers=self.headers)
        if '//OK' in response:
            logging.debug(f'Correct response to: {link}')
            trunk = self.parse_dirt_trunk(response)
            trunk['inner_name'] = link
            self.trunk_json[trunk['trunk_phone']] = trunk['value']
        if '//EX' in response:
            logging.warning(f'Error response to: {link}')

    async def query(self, url, payload=None, headers=None, method='POST'):
        if headers and payload:
            response = await self.session.request(method=method, url=url,
                                                  data=payload,
                                                  headers=headers, ssl=True)
        elif headers and not payload:
            response = await self.session.request(method=method, url=url,
                                                  headers=headers, ssl=True)
        elif payload and not headers:
            response = await self.session.request(method=method, url=url,
                                                  data=payload, ssl=True)
        else:
            response = await self.session.request(method=method, url=url,
                                                                ssl=True)
        if response.status == 200:
            text = await response.text()
            if '//EX' in text:
                logging.warning(f'Incorrect response: {payload}')
            return text
        else:
            logging.warning(
                f'Connection ERROR! Status code: {response.status}')

    async def close_session(self):
        await self.session.close()

    def parse_dirt_trunk(self, dirt_trunk):
        trunk_dict = {}
        trunk = re.search(
            r'(sip_\d+_\w+\",\")((?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%\^&\\{}\[\]()_\-~?+]).{8,16})',
            dirt_trunk)
        trunk_device = re.search(r'(Ca.{4})..(\d.\d)..(Ca.{4})', dirt_trunk)
        trunk_sip_device = True if '4' in trunk_device.group(2) else False
        trunk_sip_enabled = True if '4,1' in trunk_device.group(2) else False
        trunk_inner_link = trunk_device.group(3)
        trunk_sip_obj = trunk_device.group(1)
        trunk_identify_line = re.search(r'"(mobsip_\d{10})"',
                                        dirt_trunk).group(1)
        if trunk:
            trunk_phone = '7' + trunk.group(1).split('_')[1]
            trunk_login = trunk.group(1).split('"')[0]
            trunk_password = bytes(trunk.group(2).split('"')[0],
                                   'utf-8').decode('unicode_escape')

            trunk_dict = {'trunk_phone': trunk_phone,
                          'value': {
                              'trunk_login': trunk_login,
                              'trunk_password': trunk_password,
                              'trunk_sip_device': trunk_sip_device,
                              'trunk_sip_enabled': trunk_sip_enabled,
                              'trunk_identify_line': trunk_identify_line,
                              'trunk_sip_obj': trunk_sip_obj,
                              'trunk_inner_link': trunk_inner_link}}
        return trunk_dict

    def get_trunks(self):
        loop = asyncio.get_event_loop()
        login = loop.create_task(self.get_login())
        loop.run_until_complete(asyncio.gather(login))
        if len(self.pagination) > 1:
            pages = [loop.create_task(self.get_list_trunks(page)) for page in
                     self.pagination]
            loop.run_until_complete(asyncio.gather(*pages))
        else:
            loop.run_until_complete(self.get_list_trunks(self.pagination[0]))
        coros = [loop.create_task(self.get_trunk(link)) for link in
                 self.unique_payloads_links]
        loop.run_until_complete(asyncio.gather(*coros))
        loop.run_until_complete(self.close_session())

        return self.trunk_json

    def trunk_list_action(self, sim_list, action):
        query_list = []
        all_trunks = self.get_trunks()
        url = f'{self.base_api_url}DispatcherGwtService'
        loop = asyncio.get_event_loop()
        login = loop.create_task(self.get_login())
        loop.run_until_complete(asyncio.gather(login))
        for num in sim_list:
            str_num = str(num)
            if str_num in all_trunks:
                trunk = all_trunks[str_num]
                if action == 'add':
                    payload = TRUNK_ADD_SIP.format(
                        trunk_info_code=self.trunk_codes['trunk_info_code'],
                        identify_line=trunk['trunk_identify_line'],
                        inner_link=trunk['trunk_inner_link'],
                        sip_obj=trunk['trunk_sip_obj'],
                        contract_link=self.contract_url_abonents)
                if action == 'del':
                    payload = TRUNK_DESTROY_SIP.format(
                        trunk_info_code=self.trunk_codes['trunk_info_code'],
                        trunk_inner_link=trunk['trunk_inner_link'])
                query_list.append(loop.create_task(
                    self.query(url=url, payload=payload,
                               headers=self.headers)))
        loop.run_until_complete(asyncio.gather(*query_list))
        loop.run_until_complete(self.close_session())
