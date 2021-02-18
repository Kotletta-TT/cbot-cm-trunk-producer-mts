import re
import aiohttp
import asyncio
import string


class VATS:

    def __init__(self, address, user, password, x_gwt_permutation, contract_url_abonents, count_sim) -> None:
        self.unique_payloads_links = []
        self.dirt_trunks = []
        self.list_trunks = []
        self.address = address
        self.user = user
        self.contract_url_abonents = contract_url_abonents
        self.pagination = self.calc_pagination(count_sim)
        self.password = password
        self.part_auth_url = 'j_spring_security_check'
        self.base_api_url = f'https://{address}/vpbxGwt/'
        self.headers = {'X-GWT-Module-Base': self.base_api_url,
                        'X-GWT-Permutation': x_gwt_permutation,
                        'Content-Type': 'text/x-gwt-rpc; charset=UTF-8'}

    def calc_pagination(self, count_sim):
        alphabet = string.ascii_uppercase
        return alphabet[0: count_sim // 100 + 1]

    async def get_login(self):
        self.session = aiohttp.ClientSession()
        url = f'https://{self.address}/{self.part_auth_url}'
        data = aiohttp.FormData()
        data.add_fields(['j_username', self.user], ['j_password', self.password])
        await self.query(url=url, payload=data)

    async def get_list_trunks(self, page):
        contract_inner_link = f'|-2|7|0|8|{self.contract_url_abonents}|0|0|8|{page}|8|Bk|0|'
        url = f'{self.base_api_url}AbonentBrowserGwtService'
        payload = f'7|0|8|https://vpbx.mts.ru/vpbxGwt/|3D7E196DA92A574D98BAC0DEE7D909C8|ru.cti.vpbx.shared.services.AbonentBrowserGwtService|list|ru.cti.vpbx.shared.models.browser.AbonentBrowserRequestGWTModel/3482149540|java.lang.Boolean/476441737|ru.cti.vpbx.shared.enums.MIGRATION_STATE_TYPE/1556569729|java.lang.Long/4227064769|1|2|3|4|1|5|5|0|6|0|0{contract_inner_link}'
        response = await self.query(url=url, payload=payload, headers=self.headers)
        online_trunks = set(re.findall(r"Ca.{4}',2,0,0,\d,8,\d,\d,0,\d,0,0,0", response))
        links_trunks = [link.split("'")[0] for link in online_trunks]
        for link in links_trunks:
            self.unique_payloads_links.append(link)
        self.unique_payloads_links = list(set(self.unique_payloads_links))

    async def get_trunk(self, link):
        url = f'{self.base_api_url}DispatcherGwtService'
        abonent_payload = '7|0|6|https://vpbx.mts.ru/vpbxGwt/|EAA49B7B1A97DFBDC367A2E2573FB3B7|ru.cti.vpbx.shared.services.DispatcherService|getForm|java.lang.Long/4227064769|ru.cti.vpbx.shared.services.DispatcherService$DISPATCHER/4095484021|1|2|3|4|2|5|6|5|{link}|6|{num_func}|'
        payload = abonent_payload.format(link=link, num_func='31')
        response = await self.query(url=url, payload=payload, headers=self.headers)
        if '//OK' in response:
            trunk = self.parse_dirt_trunk(response)
            trunk['inner_name'] = link
            self.list_trunks.append(trunk)
        if '//EX' in response:
            payload = abonent_payload.format(link=link, num_func='32')
            response = await self.query(url=url, payload=payload, headers=self.headers)
            trunk = self.parse_another_dirt_trunk(response)
            self.list_trunks.append(trunk)

    async def query(self, url, payload, headers=None):
        if headers == self.headers:
            response = await self.session.request(method='POST', url=url, data=payload, headers=headers, ssl=False)
        else:
            response = await self.session.request(method='POST', url=url, data=payload, ssl=False)
        if response.status == 200:
            return await response.text()
        else:
            return await response.text()
            # raise ConnectionError

    async def close_session(self):
        await self.session.close()

    def parse_another_dirt_trunk(self, dirt_trunk):
        trunk_dict = {}
        print(dirt_trunk)
        trunk_login = re.search(r"sip_\d+_\w+", dirt_trunk)
        if trunk_login:
            trunk_password = re.search(r"(?<=pov.vpbx.mts.ru.{9})[A-Za-z0-9!@#$%\^&\\{}\[\]()_\-~?]+", dirt_trunk)
            trunk_phone = re.search(r"(?<=BLOCKED_CODE.{13})\d*", dirt_trunk)
            trunk_dict = {'trunk_login': trunk_login.group(),
                          'trunk_password': trunk_password.group(),
                          'trunk_phone': trunk_phone.group()}
            return trunk_dict

    def parse_dirt_trunk(self, dirt_trunk):
        trunk_dict = {}
        trunk = re.search(
            r'(sip_\d+_\w+\",\")((?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%\^&\\{}\[\]()_\-~?+]).{8,16})',
            dirt_trunk)
        trunk_device = re.search(r'Ca.{4}..(\d.\d)..Ca.{4}', dirt_trunk).group(1)
        trunk_sip_device = True if '4' in trunk_device else False
        trunk_sip_enabled = True if '4,1' in trunk_device else False
        trunk_identify_line = re.search(r'"(mobsip_\d{10})"', dirt_trunk).group(1)
        if trunk:
            trunk_phone = trunk.group(1).split('_')[1]
            trunk_login = trunk.group(1).split('"')[0]
            trunk_password = bytes(trunk.group(2).split('"')[0], 'utf-8').decode('unicode_escape')
            trunk_dict = {'trunk_login': trunk_login,
                          'trunk_password': trunk_password,
                          'trunk_phone': trunk_phone,
                          'trunk_sip_device': trunk_sip_device,
                          'trunk_sip_enabled': trunk_sip_enabled,
                          'trunk_identify_line': trunk_identify_line}
        return trunk_dict

    def get_trunks(self):
        loop = asyncio.get_event_loop()
        login = loop.create_task(self.get_login())
        loop.run_until_complete(asyncio.gather(login))
        if len(self.pagination) > 1:
            pages = [loop.create_task(self.get_list_trunks(page)) for page in self.pagination]
            loop.run_until_complete(asyncio.gather(*pages))
        else:
            loop.run_until_complete(self.get_list_trunks(self.pagination[0]))
        coros = [loop.create_task(self.get_trunk(link)) for link in self.unique_payloads_links]
        loop.run_until_complete(asyncio.gather(*coros))
        loop.run_until_complete(self.close_session())

        return self.list_trunks

    def trunk_add_device(self, number=None, *args):
        all_trunks = self.get_trunks()
        url = f'{self.base_api_url}DispatcherGwtService'
        loop = asyncio.get_event_loop()
        login = loop.create_task(self.get_login())
        loop.run_until_complete(asyncio.gather(login))
        if number:
            for trunk in all_trunks:
                if trunk['trunk_phone'] == number:
                    payload = '7|0|14|https://vpbx.mts.ru/vpbxGwt/|EAA49B7B1A97DFBDC367A2E2573FB3B7|ru.cti.vpbx.shared.services.DispatcherService|updateForm|ru.cti.vpbx.shared.models.codebase.RecordGWTModel/4241958543|ru.cti.vpbx.shared.services.DispatcherService$DISPATCHER/4095484021|ru.cti.vpbx.shared.models.form.device.AbonentDeviceFormGWTModel/591779426|java.util.ArrayList/4159755760|ru.cti.vpbx.shared.models.form.device.AbonentDeviceRecordGWTModel/1158222701|java.lang.Long/4227064769|mobsip_{number}|SIP-phone|java.lang.Integer/3438268394|Generic SIP Phone|1|2|3|4|2|5|6|7|8|1|9|10|{inner_name}|1|10|CaZQKc|10|CaTEZB|11|0|0|12|0|0|0|13|1|1|14|0|8|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|-4|6|31|'.format(
                        number=number, inner_name=trunk['inner_name'])
                    query = loop.create_task(self.query(url, payload, self.headers))
                    loop.run_until_complete(asyncio.gather(query))

        if type(args) == list and len(args) > 0:
            query_list = []
            for num in args:
                for trunk in all_trunks:
                    if str(num) == trunk['trunk_phone']:
                        payload = '7|0|14|https://vpbx.mts.ru/vpbxGwt/|EAA49B7B1A97DFBDC367A2E2573FB3B7|ru.cti.vpbx.shared.services.DispatcherService|updateForm|ru.cti.vpbx.shared.models.codebase.RecordGWTModel/4241958543|ru.cti.vpbx.shared.services.DispatcherService$DISPATCHER/4095484021|ru.cti.vpbx.shared.models.form.device.AbonentDeviceFormGWTModel/591779426|java.util.ArrayList/4159755760|ru.cti.vpbx.shared.models.form.device.AbonentDeviceRecordGWTModel/1158222701|java.lang.Long/4227064769|mobsip_{number}|SIP-phone|java.lang.Integer/3438268394|Generic SIP Phone|1|2|3|4|2|5|6|7|8|1|9|10|{inner_name}|1|10|CaZQKc|10|CaTEZB|11|0|0|12|0|0|0|13|1|1|14|0|8|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|-4|6|31|'.format(
                            number=trunk['trunk_phone'], inner_name=trunk['inner_name'])
                        query_list.append([url, payload])

            queries = [loop.create_task(self.query(url=query[0], payload=query[1], headers=self.headers)) for query in
                       query_list]
            loop.run_until_complete(asyncio.gather(*queries))

        loop.run_until_complete(self.close_session())
