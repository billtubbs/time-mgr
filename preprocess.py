import pandas as pd
import numpy as np
import dateutil
import os


def datetime_input_from_user(message="Date: ", default=None):
    ts = None
    while ts is None:
        s = input(message)
        if s == '':
            ts = pd.Timestamp(default)
            break
        try:
            ts = pd.to_datetime(s)
        except dateutil.parser._parser.ParserError:
            print("Date not recognized. Try again.")
    return ts


data_dir = 'data'
filename = "Toggl_time_entries_2021-01-01_to_2021-12-31.csv"
df = pd.read_csv(os.path.join(data_dir, filename))

df.Duration = pd.to_timedelta(df.Duration)
df['start_time'] = pd.to_datetime(df['Start date'] + ' ' + df['Start time'])
df['end_time'] = pd.to_datetime(df['End date'] + ' ' + df['End time'])

print(df.head())

first_date = df.start_time.min().date()
last_date = df.start_time.max().date()
print(f"\nData period: {first_date} to {last_date}\n")

print("Select date range")
d1 = datetime_input_from_user(message="Start date: ", default=first_date)
d2 = datetime_input_from_user(message="End date: ", default=last_date)

selection = (df.start_time.dt.date >= d1.date()) & (df.end_time.dt.date <= d2.date())

groupby_project = df.loc[selection].groupby('Project')
duration_by_project = groupby_project['Duration'].sum().sort_values(ascending=False)
print("Projects")
print(duration_by_project.reset_index())

p = None
while p is None:
    s = input("\nSelect project: ")
    try:
        p = int(s)
    except ValueError:
        print(f"Pick a number between 0 and {len(duration_by_project)}")

project = duration_by_project.index[p]
print(f"Project: {project}")

project_records = df.loc[selection & (df.Project == project)]


def durations_by_description_key(n):
    """Return total duration by key, where key is the first
    n characters of each time entry.
    """
    durations_hrs = project_records.Duration.dt.seconds // 3600
    total_duration = project_records.Duration.sum()
    duration_fraction = (project_records.Duration / total_duration).rename('Duration (%)')
    desc_keys = project_records.Description.apply(lambda s: str(s)[0:n]).rename('Key')
    durations = pd.concat([desc_keys, durations_hrs, duration_fraction],
                          axis=1)
    duration_by_key = durations.groupby('Key').sum()
    return duration_by_key.sort_values(by='Duration (%)', ascending=False)


print(durations_by_description_key(n=8))
