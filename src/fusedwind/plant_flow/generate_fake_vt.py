from fusedwind.plant_flow.vt import GenericWindTurbineVT, GenericWindTurbinePowerCurveVT, \
    ExtendedWindTurbinePowerCurveVT, WeibullWindRoseVT, GenericWindRoseVT, GenericWindFarmTurbineLayout, WTPC
#from fusedwind.plant_flow.comp import WeibullWindRose
from fusedwind.fused_helper import init_container

from random import random
from numpy import array, vstack, linspace, pi, floor
import numpy as np
from numpy import ndarray, array, loadtxt, log, zeros, cos, arccos, sin, nonzero, argsort, NaN, mean, ones, vstack, linspace, exp, arctan, arange
from numpy import pi, sqrt, dot, diff



wr_example = {
 'wind_directions': [   0.,   30.,   60.,   90.,  120.,  150.,  180.,  210.,  240.,  270.,  300.,  330.],
 'frequency_array': array([[  5.98508681e-04,   1.29125597e-03,   1.40644367e-03, 1.50695738e-03,   1.59075031e-03,   1.65624153e-03, 1.70235893e-03,   1.72856490e-03,   1.73486257e-03, 1.72178180e-03,   1.69034515e-03,   1.64201552e-03, 1.57862816e-03,   1.50231057e-03,   1.41539443e-03, 1.32032425e-03,   1.21956703e-03,   1.11552739e-03, 1.01047187e-03,   9.06465283e-04,   8.05321315e-04, 7.08568401e-04,   6.17431098e-04,   5.32826166e-04, 4.55371884e-04,   3.85408522e-04,   3.23027505e-04, 2.68106646e-04,   2.20348820e-04,   1.79321659e-04, 1.44496131e-04,   1.15282311e-04,   9.10610673e-05, 7.12108611e-05,   5.51292806e-05,   4.22493037e-05, 3.20505858e-05,   2.40662917e-05,   1.78861305e-05, 1.31563231e-05,   9.57723654e-06,   6.89937639e-06, 4.91835204e-06,   3.46932973e-06,   2.42138393e-06, 1.67205154e-06,   1.14229776e-06,   7.72019618e-07, 5.16145719e-07,   1.88493405e-07],
                           [  5.37841890e-04,   1.17137781e-03,   1.29209566e-03, 1.40243194e-03,   1.50017830e-03,   1.58343336e-03, 1.65065464e-03,   1.70070122e-03,   1.73286418e-03, 1.74688276e-03,   1.74294495e-03,   1.72167214e-03, 1.68408831e-03,   1.63157510e-03,   1.56581497e-03, 1.48872509e-03,   1.40238526e-03,   1.30896313e-03, 1.21064049e-03,   1.10954356e-03,   1.00768041e-03, 9.06887902e-04,   8.08789626e-04,   7.14766123e-04, 6.25937453e-04,   5.43157779e-04,   4.67020940e-04, 3.97875490e-04,   3.35847385e-04,   2.80868263e-04, 2.32707260e-04,   1.91004359e-04,   1.55303494e-04, 1.25083907e-04,   9.97885749e-05,   7.88488978e-05, 6.17051693e-05,   4.78226658e-05,   3.67034680e-05, 2.78943290e-05,   2.09910581e-05,   1.56399791e-05, 1.15370570e-05,   8.42528041e-06,   6.09084297e-06, 4.35860280e-06,   3.08721638e-06,   2.16426127e-06, 1.50157853e-06,   5.64510272e-07],
                           [  7.34384828e-04,   1.59522107e-03,   1.75338058e-03, 1.89615822e-03,   2.02065184e-03,   2.12442644e-03, 2.20558187e-03,   2.26280528e-03,   2.29540446e-03, 2.30331951e-03,   2.28711186e-03,   2.24793044e-03, 2.18745677e-03,   2.10783128e-03,   2.01156471e-03, 1.90143894e-03,   1.78040205e-03,   1.65146286e-03, 1.51758962e-03,   1.38161747e-03,   1.24616827e-03, 1.11358564e-03,   9.85887069e-04,   8.64733665e-04, 7.51417342e-04,   6.46864186e-04,   5.51651985e-04, 4.66039404e-04,   3.90003912e-04,   3.23285473e-04, 2.65433096e-04,   2.15851592e-04,   1.73846289e-04, 1.38663902e-04,   1.09528303e-04,   8.56703870e-05, 6.63517639e-05,   5.08823379e-05,   3.86322096e-05, 2.90385320e-05,   2.16081112e-05,   1.59165946e-05, 1.16050941e-05,   8.37502495e-06,   5.98185836e-06, 4.22836268e-06,   2.95779353e-06,   2.04737008e-06, 1.40226805e-06,   5.21865933e-07],
                           [  8.33549350e-04,   1.84169114e-03,   2.06792348e-03, 2.28187986e-03,   2.47872489e-03,   2.65397760e-03, 2.80365465e-03,   2.92440538e-03,   3.01363035e-03, 3.06957564e-03,   3.09139654e-03,   3.07918593e-03, 3.03396438e-03,   2.95763173e-03,   2.85288197e-03, 2.72308551e-03,   2.57214521e-03,   2.40433379e-03, 2.22412177e-03,   2.03600497e-03,   1.84434078e-03, 1.65320138e-03,   1.46625052e-03,   1.28664892e-03, 1.11699093e-03,   9.59273093e-04,   8.14893252e-04, 6.84676880e-04,   5.68926093e-04,   4.67485808e-04, 3.79821142e-04,   3.05100195e-04,   2.42276867e-04, 1.90169161e-04,   1.47529438e-04,   1.13104229e-04, 8.56822934e-05,   6.41306205e-05,   4.74189068e-05, 3.46336791e-05,   2.49836383e-05,   1.77980092e-05, 1.25197133e-05,   8.69506677e-06,   5.96149641e-06, 4.03449922e-06,   2.69478465e-06,   1.77626040e-06, 1.15527504e-06,   4.12261443e-07],
                           [  8.75649591e-04,   1.96089486e-03,   2.23844060e-03, 2.50798829e-03,   2.76299025e-03,   2.99704926e-03, 3.20413948e-03,   3.37883326e-03,   3.51652048e-03, 3.61360643e-03,   3.66767480e-03,   3.67760359e-03, 3.64362439e-03,   3.56731878e-03,   3.45154953e-03, 3.30032921e-03,   3.11863272e-03,   2.91216488e-03, 2.68709730e-03,   2.44979088e-03,   2.20652129e-03, 1.96322419e-03,   1.72527478e-03,   1.49731330e-03, 1.28312416e-03,   1.08557161e-03,   9.06590931e-04, 7.47229760e-04,   6.07731093e-04,   4.87647468e-04, 3.85974642e-04,   3.01293307e-04,   2.31908402e-04, 1.75977466e-04,   1.31621718e-04,   9.70160297e-05, 7.04562783e-05,   5.04046218e-05,   3.55147821e-05, 2.46404880e-05,   1.68307569e-05,   1.13157851e-05, 7.48694566e-06,   4.87388896e-06,   3.12111215e-06, 1.96570164e-06,   1.21733999e-06,   7.41145938e-07, 4.43511188e-07,   1.47913995e-07],
                           [  9.21833138e-04,   2.02972715e-03,   2.26792759e-03, 2.48924710e-03,   2.68828202e-03,   2.86016852e-03, 3.00075514e-03,   3.10675755e-03,   3.17588458e-03, 3.20692676e-03,   3.19980011e-03,   3.15554126e-03, 3.07625259e-03,   2.96499978e-03,   2.82566704e-03, 2.66277825e-03,   2.48129442e-03,   2.28639940e-03, 2.08328616e-03,   1.87695569e-03,   1.67203910e-03, 1.47265146e-03,   1.28228339e-03,   1.10373323e-03, 9.39079988e-04,   7.89694167e-04,   6.56281665e-04, 5.38953963e-04,   4.37317052e-04,   3.50571223e-04, 2.77614200e-04,   2.17141074e-04,   1.67735711e-04, 1.27949878e-04,   9.63677749e-05,   7.16551869e-05, 5.25936127e-05,   3.81007254e-05,   2.72391342e-05, 1.92157716e-05,   1.33743058e-05,   9.18285657e-06, 6.21901467e-06,   4.15380956e-06,   2.73587799e-06, 1.77670735e-06,   1.13749101e-06,   7.17855181e-07, 4.46505085e-07,   1.53770564e-07],
                           [  1.16901958e-03,   2.57123904e-03,   2.86920047e-03, 3.14535195e-03,   3.39300616e-03,   3.60617562e-03, 3.77978313e-03,   3.90984848e-03,   3.99363885e-03, 4.02977166e-03,   4.01826203e-03,   3.96051003e-03, 3.85922694e-03,   3.71830354e-03,   3.54262752e-03, 3.33786020e-03,   3.11018562e-03,   2.86604639e-03, 2.61188155e-03,   2.35388078e-03,   2.09776781e-03, 1.84862318e-03,   1.61075328e-03,   1.38760920e-03, 1.18175505e-03,   9.94882455e-04,   8.27865106e-04, 6.80845117e-04,   5.53342092e-04,   4.44375282e-04, 3.52589813e-04,   2.76379013e-04,   2.13996464e-04, 1.63653140e-04,   1.23596898e-04,   9.21732637e-05, 6.78679450e-05,   4.93326593e-05,   3.53966246e-05, 2.50665048e-05,   1.75177046e-05,   1.20797737e-05, 8.21835936e-06,   5.51572541e-06,   3.65138564e-06, 2.38394737e-06,   1.53484965e-06,   9.74342318e-07, 6.09789869e-07,   2.11057434e-07],
                           [  1.29167899e-03,   2.84708713e-03,   3.18980733e-03, 3.51603080e-03,   3.81940501e-03,   4.09401758e-03, 4.33455093e-03,   4.53642998e-03,   4.69595418e-03, 4.81040657e-03,   4.87813326e-03,   4.89858844e-03, 4.87234169e-03,   4.80104624e-03,   4.68736902e-03, 4.53488515e-03,   4.34794164e-03,   4.13149657e-03, 3.89094109e-03,   3.63191281e-03,   3.36010887e-03, 3.08110718e-03,   2.80020331e-03,   2.52226949e-03, 2.25164048e-03,   1.99202970e-03,   1.74647673e-03, 1.51732586e-03,   1.30623376e-03,   1.11420268e-03, 9.41634913e-04,   7.88403451e-04,   6.53933420e-04, 5.37289163e-04,   4.37262064e-04,   3.52454934e-04, 2.81359597e-04,   2.22425166e-04,   1.74115486e-04, 1.34954997e-04,   1.03563111e-04,   7.86777442e-05, 5.91691442e-05,   4.40454359e-05,   3.24514605e-05, 2.36624992e-05,   1.70743903e-05,   1.21913870e-05, 8.61289935e-06,   3.28301641e-06],
                           [  1.38975021e-03,   3.05388147e-03,   3.41196792e-03, 3.75586418e-03,   4.08021930e-03,   4.38002322e-03, 4.65070152e-03,   4.88820790e-03,   5.08910961e-03, 5.25066120e-03,   5.37086331e-03,   5.44850321e-03, 5.48317510e-03,   5.47527889e-03,   5.42599698e-03, 5.33724976e-03,   5.21163111e-03,   5.05232625e-03, 4.86301505e-03,   4.64776411e-03,   4.41091185e-03, 4.15695061e-03,   3.89040996e-03,   3.61574527e-03, 3.33723508e-03,   3.05889041e-03,   2.78437835e-03, 2.51696181e-03,   2.25945622e-03,   2.01420338e-03, 1.78306198e-03,   1.56741358e-03,   1.36818226e-03, 1.18586592e-03,   1.02057680e-03,   8.72088629e-04, 7.39888098e-04,   6.23227994e-04,   5.21180074e-04, 4.32685696e-04,   3.56602728e-04,   2.91747592e-04, 2.36931694e-04,   1.90991816e-04,   1.52814395e-04, 1.21353871e-04,   9.56455150e-05,   7.48132906e-05, 5.80734310e-05,   2.38465774e-05],
                           [  1.17262387e-03,   2.60943924e-03,   2.96153237e-03, 3.30851045e-03,   3.64475920e-03,   3.96476457e-03, 4.26322159e-03,   4.53514933e-03,   4.77600674e-03, 4.98180415e-03,   5.14920535e-03,   5.27561545e-03, 5.35925035e-03,   5.39918426e-03,   5.39537250e-03, 5.34864811e-03,   5.26069168e-03,   5.13397512e-03, 4.97168137e-03,   4.77760292e-03,   4.55602326e-03, 4.31158587e-03,   4.04915610e-03,   3.77368147e-03, 3.49005569e-03,   3.20299167e-03,   2.91690796e-03, 2.63583236e-03,   2.36332540e-03,   2.10242534e-03, 1.85561537e-03,   1.62481230e-03,   1.41137541e-03, 1.21613315e-03,   1.03942478e-03,   8.81153559e-04, 7.40848127e-04,   6.17728441e-04,   5.10773070e-04, 4.18784878e-04,   3.40452671e-04,   2.74406873e-04, 2.19267908e-04,   1.73686495e-04,   1.36375601e-04, 1.06134229e-04,   8.18635783e-05,   6.25763984e-05, 4.74005026e-05,   1.90836763e-05],
                           [  8.24556184e-04,   1.83763158e-03,   2.08931937e-03, 2.33782881e-03,   2.57906571e-03,   2.80899131e-03, 3.02370408e-03,   3.21952653e-03,   3.39309331e-03, 3.54143638e-03,   3.66206360e-03,   3.75302687e-03, 3.81297659e-03,   3.84119948e-03,   3.83763784e-03, 3.80288855e-03,   3.73818169e-03,   3.64533906e-03, 3.52671394e-03,   3.38511469e-03,   3.22371493e-03, 3.04595417e-03,   2.85543299e-03,   2.65580696e-03, 2.45068367e-03,   2.24352684e-03,   2.03757097e-03, 1.83574943e-03,   1.64063812e-03,   1.45441579e-03, 1.27884152e-03,   1.11524876e-03,   9.64554676e-04, 8.27283012e-04,   7.03597966e-04,   5.93346558e-04, 4.96106649e-04,   4.11237894e-04,   3.37933106e-04, 2.75267810e-04,   2.22246152e-04,   1.77841801e-04, 1.41032921e-04,   1.10830721e-04,   8.63015293e-05, 6.65826278e-05,   5.08923720e-05,   3.85353060e-05, 2.89030828e-05,   1.15455611e-05],
                           [  7.32521276e-04,   1.58062566e-03,   1.72456794e-03, 1.85424825e-03,   1.96761259e-03,   2.06297576e-03, 2.13905365e-03,   2.19498595e-03,   2.23034790e-03, 2.24514978e-03,   2.23982416e-03,   2.21520098e-03, 2.17247154e-03,   2.11314284e-03,   2.03898398e-03, 1.95196698e-03,   1.85420428e-03,   1.74788524e-03, 1.63521428e-03,   1.51835254e-03,   1.39936521e-03, 1.28017592e-03,   1.16252948e-03,   1.04796352e-03, 9.37789483e-04,   8.33082624e-04,   7.34680586e-04, 6.43189695e-04,   5.58997846e-04,   4.82292734e-04, 4.13084095e-04,   3.51228587e-04,   2.96456022e-04, 2.48395784e-04,   2.06602397e-04,   1.70579417e-04, 1.39801019e-04,   1.13730832e-04,   9.18378043e-05, 7.36090050e-05,   5.85594467e-05,   4.62391216e-05, 3.62375226e-05,   2.81859826e-05,   2.17581928e-05, 1.66692633e-05,   1.26736799e-05,   9.56247777e-06, 7.15991731e-06,   2.85976559e-06]]),
 'wind_speeds': [  4.        ,   4.42857143,   4.85714286,   5.28571429,
                  5.71428571,   6.14285714,   6.57142857,   7.        ,
                  7.42857143,   7.85714286,   8.28571429,   8.71428571,
                  9.14285714,   9.57142857,  10.        ,  10.42857143,
                 10.85714286,  11.28571429,  11.71428571,  12.14285714,
                 12.57142857,  13.        ,  13.42857143,  13.85714286,
                 14.28571429,  14.71428571,  15.14285714,  15.57142857,
                 16.        ,  16.42857143,  16.85714286,  17.28571429,
                 17.71428571,  18.14285714,  18.57142857,  19.        ,
                 19.42857143,  19.85714286,  20.28571429,  20.71428571,
                 21.14285714,  21.57142857,  22.        ,  22.42857143,
                 22.85714286,  23.28571429,  23.71428571,  24.14285714,
                 24.57142857,  25.        ]}


