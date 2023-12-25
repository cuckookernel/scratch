
from mido import MidiFile


def _main():
    path = "/home/teo/Downloads/MIDIs/Queen - Bohemian Rhapsody.mid"
    file = MidiFile(path)
    # %%
    dir(file)
    # %%
    file.print_tracks()
    # %%
    len(file.tracks)
    # %%
    msgs = file.tracks[2]
    # %%
    for msg in msgs:
        print(msg)
    # %%
    note_msgs = [msg for msg in msgs
                 if msg.type.startswith("note_")]
    # %%
    note_msgs1 = sorted(note_msgs, key=lambda msg: msg.time)
    # %%
    import pandas as pd
    notes = pd.DataFrame(note_msgs, columns=["msg"])
    notes['type'] = notes['msg'].apply(lambda msg: msg.type)
    notes['note'] = notes['msg'].apply(lambda msg: msg.note)
    notes['time'] = notes['msg'].apply(lambda msg: msg.time)
    notes['velo'] = notes['msg'].apply(lambda msg: msg.velocity)

    del notes['msg']
    # %%
    notes1 = notes.sort_values('time')
