#coding=utf-8

import json

from youth import utils
from youth import maps

# Class that represents a Trip
class Trip(object):
    def __init__(self, title, expenses, duration, steps):
        self.title = title
        self.expenses = expenses
        self.duration = duration
        self.steps = steps
        self.change_action = None
    def summary(self):
        return 'Expenses: ' + str(self.expenses) + ' RUR, travel time: ' + utils.duration_to_string(self.duration)
    def jsonable(self):
        return self.__dict__

def get(from_location, start_time, transport):
    if transport == 'meteor':
        route = maps.get_route(from_location, '59.93993,30.309073')
        trip_to = create_trip('Way to Peterhof: Meteor (speed boat)', route, start_time)
    elif transport == 'train':
        route = maps.get_route(from_location, '59.9072128,30.299578099999962')
        trip_to = create_trip('Way to Peterhof: subway + suburban train', route, start_time)
    elif transport == 'bus':
        route = maps.get_route(from_location, '59.86732529999999,30.261337499999968')
        route.append(maps.RouteStep('Cross the street through the underpass and find a bus stop',
                                    5, 'About 5 mins, 150 m', None, maps.GeoPoint(59.86758, 30.261308), maps.GeoPoint(59.868398, 30.259806),
                                    maps.get_route_leg('59.86758,30.261308', '59.868398,30.259806')))
        route.append(maps.RouteStep('Take a minibus ("route-taxi"). Look for one of the following route numbers: К-424, ' +
                                    'K-424a, К-300, К-224, К-401a, К-404 or any route-taxi where you see word "Фонтаны" ' + 
                                    'on the window. Pay to driver, price may slightly vary. You should ask driver to stop in Peterhof.',
                                    60, 'About 1 hour', maps.Transport('Share taxi', 'К-424, K-424a, К-300, К-224, К-401a, К-404', None, 70)))
        route.append(maps.RouteStep('Leave route taxi on Pravlentskaya ulitsa and go to Lower Park entry',
                                    10, 'About 10 mins, 800 m', None, maps.GeoPoint(59.883884, 29.911548), maps.GeoPoint(59.880511, 29.906809),
                                    maps.get_route_leg('59.883884,29.911548', '59.880511,29.906809')))
        trip_to = create_trip('Way to Peterhof: subway + bus', route, start_time)
    trip_to.change_action = 'Change transport'
            
    
    steps_in = [
        {'instruction': 'Buy the Lower Park tickets in a box office.' + 
                        'Our recommendation to visit Lower park and Upper park with all fountains at least. Also you can try to visit Grand palace you should be prepared to the huge queues. First one to buy tickets and another one to enter. Note that ticket in lower park works only for one visit. If you leave park you are not able to visit it again at the same day.',
         'start_time': utils.time_to_string(utils.time_add_mins(start_time, 120)),
         'hint' : 'pay fare: XXX RUR'}]
    trip_in = Trip('Peterhof sightseeing', 0, 120, steps_in)
    
    option_bus = {'alias': 'bus',
                  'title': 'Subway + bus',
                  'time': '2h00',
                  'experience': 'Poor',
                  'onfoot': '1,300 m',
                  'price': '95 RUR per person',
                  'simplicity': 'Average',
                  'icon': 'placeholder',
                  'selected': transport == 'bus'}
    option_meteor = {'alias': 'meteor',
                  'title': 'Meteor (speed boat)',
                  'time': '1h15',
                  'experience': 'Good',
                  'onfoot': '900 m',
                  'price': '525 RUR per person',
                  'simplicity': 'Easy',
                  'icon': 'placeholder',
                  'risks': 'Risks: long queue before getting onboard',
                  'selected': transport == 'meteor'}
    option_train = {'alias': 'train',
                  'title': 'Subway + suburban train',
                  'time': '1h55',
                  'experience': 'Poor',
                  'onfoot': '2,500 m',
                  'price': '85 RUR per person',
                  'simplicity': 'Difficult',
                  'icon': 'placeholder',
                  'selected': transport == 'train'}
    
    context = { 'from_location': from_location, 'start_time' : utils.time_serialize(start_time) }
        
    return {'trips': [trip_to, trip_in], 'options': [option_bus, option_meteor, option_train], 'context': context}

def create_trip(title, route, start_time):    
    steps_to = []
    duration = 0
    expenses = 0
    for step in route: 
        steps_to.append({'instruction': step.direction,
                 'start_time': utils.time_to_string(utils.time_add_mins(start_time, duration)),
                 'hint' : step.addinfo,
                 'details' :
                 {
                    'show_label': 'Show the map',
                    'hide_label': 'Hide the map',
                    'action': 'map',
                    'map': { 'points' : json.dumps([s.__dict__ for s in step.points]) }
                 } if step.points != None else None})
        duration += step.duration
        expenses += step.transport.price if step.transport != None and step.transport.price != None else 0
    return Trip(title, expenses, duration, steps_to)