def generate_a_valid_wt(D = 200*random()):
    wt_desc = GenericWindTurbineVT()
    wt_desc.rotor_diameter = D
    wt_desc.hub_height = D * (0.5 + random())
    return wt_desc

def generate_random_GenericWindTurbinePowerCurveVT(D=None):
    """
    Generate a random turbine and power curve using the GenericWindTurbinePowerCurveVT class

    Parameters
    ----------
    D       float, default=random, (optional)
            The wind turbine rotor diameter

    Returns
    -------
    wt_desc GenericWindTurbinePowerCurveVT
            A random wind turbine power curve and c_t curve variable tree
    """
    if not D:
        D = 200*random()

    wt_desc = GenericWindTurbinePowerCurveVT()
    wt_desc.rotor_diameter = D
    wt_desc.hub_height = D * (0.5 + random())
    wt_desc.cut_in_wind_speed = 2. + 4. * random()
    wt_desc.cut_out_wind_speed = 20. + 10. * random()
    rho = 1.225
    rated_wind_speed = 8. + 4. * random()
    max_a = 0.333 * random()
    max_cp = 4 * max_a * (1 - max_a)**2.
    max_ct = 4 * max_a * (1 - max_a)
    A = 0.25 * pi * D**2. # Rotor area
    ideal_power = lambda ws: 0.5 * rho * A * max_cp * ws **3.
    real_power = lambda ws: ideal_power(ws) if ws < rated_wind_speed else ideal_power(rated_wind_speed)
    #a_ct = -sqrt(-c_t + 1)/2 + 1/2
    ct_from_cp = lambda cp: min(0.89, cp  * 2.)
    cp_from_power = lambda power, ws: power/(0.5 * rho * A * ws**3.)
    ct_from_power = lambda pws: ct_from_cp(cp_from_power(pws[0], pws[1]))
    N = 3+int(random() * 100)
    ws = linspace(wt_desc.cut_in_wind_speed, wt_desc.cut_out_wind_speed, N)
    wt_desc.power_curve = vstack([ws, map(real_power, ws)]).T
    wt_desc.c_t_curve = vstack([ws, map(ct_from_power, zip(wt_desc.power_curve[:,1],ws))]).T
    wt_desc.power_rating = ideal_power(rated_wind_speed)
    wt_desc.rated_wind_speed = rated_wind_speed
    wt_desc.air_density = rho
    wt_desc.test_consistency()
    return wt_desc

