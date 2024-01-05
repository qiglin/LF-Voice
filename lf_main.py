import sys
import re
from getopt import getopt
from lf_voice import LF_Voice as LFV

'''Driver program for lf_voice.py
'''

def usage():
    '''Print out usage'''
    print(f'Usage-1: lf.py [-h] [-p] -s <sampling_freq_Hz> -g "F0 Ee Te Tp Ta" ')
    print(f'   where F0 is pitch in Hz, Ee excitation strength, Ta, Tp, and Ta are timing parameters in ms')
    print(f'   -g: denote the generative set of parameters to be used')
    print(f'Usage-2: lf.py -s <sampling_freq_Hz> -d "F0 Ee Rk Rg Ra"')
    print(f'   where F0 is pitch in Hz, Ee excitation strength, Rk, Rg, and Ra are dimensionless ratios relative to F0')
    print(f'   -d: denote the descriptive set of parameters to be used')
    print(f'   -h: print out this help message')
    print(f'   -p: plot the LF curves')
    sys.exit()

def parse_parameters(cfg, tmp):
    '''Parse the string of "F0, Ee, Te, Tp, Ta" or of "F0, Ee, Rk, Rg, Ra"
    Store the results into a dict, cfg
    '''
    tmp = tmp.replace(',', ' ').strip()
    tmp = re.sub('\s+', ' ', tmp).split(' ')
    if len(tmp) != 5:
        raise ValueError(f'Requires 5 numbers, given {tmp}')
    tmp = [float(t) for t in tmp]
    if cfg['generative']:
        cfg['F0'], cfg['Ee'], cfg['Te'], cfg['Tp'], cfg['Ta'] \
                    = tmp[0], tmp[1], tmp[2]/1000, tmp[3]/1000, tmp[4]/1000
        # converting timing parameters from ms to s.

        # For advanced users, F0 can be given as fundamental period (in ms) or as pitch (in Hz)
        if cfg['F0'] <= 0.:
            raise ValueError("Negative or zero pitch found, F0={cfg'F0']")
        elif cfg['F0'] < 20: # given as the pitch period is ms (instead of pitch in Hz)
            cfg['F0'] = 1000./cfg['F0']
    else:
        cfg['F0'], cfg['Ee'], cfg['Rk'], cfg['Rg'], cfg['Ra'] \
                    = tmp[0], tmp[1], tmp[2], tmp[3], tmp[4]
    return cfg

def parse_cmd(argv):
    try:
        opts, args = getopt(argv, 'hps:g:d:',
                            ['help', 'plot', 'sampling_freq=', 'generative=', 'descriptive='])
    except getopt.GetoptError as e:
        print('GetoptError, e=', e)
        usage()
    except Exception as ex:
        print('Exception in parse_cmd(), e=', ex)
        usage()

    cfg = {'generative':None, 'Fs':None, 'plot':False}
    try:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
            elif opt in ("-p", "--plot"):
                cfg['plot'] = True
            elif opt in ("-s", "--sampling_freq"):
                cfg['Fs'] = float(arg)
            elif opt in ("-g", "--generative"):
                cfg['generative'] = True
                cfg = parse_parameters(cfg, arg)
            elif opt in ("-d", "--descriptive"):
                cfg['generative'] = False
                cfg = parse_parameters(cfg, arg)
    except ValueError as err:
        print(f'ValueError, {err}')
        print('Please check your command line.')
        usage()

    return cfg


if __name__ == '__main__':
    if len(sys.argv) == 1:
        cfg = {'generative':True, 'Fs':20000, 'F0':125, 'Ee':-200, 'Te':6, 'Tp':4, 'Ta':0.2}
        cfg['Te'] /= 1000.
        cfg['Tp'] /= 1000.
        cfg['Ta'] /= 1000.
        cfg['plot'] = True
    else:
        cfg = parse_cmd(sys.argv[1:])

    lfv = LFV(Fs=cfg['Fs'], Ee=cfg['Ee'])

    if cfg['generative'] == False:
        cfg['F0'], cfg['Te'], cfg['Tp'], cfg['Ta'] = \
            lfv.descriptive_to_generative(F0=cfg['F0'], Rk=cfg['Rk'], Rg=cfg['Rg'], Ra=cfg['Ra'])

    samples = []
    for i, sample in enumerate(lfv.synthesize_wave(F0=cfg['F0'], Te=cfg['Te'], Tp=cfg['Tp'], Ta=cfg['Ta'])):
        '''synthesize_wave() is a generator. The very first sample takes some extra time to produce
        because various synthesis parameters need to be calculated iteratively.
        '''
        samples.append(sample)

    if cfg['plot']:
        import matplotlib.pyplot as plt

        tid = [i*1000./cfg['Fs'] for i in range(len(samples))]
        plt.plot(tid, samples)
        plt.plot((0, tid[-1]), (0., 0.), 'k--') # adding time axis to illustrate "zero area" contained by the curves
        ite = samples.index(min(samples))
        plt.plot((tid[ite], tid[ite]), (samples[ite], 0.), 'g-.') # adding a line to indicate the excitation epoch at Te
        plt.title('LF voice derivative: dUg(t)/dt')
        plt.xlabel('Time in msec')
        plt.show()
