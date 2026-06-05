"""
Data generator for the ADM city mobility platform project.
Generates realistic data for: Users, Stations, Trips, Events.
"""
import random
from datetime import datetime, timedelta

NAMES = [
    "Luca", "Marco", "Andrea", "Giuseppe", "Antonio", "Francesco", "Matteo",
    "Davide", "Lorenzo", "Simone", "Sara", "Giulia", "Martina", "Chiara",
    "Valentina", "Federica", "Alessia", "Elena", "Maria", "Laura",
    "Rahim", "Karim", "Subir", "Ameet", "Sofia", "Emma", "Fatima", "Yusuf"
]

SURNAMES = [
    "Rossi", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci",
    "Marino", "Greco", "Bruno", "Gallo", "Conti", "De Luca", "Costa", "Mancini",
    "Saha", "Das", "Khan", "Ali", "Hasan", "Schmidt", "Dupont", "Garcia", "Nguyen"
]

COUNTRIES = [
    "Italy", "Germany", "France", "Spain", "Poland", "Romania", "Portugal",
    "Greece", "Netherlands", "Belgium", "Bangladesh", "India", "Morocco", "Vietnam"
]

ITALIAN_CITIES = [
    "Milan", "Rome", "Naples", "Turin", "Palermo", "Genoa", "Bologna",
    "Florence", "Bari", "Catania", "Venice", "Verona", "Messina", "Padua", "Trieste"
]

STATION_SUFFIXES = [
    "Centrale", "Nord", "Sud", "Est", "Ovest", "Piazza",
    "Universita", "Aeroporto", "Porto", "Stadio", "Parco", "Duomo"
]

EVENT_TYPES = ["GPS", "ERROR", "BATTERY", "DELAY"]

EVENT_VALUES = {
    "GPS":     ["45.4654,9.1859", "41.9028,12.4964", "43.7696,11.2558",
                "40.8518,14.2681", "45.0703,7.6869", "44.4949,11.3426"],
    "ERROR":   ["Low battery warning", "GPS signal lost", "Network timeout",
                "Sensor failure", "Communication error", "Brake fault detected"],
    "BATTERY": ["85%", "60%", "45%", "30%", "20%", "10%", "95%", "75%"],
    "DELAY":   ["2 min delay", "5 min delay", "10 min delay",
                "Traffic congestion", "Road works", "Weather conditions"]
}


def generate_users(n_users):
    users = []
    base = datetime(1960, 1, 1)
    for i in range(n_users):
        bdate = base + timedelta(days=random.randint(0, 365 * 40))
        users.append({
            "user_id":   i + 1,
            "name":      random.choice(NAMES),
            "surname":   random.choice(SURNAMES),
            "birthdate": bdate.strftime("%Y-%m-%d"),
            "country":   random.choice(COUNTRIES)
        })
    return users


def generate_stations(n_stations=50):
    stations = []
    used = set()
    for i in range(n_stations):
        while True:
            city   = random.choice(ITALIAN_CITIES)
            suffix = random.choice(STATION_SUFFIXES)
            name   = f"{city} {suffix}"
            if name not in used:
                used.add(name)
                break
        stations.append({
            "station_id": i + 1,
            "name":       name,
            "city":       city,
            "capacity":   random.randint(10, 50)
        })
    return stations


def generate_trips(n_trips, n_users, n_stations):
    trips = []
    base = datetime(2024, 1, 1)
    for i in range(n_trips):
        user_id = random.randint(1, n_users)
        start_s = random.randint(1, n_stations)
        end_s   = random.randint(1, n_stations)
        while end_s == start_s:
            end_s = random.randint(1, n_stations)

        start_time = base + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59)
        )
        duration   = random.randint(5, 120)
        end_time   = start_time + timedelta(minutes=duration)
        total_cost = round(1.0 + duration * 0.15 + random.uniform(0, 2.0), 2)

        trips.append({
            "trip_id":          i + 1,
            "user_id":          user_id,
            "start_station_id": start_s,
            "end_station_id":   end_s,
            "start_time":       start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time":         end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cost":       total_cost
        })
    return trips


def generate_events(trips, events_per_trip):
    if events_per_trip == 0:
        return []
    events = []
    eid = 1
    for trip in trips:
        t0  = datetime.strptime(trip["start_time"], "%Y-%m-%d %H:%M:%S")
        t1  = datetime.strptime(trip["end_time"],   "%Y-%m-%d %H:%M:%S")
        dur = max((t1 - t0).total_seconds(), 1)
        for _ in range(events_per_trip):
            ts    = t0 + timedelta(seconds=random.uniform(0, dur))
            etype = random.choice(EVENT_TYPES)
            events.append({
                "event_id":  eid,
                "trip_id":   trip["trip_id"],
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "type":      etype,
                "value":     random.choice(EVENT_VALUES[etype])
            })
            eid += 1
    return events


def generate_dataset(n_users, n_trips, events_per_trip, n_stations=50):
    """Return a full dataset dict for all four entities."""
    users    = generate_users(n_users)
    stations = generate_stations(n_stations)
    trips    = generate_trips(n_trips, n_users, n_stations)
    events   = generate_events(trips, events_per_trip)
    return {"users": users, "stations": stations, "trips": trips, "events": events}