def generate_random_WTPC(D=None, **kwargs):
    wt = generate_random_GenericWindTurbinePowerCurveVT(D)
    inputs = {k: getattr(wt, k) for k in wt.list_vars()}
    inputs['position'] = np.random.rand(2)
    inputs['name'] = 'wt'
    # Replacing the parameters by the inputs of the function
    for k, v in kwargs.iteritems():
        inputs[k] = v
    return WTPC(**inputs)


def generate_random_wt_positions(D=None, nwt=None, min_D=None):
    """
    Generate a random layout of wind turbines

    Parameters
    ----------
    D       float, default=random, (optional)
            The wind turbine rotor diameter

    nwt     int, default=random, (optional)
            The number of turbines in the layout

    min_D   float, default=random, (optional)
            The minimum of rotor diameter between turbines

    Returns
    ------
    wt_positions    ndarray [nwt, 2]
                    The (x,y) position of the turbines

    Example
    -------
    >>> generate_random_wt_positions(D=82., nwt=5, min_D=7.)
    array([[  0.        ,   0.        ],
           [ -1.74906289, -30.4628047 ],
           [ -5.88793386,  -7.11251901],
           [-35.53857721,  32.42632383],
           [ 15.25619612,   0.79847237],
           [  1.20034923, -10.73881476]])

    """

    if not D:
        D = 200*random()
    if not nwt:
        nwt = int(30*random())
    if not min_D:
        min_D = 3. + 5.*random()

    Nnorm = lambda x: sqrt(x[0]**2. + x[1]**2.)
    min_dist = lambda pos_arr, pos: min(map(Nnorm, pos_arr - pos))
    def random_path(wt_positions):
        N = floor(random()*len(wt_positions))
        #print N
        x0, y0 = wt_positions[N,:]
        count = 0
        while min_dist(wt_positions, array([x0,y0])) < min_D and count < 20:
            x0, y0 =  x0 + (0.5-random()) * D, y0 + (0.5-random()) * D
            count +=1
        return vstack([wt_positions, [x0, y0]])

    wt_positions = array([[0.,0.]])
    for i in range(nwt-1):
        wt_positions = random_path(wt_positions)
    return wt_positions

