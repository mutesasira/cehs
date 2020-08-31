
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd


class SideNav:

    def __init__(self, elements):

        self.elements = elements
        self.callbacks = []
        for els in elements:
            self.callbacks.extend(els.callbacks)

    @property
    def layout(self):
        el_layout = [dbc.Row(x.layout) for x in self.elements]

        layout = html.Div([
            dbc.Button("Show controls", id="fade-button", className="mb-3"),
            dbc.Fade(
                el_layout,
                id="fade",
                is_in=False,
                style={'transition': 'opacity 100ms ease',
                       'background': 'white',
                       #    'padding': '12px 12px 12px 12px',
                       #    'border': '1px solid gray',
                       #    'height': '80vh',
                       'width': '25vw',
                       'overflow': 'visible'},
                className='top shadow-sm p-3 mb-5 rounded'
            )
        ], style={'position':'fixed', 'left': '20px', 'top': '20px'}, className='top')
        return layout

    def _requires_dropdown(self):
        return True


class DatePicker:

    def __init__(self, element_id, min_date, max_date, initial_visible_month=None):
        self.id = element_id
        self.min_date = min_date
        self.max_date = max_date
        self.initial_visible_month = initial_visible_month or self.min_date

    @property
    def layout(self):
        layout = dbc.Col([html.Div(
            html.P(self.id,
                   className='text-center m-0 p-0'),
            style={'color': '#363638'}),
            dcc.DatePickerSingle(id=self.id,
                                 min_date_allowed=self.min_date,
                                 max_date_allowed=self.max_date,
                                 initial_visible_month=self.initial_visible_month,
                                 persistence=True,
                                 persistence_type='session',
                                 style={'width': '100%'})],
            style={'width': '100%'})
        return layout


# !TODO style date pickers
class DatePickerGroup:

    def __init__(self, els: []):
        self.els = els
        self.callbacks = []

    @property
    def layout(self):
        return dbc.Col(dbc.Row([x.layout for x in self.els]))

    def _requires_dropdown(self):
        return False


class CardLayout:
    default_colors = {'title': '#3c6792',
                      'subtitle': '#555555',
                      'text': '#363638',
                      'fig': ['#b00d3b', '#f77665', '#e2d5d1', '#96c0e0', '#3c6792']
                      }

    def __init__(self, elements: [], **kwargs):
        self.els = elements
        self.title = kwargs.get('title', '')
        self.column_width = []

        self.__callbacks = []
        for x in self.els:
            self.__callbacks.extend(x.callbacks)

    @property
    def layout(self):
        layout = [
            dbc.Row(
                dbc.Col([
                        html.Div(
                            html.H5(html.B(self.__format_string(self.title, self.data)),
                                    style={'color': '#555555',
                                           'text-align': 'center',
                                           'width': '100%'
                                           }
                                    )
                        ) if self.title != '' else None
                        ])
            ),
            dbc.Row([
                dbc.Col(self.els[0].layout, className='m-24', width=7),
                dbc.Col(self.els[1].layout, className='m-24', width=5)
            ]
            )
        ]
        # layout = [dbc.Col(x.layout, className='m-24') for x in self.els]
        return dbc.Col(layout)

    @property
    def data(self):
        return self.els[0].data

    @data.setter
    def data(self, value):
        for el in self.els:
            el.data = value

    @property
    def callbacks(self):
        return self.__callbacks

    def _requires_dropdown(self):
        return True

    def __format_string(self, string, data):
        formatted_string = string
        if '$' in string:

            assert data != {}, 'Data has to be defined for labels to be dynamic'

            keys = {
                '$label$': next(iter(data.values())).columns[0]
            }

            # first, get rid of static replacements (first column names etc)
            for key, value in keys.items():
                formatted_string = formatted_string.replace(key, str(value))

            # deal with complex labels
            while '$' in formatted_string:
                sub = self.__get_substring_between_elements(
                    formatted_string, '$')

                try:
                    if 'trace' in sub:
                        trace_index = sub.split('.')[1]
                        formatted_string = formatted_string.replace(f'$trace.{trace_index}$',
                                                                    f'{list(data.keys())[int(trace_index)]}')

                    if 'data' in sub:
                        _, index, aggregation = sub.split('.')
                        func = getattr(np, aggregation)
                        formatted_string = formatted_string.replace(f'$data.{index}.{aggregation}$',
                                                                    f'{func(list(data.values())[int(index)])[0]}')

                except Exception as e:  # !TODO handle errors explicitly
                    print(e)
                    print(
                        'Dynamic string parsing error. Are you passing all necessary arguments?')
                    return formatted_string

        return formatted_string

    def __get_substring_between_elements(self, string, element, closing_element='$'):
        try:
            out = string.split(element, 1)[1]
            out = out.split(closing_element, 1)[0] \
                if closing_element in out \
                else None
        except IndexError as e:
            out = None
            print(e)
            print('All dynamic strings should have closing $ sign')


# class NoObservation:
#     """
#         To be called when no data was recorded for a certain reference or target date
#         Renders: No Observation layout
#     """

#     @property
#     def layout(self):
#         return dbc.Col(dbc.Row([dbc.Col([
#             html.Div(
#                 html.H5(html.B('No data has been recorded for this Reference Date or Target Date',
#                                style={'color': '#000000',
#                                       'text-align': 'center',
#                                       'width': '100%'
#                                       }
#                                )
#                         )
#                 )
#             ])]))


class Methodology:

    def __init__(self, elements):

        self.elements = elements
        self.callbacks = []

    @property
    def layout(self):
        el_layout = [dbc.Row(x.layout) for x in self.elements]

        layout = html.Div([
            dbc.Button("Show Info", id="fade-button2", className="mb-3", style={'position':'fixed', 'right': '20px', 'top': '20px'}),
            dbc.Fade(
                el_layout,
                id="fade2",
                is_in=False,
                style={'transition': 'opacity 100ms ease',
                       'background': 'white',
                       'height': 'auto',
                       'width': '30vw',
                       'overflow': 'visible',
                       'position':'fixed', 'right': '20px', 'top': '80px'},
                className='top shadow-sm p-3 mb-5 rounded'
            )
        ], className='top')
        return layout

    def _requires_dropdown(self):
        return False