################################################################################
#
#   Yahoo Finance
#
#   Scrapes and displays major indices from finance.yahoo.com
#
#   - Initialization parameters:
#
#       refresh     Minutes to wait between webscrapes (default=15, min=1)
#       TODO: closed_refresh
#
#   - Format parameters:  none
#
#
#   Jeff Jetton, Feb-Mar 2023
#
################################################################################



import datetime as dt
from segment_parent import SegmentParent


class Segment(SegmentParent):
    
    symbols = {'^GSPC':'S&P 500',
               '^DJI' :'Dow Jones',
               '^IXIC':'NASDAQ',
               '^RUT' :'Russell'
              }
    
    def __init__(self, display, init):
        super().__init__(display, init, default_refresh=15)


    def show_intro(self):
        self.d.print('Financial info from finance.yahoo.com')


    @classmethod
    def parse_indexes(cls, streamers):
        ind = []
        curr_symbol = ''
        i = {'symbol':''}
        for s in streamers:
            symbol = s['data-symbol']
            # Check for new symbol
            if symbol != curr_symbol:
                # Close out any current index
                if i['symbol'] != '':
                    ind.append(i)
                # Set up new index
                i = {'symbol':symbol, 'price':'N/A', 'delta':'N/A', 'delta_pct':'N/A'}
                curr_symbol = symbol
            # Check for price
            if s['data-field'] == 'regularMarketPrice':
                i['price'] = s.contents[0]
            elif s['data-field'] == 'regularMarketChange':
                i['delta'] = s.contents[0].contents[0]
            elif s['data-field'] == 'regularMarketChangePercent':
                i['delta_pct'] = s.contents[0].contents[0]
        # Append last index
        ind.append(i)
        return ind


    @classmethod
    def process_indexes(cls, ind):
        # Translates symbols and only returns the symbols we have names for
        new_ind = []
        for i in ind:
            if i['symbol'] not in cls.symbols:
                continue
            i['name'] = cls.symbols[i['symbol']]
            new_ind.append(i)
        return new_ind


    
    def refresh_data(self):
        self.data = {'fetched_on':dt.datetime.now(),
                     'market_message':'',
                     'indexes':[],
                    }
        soup = self.get_soup('https://finance.yahoo.com')
        if soup is None:
            return
        msg = soup.find('span', {'data-id':'mk-msg'})
        if len(msg) > 0:
            self.data['market_message'] = self.d.clean_chars(msg.contents[0])
        streamers = soup.find_all('fin-streamer')
        self.data['indexes'] = self.parse_indexes(streamers)
        self.data['indexes'] = self.process_indexes(self.data['indexes'])



    def show(self, fmt):
        # Check for need to refresh
        if self.data_is_stale():
            self.d.print_update_msg('Updating Financial Data')
            self.refresh_data()

        self.d.print_header('Stocks', '$')
        self.d.newline()
        
        if 'CLOSED' in self.data['market_message'].upper():
            self.d.print(self.data['market_message'])
        else:
            self.d.print(f"As of {self.d.fmt_time_text(self.data['fetched_on'])}")
    
        for i in self.data['indexes']:
            self.d.newline()
            self.d.print(f"    {i['name']:9}  {i['price']:>9}")
            self.d.print(f"               {i['delta']:>9}  {i['delta_pct']}")

