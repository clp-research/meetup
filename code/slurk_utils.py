import os
from glob import glob
import pandas as pd
import json
from textwrap import wrap
from IPython.display import HTML, display
import matplotlib.pyplot as plt


# Specific to meet up

def parse_event_mu(e, column_names_only=False):
    if column_names_only:
        return 'msg time user userID receiver m-type'.split()
    return (e['msg'] if e['type'] == 'text'
            else 'cmd: ' + e['command'] if e['type'] == 'command'
            # at most the last three parts of the path are needed to identify the image:
            # else 'url: ' + '/'.join(e['url'].split('/')[-3:]) if e['type'] == 'new_image'
            # well, hardcoding that is bad, doesn't work sometimes
            # so here I'm hardcoding the fact that the word "training"
            # occurs in the URL:
            else 'url: ' + e['url'].split('training')[1] if e['type'] == 'new_image'
            else "",
            e['timestamp-iso'],
            e['user']['name'],
            e['user']['id'],
            'All' if 'receiver' not in e else e['receiver'],
            e['type'])
    

def inst2type(url):
    prefix_elements = url.split('/')[:-1]  # remove image name
    if len(prefix_elements) and len(prefix_elements[0]) == 1:  # if significant, longer than one letter
        return prefix_elements[1]
    return '/'.join(prefix_elements)


def postproc_df(in_df, game_master='Game Master'):
    '''Make some information in MeetUp DFs more accessible. Not in place, returns new DF'''
    this_df = in_df.copy()
    # canonicalise usernames
    usernames = this_df['user'].unique().tolist()
    usernames.remove(game_master)
    user2canonical = {u: c for u, c in zip(usernames, ['A', 'B'])}
    user2canonical['Game Master'] = 'GM'
    name2id = {e[0]: e[1] for e in this_df[['user', 'userID']].values}
    canonical2id = {v: name2id[k] for k, v in user2canonical.items()}
    id2canonical = {v: k for k, v in canonical2id.items()}

    this_df['user'] = this_df['user'].apply(lambda x: user2canonical[x])

    # find the current location of each user at all times
    is_in = {}
    locations = []
    for n, this_row in this_df.iterrows():
        if this_row['m-type'] == 'new_image':
            is_in[this_row['receiver']] = this_row['msg'].split()[1]  # remove "url: " part
        locations.append(
            (
                'unspec' if canonical2id['A'] not in is_in else is_in[canonical2id['A']],
                'unspec' if canonical2id['B'] not in is_in else is_in[canonical2id['B']]
            )
        )

    this_df['A_type'] = [inst2type(e[0]) for e in locations]
    this_df['B_type'] = [inst2type(e[1]) for e in locations]
    this_df['A_inst'] = [e[0] for e in locations]
    this_df['B_inst'] = [e[1] for e in locations]

    # make timestamps relative to first event
    this_df['time'] = pd.to_datetime(this_df['time']) - pd.to_datetime(this_df.iloc[0]['time'])

    # resolve receiver
    this_df['receiver'] = this_df['receiver'].apply(
        lambda x: 'All' if x == 'All' else id2canonical[x])

    # re-order columns, for easier viewing
    out_col_order = 'msg time user A_type B_type m-type receiver A_inst B_inst userID'.split()
    return this_df[out_col_order]


# Universal functions, for all slurk logfiles

def logs_to_dfs(path, parser=None, columns=None):
    '''read in slurk logfiles and return list of data frames

    Arguments:
    path -- where to look for the logfiles

    Keyword arguments:
    parser -- function that parses event into parts

    Returns:
    df -- list of DataFrames, one for each logfile
    meta_data -- filename for each DF in df
    '''
    if parser is None:
        raise ValueError("No event parser specified")
    columns = parser('', column_names_only=True)
    df = []
    meta_data = []

    for this_file in path:
        with open(this_file, 'r') as f:
            df.append(pd.DataFrame([parser(e) for e in json.load(f)],
                                   columns=columns))
            meta_data.append(this_file)
    return df, meta_data