def generate_random_GenericWindRoseVT():
    """
    Generate a random GenericWindRoseVT object

    Parameters
    ----------

    N/A

    Returns
    -------
    wind_rose   GenericWindRoseVT
                A wind rose variable tree

    """
    weibull_array = np.array([[  0.00000000e+00,   3.59673400e-02,  9.22422800e+00,   2.38867200e+00],
                             [  3.00000000e+01,   3.94977300e-02,   9.86435600e+00,   2.44726600e+00],
                             [  6.00000000e+01,   5.17838000e-02,   9.65220200e+00,   2.41992200e+00],
                             [  9.00000000e+01,   6.99794900e-02,   9.98217800e+00,   2.58789100e+00],
                             [  1.20000000e+02,   8.36383000e-02,   1.00946000e+01,   2.74804700e+00],
                             [  1.50000000e+02,   6.43412500e-02,   9.64369000e+00,   2.59179700e+00],
                             [  1.80000000e+02,   8.64220000e-02,   9.63377500e+00,   2.58007800e+00],
                             [  2.10000000e+02,   1.17690000e-01,   1.05678600e+01,   2.54492200e+00],
                             [  2.40000000e+02,   1.51555100e-01,   1.14525200e+01,   2.46679700e+00],
                             [  2.70000000e+02,   1.47361100e-01,   1.17423700e+01,   2.60351600e+00],
                             [  3.00000000e+02,   1.00109800e-01,   1.16923200e+01,   2.62304700e+00],
                             [  3.30000000e+02,   5.16542400e-02,   1.01385800e+01,   2.32226600e+00]])
    ### -> This is going to be really slow because of interpolation
    nwd, nws = 4+int(random()*360), 4+int(random()*25)
    wd = linspace(0., 360., nwd)[:-1].tolist()
    ws = linspace(3., 30., nws).tolist()
    #wind_rose_array = array([[wd_, random(), random()*15., random()*4.] for wd_ in wd])
    #wind_rose_array *= [1., 1./wind_rose_array[:,1].sum(), 1., 1.]
    #return WeibullWindRose()(wind_directions= wd,
    #                         wind_speeds=ws,
    #                         wind_rose_array=wind_rose_array).wind_rose
    #
    gwr = GenericWindRoseVT(wind_directions=wd, wind_speeds=ws, weibull_array=weibull_array)
    return gwr

