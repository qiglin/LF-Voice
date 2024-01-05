import math

'''The LF model is the most popular voice model. It was originally implemented as an appendix of my PhD dissertation.
   Here is an improved version in Python.
   Q. Lin, Jan. 2024
'''
class LF_Voice:
    '''Implmenting the LF voice model
    '''
    def __init__(self, *, Fs=20000., Ee=-600):
        self.Fs = Fs
        self.Ee = Ee # the excitation strength, just a scale factor
        self.F0, self.Te, self.Tp, self.Ta = None, None, None, None

    def descriptive_to_generative(self, *, F0, Rk, Rg, Ra):
        '''The input is given in terms of descriptive parameters.
        Converting them to the corresponding generative ones.
        Rk, Rg, Ra are ratios not in percentage.
        '''
        T0 = 1./F0 # F0 in Hz, T0 in sec
        self.Ta = Ra*T0
        self.Tp = T0 /(2.*Rg)
        self.Te = (1.+Rk)*self.Tp
        self.F0 = F0
        return self.F0, self.Te, self.Tp, self.Ta
    def generative_to_descriptive(self, *, F0, Te, Tp, Ta):
        '''To transform the generative set of timing parameters in ms to the descriptive set 
        of ratios (relative to pitch)
        '''
        T0 = 1000./F0
        Ra = Ta/T0
        Rg = T0/(2.*Tp)
        Rk = (Te-Tp)/Tp
        return F0, Rk, Rg, Ra
    def set_generative_parameters(self, *, F0=None, Te=None, Tp=None, Ta=None):
        '''Extra method for passing generative parameters to the object
        '''
        self.Te, self.Tp, self.Ta = Te, Tp, Ta
        return

    def sanity_check(self):
        try:
            if self.Tp/self.Te < 0.5:
                raise ValueError(f'Ratio of Tp/Te={(self.Tp/self.Te):.3f} is smaller than 0.5')
            elif self.Tp >= self.Te:
                raise ValueError(f'Tp={self.Tp:.4f} is equal to or bigger than Te={self.Te}')
            elif self.Te >= 1./self.F0:
                raise ValueError(f'Te={self.Te:.4f} should be smaller than T0={(1./self.F0):.4f}')
            elif self.F0 <= 0.:
                raise ValueError(f'F0={self.F0:.1f} should be smaller than T0={(1./self.F0):.4f}')
            elif self.Ee == 0:
                raise ValueError(f'Ee cannot be 0.')
        except ValueError as e:
            print(f'ValueError in sanity_check(), {e}')
            exit()

    def _synthesis_parameters(self):
        '''A "private" method to iteratively work out synthesis parameters (or waveform 
        parameters) from the generative parameters
        '''
        F0, Te, Tp, Ta = self.F0, self.Te, self.Tp, self.Ta
        T0 = 1./self.F0
        Ee = self.Ee

        self.have_return_curve = False if Ta < 1.e-6 else True
        n_iters = 50 # 50 is a safe upper bound
        relative_threshold = 1.e-5 # threshold for early termination of looping

        # Determine waveform parameters of the return curve
        if self.have_return_curve:
            xe0 = 1./Ta
            tb = T0 - Te
            Ta = min(Ta, 0.98*tb)
            self.Ta = Ta

            for i in range(n_iters):
                x = math.exp(-tb*xe0)
                q = x - 1. + Ta*xe0
                q_prime = -tb*x + Ta
                x = q/q_prime
                xe = xe0 - x
                if abs(x/xe0) <= relative_threshold:
                    break
                xe0 = xe

            self.ex = 1./(xe*Ta) # Ee normalized to 1
            ur = self.ex * (math.exp(-xe*tb)*(1/xe+tb)-1./xe)
        else:
            ur = 0. # Zero area contained by the return curve
            xe = 0.
            tb = 0.

        self.xe = xe
        self.tb = tb

        # Next the main waveform (exponentially growing)
        omega = math.pi/Tp
        omega_te = omega * Te
        sd = math.sin(omega_te)
        cd = math.cos(omega_te)
        eesd = abs(1./sd) # Ee normalized to 1
        omega_cd = omega * cd

        alpha = 200 # initilization
        if ((Te-Tp)+Ta)/Tp >= 0.85:
            alpha = 40 # different initilization if specific condition is met
        for i in range(n_iters):
            ed = math.exp(alpha*Te)
            e0 = eesd/ed
            gg = alpha*alpha + omega*omega
            ue = e0/gg*(ed*(alpha*sd-omega_cd) + omega)
            ut = ue + ur # total area
            ut_prime = -Te*ue+(-2.*alpha*ue+e0*(ed*(Te*(alpha*sd-omega_cd)+sd)))/gg # derivative
            x = ut/ut_prime
            if abs(x/alpha) < relative_threshold:
                break
            alpha -= x

        # Check if the amplitude given is for Ee or Ug_max
        if Ee < 0:
            e0 = abs(Ee) * e0 # Ee specified
        else:
            e0 = Ee/omega/(1.+math.exp(alpha/omega*math.pi)) * gg # Ug_max specified

        self.alpha = alpha
        self.omega = omega
        self.e0 = e0
        return

    def synthesize_wave(self, *, F0=None, Te=None, Tp=None, Ta=None):
        '''Implemented as a generator to produce LF voice derivatives, namely, dUg(t)/dt
        Major components: 1) iteratively work out synthesis parameters by applying the restriction of
        net zero between the "positive area" and "negative area", 2) use a 2nd-order 
        filter to efficiently generate the main exponentially growing curve, and 3) and use a 1st-order  
        filter to efficiently generate the return curve.
        '''
        if F0 is None or Te is None or Tp is None or Ta is None:
            F0, Te, Tp, Ta = self.F0, self.Te, self.Tp, self.Ta
        else:
            self.F0, self.Te, self.Tp, self.Ta = F0, Te, Tp, Ta

        if F0 is None or Te is None or Tp is None or Ta is None:
            raise ValueError('One or more generative parameters are None')
        
        self.sanity_check()
        
        self._synthesis_parameters()
        
        Fs = self.Fs
        ite = round(Fs*self.Te)
        a1 = math.exp(self.alpha/Fs)
        x_in = self.e0 * a1 * math.sin(self.omega/Fs)
        b1 = 2.*a1*math.cos(self.omega/Fs)
        b2 = a1 * a1
        y1 = 0.
        yield y1
        y_out = x_in
        for i in range(ite):
            yield y_out
            y2 = y1
            y1 = y_out
            y_out = b1 * y1 - b2 *y2

        itot = round(Fs/self.F0)
        if self.have_return_curve:
            ed_const = math.exp(-self.tb*self.xe)
            gain = -y1 /(1.-ed_const)
            ed_const = gain * ed_const
            a1 = math.exp(-self.xe/Fs)
            y1 = -gain
            for i in range(ite, itot-1):
                y_out = a1 * y1
                y1 = y_out
                yield y_out+ed_const
        else:
            for i in range(ite, itot-1):
                yield 0.

        return