def get_colmap(df, botname='Game Master'):
    users = df['user'].unique().tolist()
    users.remove(botname)
    colmap = dict(zip(users, 'blue green'.split()))
    colmap[botname] = 'black'
    return colmap


def user_styler(r, colmap):
    return ['color: {}'.format(colmap[r['user']]) for _ in range(len(r))]


def pp(df, width=50, textcol='msg', botname='GM'):
    out_cols = []
    for this_col in df.columns:
        textcols = [textcol] if type(textcol) is not list else textcol
        if this_col in textcols:
            out_cols.append(df[this_col]
                            .apply(lambda x: 'XXBREAKHEREXX'.join(wrap(x, width))))
        else:
            out_cols.append(df[this_col])

    display(HTML(pd.concat(out_cols, axis=1)
                 .style.apply(lambda x:
                              user_styler(x,
                                          get_colmap(df, botname=botname)),
                              axis=1)
                 .render()
                 .replace("XXBREAKHEREXX", "<br/>")))


def get_img_ade_row(df, nrow, player):
    path = df.iloc[nrow]['A_inst' if player == 'A' else 'B_inst']
    split = 'training' if 'train' in path else 'validation'
    full = os.environ['ADE_20k_PATH'] + split + path
    return plt.imread(full)


def plot_ade_row(df, nrow, size=(8, 8)):
    imgs = [get_img_ade_row(df, nrow, player) for player in ['A', 'B']]
    fig, axs = plt.subplots(1, 2)
    fig.set_size_inches(size)
    axs[0].imshow(imgs[0])
    axs[0].axis('off')
    axs[1].imshow(imgs[1])
    axs[1].axis('off')


def reduce_inst(pathseries):
    out = []
    for path in pathseries:
        out.append('/ '.join(path.split('/')))
    return out


def get_target_type(df):
    return df[df['msg'].str.contains('You have to meet in the room of type: ')]['msg'].tolist()[0].split()[-1]


def reformat_dial_pp(in_dial, show=True):
    this_dial = in_dial.copy()

    print(get_target_type(this_dial))

    this_dial[['A_inst', 'B_inst']] = this_dial[['A_inst', 'B_inst']].apply(reduce_inst)
    this_dial['public'] = this_dial['user'] + ': ' + this_dial['msg']
    this_dial.loc[this_dial['m-type'] == 'command', 'public'] = ''
    this_dial.loc[this_dial['receiver'] != 'All', 'public'] = ''

    this_dial['A-private'] = this_dial['user'] + ': ' + this_dial['msg']
    this_dial.loc[(this_dial['user'] == 'B'), 'A-private'] = ''
    this_dial.loc[(this_dial['user'] == 'A') & (this_dial['m-type'] == 'text'), 'A-private'] = ''
    this_dial.loc[(this_dial['receiver'] == 'B'), 'A-private'] = ''

    this_dial['B-private'] = this_dial['user'] + ': ' + this_dial['msg']
    this_dial.loc[(this_dial['user'] == 'A'), 'B-private'] = ''
    this_dial.loc[(this_dial['user'] == 'B') & (this_dial['m-type'] == 'text'), 'B-private'] = ''
    this_dial.loc[(this_dial['receiver'] == 'A'), 'B-private'] = ''

    this_dial[['A-private', 'B-private']] = this_dial[['A-private', 'B-private']].apply(reduce_inst)

    this_dial = this_dial[this_dial['msg'] != 'cmd: new_image']

    if show:
        display(pp(this_dial[['time', 'A-private',
                              'public', 'B-private',
                              'user', 'receiver']][10:],
                   textcol=['A-private', 'public', 'B-private'], width=100))
    else:
        return this_dial[['time', 'A-private',
                          'public', 'B-private']]