# def generate_random_wt_layout(D=None, nwt=None):
#     """
#     Generate a random GenericWindFarmTurbineLayout of wind turbines
#
#     Parameters
#     ----------
#     D       float, default=random, (optional)
#             The wind turbine rotor diameter
#
#     nwt     int, default=random, (optional)
#             The number of turbines in the layout
#
#     Returns
#     -------
#     wt_layout   GenericWindFarmTurbineLayout
#                 A random wind turbine layout
#
#     """
#     if D is None:
#         D = 200*random()
#     if nwt is None:
#         nwt = int(30*random())
#     wt_layout = GenericWindFarmTurbineLayout()
#     wt_layout.wt_positions = generate_random_wt_positions(D=D, nwt=nwt)
#     wt_layout.wt_list = [generate_random_GenericWindTurbinePowerCurveVT(D) for i in range(nwt)]
#     wt_layout.wt_wind_roses = [generate_random_GenericWindRoseVT() for i in range(nwt)]
#     wt_layout.wt_names = ['wt_%d'%(i) for i in range(nwt)]
#     wt_layout.test_consistency()
#     return wt_layout

def generate_random_wt_layout(D=None, nwt=None):
    """
    Parameters
    ----------
    D       float, default=random, (optional)
            The wind turbine rotor diameter

    nwt     int, default=random, (optional)
            The number of turbines in the layout

    Returns
    -------
    a random GenericWindFarmTurbineLayout instance
    """
    if not D:
        D = 200*random()
    if not nwt:
        nwt = int(30*random())
    wt_positions = generate_random_wt_positions(D=D, nwt=nwt)
    return GenericWindFarmTurbineLayout([generate_random_WTPC(
        name='wt%d'%(n),
        position=wt_positions[n,:],
        wind_rose=generate_random_GenericWindRoseVT()) for n in range(nwt)])