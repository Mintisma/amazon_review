from spyre import server
import pandas as pd
import os

import us, uk, de, jp


class ReviewDownload(server.App):
    title = 'Download Reviews'

    countries = [
        {'label': 'US', 'value': 'US'},
        {'label': 'UK', 'value': 'UK'},
        {'label': 'DE', 'value': 'DE'},
        {'label': 'JP', 'value': 'JP'},
    ]

    inputs = [
        {
            'type': 'dropdown',
            'label': 'country',
            'options': countries,
            'key': 'country',
        },
        {
            'type': 'text',
            'key': 'asin',
            'label': 'asin',
        },
        {
            'type': 'slider',
            'label': 'pages',
            'key': 'pages',
            'action_id': 'update_search',
            "min": 1, "max": 1000, "value": 1
        },
    ]

    controls = [
        {
            'type': 'button',
            'label': 'Search',
            'id': 'update_search'
        },
        {
            'type': 'button',
            'label': 'Download',
            'id': 'download'
        },
    ]

    tabs = ['Table']

    outputs = [
        {
            'type': 'table',
            'id': 'table',
            'control_id': 'update_search',
            'tab': 'Table',
            'on_page_load': True,
        },
        {
            'type': 'download',
            'id': 'download',
            'control_id': 'download',
            'on_page_load': False,
        }
    ]

    def getData(self, params):
        country = params['country']
        asin = params['asin']
        pages = int(params['pages'])

        if country == 'US':
            lst = us.multi_review(asin, pages)
        elif country == 'UK':
            lst = uk.multi_review(asin, pages)
        elif country == 'DE':
            lst = de.multi_review(asin, pages)
        elif country == 'JP':
            lst = jp.multi_review(asin, pages)

        if 'lst' in locals():
            if len(lst) > 0:
                d = {}
                for i in range(len(lst)):
                    d[i] = pd.DataFrame(lst[i])
                df = pd.concat([d[i] for i in range(len(d))])
                df = df.sort_values('helpful', ascending=False)
        return df

if __name__ == '__main__':
    app = ReviewDownload()
    app.launch(host='0.0.0.0',port=int(os.environ.get('PORT', '4000')))
