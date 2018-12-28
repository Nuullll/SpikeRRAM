
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, 'raw_data')


def process_ltp_data(ltp_data):
    result = {
        'vg': ltp_data['vg'][0],
        'vbl': [],
        'delta_mean': [],
        'delta_std': []
    }

    groups = ltp_data.groupby('vbl').groups
    for vbl, index in groups.items():
        data = ltp_data.iloc[index]

        result['vbl'].append(vbl)

        delta = (data['iend'] - data['istart']) / data['istart']
        result['delta_mean'].append(delta.mean())
        result['delta_std'].append(delta.std())

    istart_points = ltp_data['istart'].values

    return result, istart_points


def process_ltd_data(ltd_data):
    result = {
        'vg': ltd_data['vg'][0],
        'vsl': [],
        'delta_mean': [],
        'delta_std': []
    }

    groups = ltd_data.groupby('vsl').groups
    for vbl, index in groups.items():
        data = ltd_data.iloc[index]

        result['vsl'].insert(0, vbl)

        delta = (data['iend'] - data['istart']) / data['istart']
        result['delta_mean'].insert(0, delta.mean())
        result['delta_std'].insert(0, delta.std())

    istart_points = ltd_data['istart'].values

    return result, istart_points


def plot(set_result, reset_result, profile):
    params = {
        't_left': -10,
        't_right': 10,
        'A_p': 0.52,
        'tau_p': 3,
        'A_m': 0.62,
        'tau_m': 5,
    }

    labels = []
    labels += [f'{vbl}V' for vbl in set_result['vbl']]
    labels += [f'{vsl}V' for vsl in reset_result['vsl']]

    x1 = np.linspace(params['t_left'], -0, len(set_result['vbl']))
    x2 = np.linspace(0, params['t_right'], len(reset_result['vsl']))

    plt.figure()
    plt.hold(True)
    plt.errorbar(x1, set_result['delta_mean'], set_result['delta_std'],
                 fmt='rs', capsize=5)
    plt.errorbar(x2, reset_result['delta_mean'], reset_result['delta_std'],
                 fmt='bs', capsize=5)

    # annotate set reset voltages
    color = 'r'
    i = 0
    for label, x, y in zip(labels, np.hstack((x1, x2)), np.hstack((set_result['delta_mean'], reset_result['delta_mean']))):
        if i >= len(set_result['vbl']):
            color = 'b'
        plt.annotate(label, xy=(x-0.5, y-0.1), color=color)
        i += 1

    plt.ylim(-1, 1)
    ax = plt.gca()

    plt.ylabel(r'$\Delta W / W_0$')
    plt.xlabel(r'$\Delta t$ (ms)')

    ax.grid(True, axis='y')

    # plot model
    x1 = np.linspace(params['t_left'], 0, 100)
    x2 = np.linspace(0, params['t_right'], 100)
    y1 = params['A_p'] * np.exp(-np.abs(x1) / params['tau_p'])
    y2 = -params['A_m'] * np.exp(-np.abs(x2) / params['tau_m'])
    y = np.hstack((y1, y2))
    plt.plot(np.hstack((x1, x2)), y, 'g--')

    plt.legend(['exponential model', 'SET, Vg=2.5V, Vsl=0', 'RESET, Vg=5V, Vbl=0'])

    plt.annotate(r'$A_+=%s, \tau_+=%s$' % (params['A_p'], params['tau_p']), xy=(-8, 0.4), color='g')
    plt.annotate(r'$A_-=%s, \tau_-=%s$' % (params['A_m'], params['tau_m']), xy=(2, -0.75), color='g')

    plt.title(r'$W_0 = %.2f \pm %.2f \mu S$' % (profile['conductance'].mean(), profile['conductance'].std()))

    plt.show()


def main():
    data_file = os.path.join(RAW_DATA_DIR, 'stdp', 'init3000.xlsx')

    data = pd.read_excel(data_file, sheet_name=['set', 'reset'], header=None,
                         names=['id', 'istart', 'vbl', 'vg', 'vsl', 'iend'], usecols='B, L, U, V, W, Y')

    set_result, set_istart = process_ltp_data(data['set'])
    reset_result, reset_istart = process_ltd_data(data['reset'])

    istart = np.hstack((set_istart, reset_istart))  # nA
    vrd = 0.15  # V
    g = istart / vrd / 1000

    print(set_result, reset_result)

    plot(set_result, reset_result, {'conductance': g})


if __name__ == '__main__':
    main()
