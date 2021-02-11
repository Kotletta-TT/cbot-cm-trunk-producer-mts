import re
import aiohttp
import asyncio

class VATS:


    def __init__(self, address, user, password, x_gwt_permutation, contract_url_abonents) -> None:
        self.unique_payloads_links = []
        self.dirt_trunks = []
        self.list_trunks = []
        self.address = address
        self.user = user
        self.contract_url_abonents = contract_url_abonents.format(page='A')
        self.password = password
        self.part_auth_url = 'j_spring_security_check'
        self.base_api_url = f'https://{address}/vpbxGwt/'
        self.headers = {'X-GWT-Module-Base': self.base_api_url,
                        'X-GWT-Permutation': x_gwt_permutation,
                        'Content-Type': 'text/x-gwt-rpc; charset=UTF-8'}

    async def get_login(self):
        self.session = aiohttp.ClientSession()
        url = f'https://{self.address}/{self.part_auth_url}'
        data = aiohttp.FormData()
        data.add_fields(['j_username', self.user], ['j_password', self.password])
        await self.query(url=url, payload=data)

    async def get_list_trunks(self):
        url = f'{self.base_api_url}AbonentBrowserGwtService'
        payload = f'7|0|8|https://vpbx.mts.ru/vpbxGwt/|3D7E196DA92A574D98BAC0DEE7D909C8|ru.cti.vpbx.shared.services.AbonentBrowserGwtService|list|ru.cti.vpbx.shared.models.browser.AbonentBrowserRequestGWTModel/3482149540|java.lang.Boolean/476441737|ru.cti.vpbx.shared.enums.MIGRATION_STATE_TYPE/1556569729|java.lang.Long/4227064769|1|2|3|4|1|5|5|0|6|0|0{self.contract_url_abonents}'
        response = await self.query(url=url, payload=payload, headers=self.headers)
        online_trunks = set(re.findall(r"Ca.{4}',2,0,0,\d,8,\d,\d,0,\d,0,0,0", response))
        links_trunks = [link.split("'")[0] for link in online_trunks]
        for link in links_trunks:
            self.unique_payloads_links.append(link)


    async def get_trunk(self, link):
        url = f'{self.base_api_url}DispatcherGwtService'
        abonent_payload = '7|0|6|https://vpbx.mts.ru/vpbxGwt/|EAA49B7B1A97DFBDC367A2E2573FB3B7|ru.cti.vpbx.shared.services.DispatcherService|getForm|java.lang.Long/4227064769|ru.cti.vpbx.shared.services.DispatcherService$DISPATCHER/4095484021|1|2|3|4|2|5|6|5|{link}|6|{num_func}|'
        payload = abonent_payload.format(link=link, num_func='31')
        response = await self.query(url=url, payload=payload, headers=self.headers)
        if '//OK' in response:
            trunk = self.parse_dirt_trunk(response)
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
        trunk_login = re.search(r"sip_\d+_\w+", dirt_trunk) # регулярное выражение - транк с номером по сути это выражение проверяет привязку номера к транку
        if trunk_login:
            trunk_password = re.search(r"(?<=pov.vpbx.mts.ru.{9})[A-Za-z0-9!@#$%\^&\\{}\[\]()_\-~?]+", dirt_trunk)
            trunk_phone = re.search(r"(?<=BLOCKED_CODE.{13})\d*", dirt_trunk)
            trunk_dict = {'trunk_login': trunk_login.group(),
                          'trunk_password': trunk_password.group(),
                          'trunk_phone': trunk_phone.group()}
            return trunk_dict
            
    def parse_dirt_trunk(self, dirt_trunk):
        trunk_dict = {}
        trunk = re.search(r'(sip_\d+_\w+\",\")((?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%\^&\\{}\[\]()_\-~?+]).{8,16})', dirt_trunk)
        if trunk:
            trunk_phone = trunk.group(1).split('_')[1]
            trunk_login = trunk.group(1).split('"')[0]
            trunk_password = trunk.group(2).split('"')[0]
            trunk_dict = {'trunk_login': trunk_login,
                          'trunk_password': trunk_password,
                          'trunk_phone': trunk_phone}
        return trunk_dict

    def get_trunks(self):
        loop = asyncio.get_event_loop()
        login = loop.create_task(self.get_login())
        loop.run_until_complete(asyncio.gather(login))
        loop.run_until_complete(self.get_list_trunks())
        coros = [loop.create_task(self.get_trunk(link)) for link in self.unique_payloads_links]
        loop.run_until_complete(asyncio.gather(*coros))
        loop.run_until_complete(self.close_session())
        
        return self.list_trunks