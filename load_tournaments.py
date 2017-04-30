#Created by Brian Eisenberg 4/25/2017
import melee
import smash_gg_connector
import grequests

base_url = 'https://api.smash.gg/public/tournaments/schedule?expand[]&page=1&per_page=100'




class Tournament_Loader:
    def __init__(self, container):
        self.container = container
        self.pages = 2
        self.tournaments = {}
        self.phases = []
        self.urls = []

    def melee_slug(self, tournament):
        tid = str(tournament['id'])
        top_events = tournament['mutations']['cardData'][tid]['eventData']['topEvents']
        num_events = len(top_events)
        for x in range(0, num_events):
            if top_events[x]['name'] == "Melee Singles":
                return top_events[x]['slug']

    def tournament_complete(self, tournament):
        tid = str(tournament['id'])
        return bool(tournament['mutations']['cardData'][tid]['hasRegistrationEnded'])

    def get_tournaments(self, data):
        return data['items']['entities']['tournament']

    def valid_tournament (self, tournament):
        return self.melee_slug(tournament) is not None and self.tournament_complete(tournament)

    def get_urls(self, pages):
        x = 1
        urls = []
        while (x < pages):
            url = 'https://api.smash.gg/public/tournaments/schedule?expand[]&page={0}&per_page={1}'.format(x, 100)
            #print(url)
            urls.append(url)
            x += 1
        return urls

    def parse_tournament(self, r, **kwargs):
        self.urls.append(r.url)
        tournament_page = self.get_tournaments(r.json())
        for tournament in tournament_page:
            if (self.valid_tournament(tournament)):
                name = format(tournament['name'])
                tid = str(tournament['id'])
                slug = self.melee_slug(tournament)
                date = tournament['startAt']
                phase_url = smash_gg_connector.phase(slug)
                self.phases.append(phase_url)
                entrants_url = smash_gg_connector.entrants(slug)
                melee_tournament = melee.Tournament(tid, name, date, phase_url, entrants_url)
                self.tournaments[tid] = melee_tournament
                print('{0} added to tournaments'.format(name))


    def load_tournaments(self):
        pages = smash_gg_connector.Connection(base_url).pages
        urls = self.get_urls(pages)
        requests = []
        for url in urls:
            rs = grequests.get(url, hooks=dict(response=self.parse_tournament))
            requests.append(rs)
        result = grequests.map(requests)
        print(len(self.urls))
        print(len(self.phases))
        return self.phases

    '''def load_tournaments(self):
        print('loading tournaments')
        #start_time = time.time()
        phase_groups = []
        pages = smash_gg_connector.Connection(base_url).pages
        self.async(self.get_urls(pages))
        #connection = smash_gg_connector.Async_Connection(self.get_urls(pages))


        tournament_pages = connection.data_list
        for tournament_page in tournament_pages:
            tournament_page = self.get_tournaments(tournament_page)'''
