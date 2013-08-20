from test_lib import *
from fused_wake.noj import *
from numpy import loadtxt


class testWakeModel(unittest.TestCase):
    tests = {'NOJ': {'test1': {'z_0': 1.0000e-04,
                               'TI': 0.07,
                               'U0': 8.0,
                               'c_t': 0.8060,
                               'xpos': 423974,
                               'ypos': 6151447,
                               'hub_height': 70.0,
                               'rotor_diameter': 80.0,
                               'wind_direction': 270.0,
                               'points': 'unittest_ref_files/NOJ/points1.txt',
                               'u': 'unittest_ref_files/NOJ/points_u1.txt'},
                     'test2': {'z_0': 1.0000e-04,
                               'TI': 0.07,
                               'U0': 8.0,
                               'c_t': 0.8060,
                               'xpos': 423974,
                               'ypos': 6151447,
                               'hub_height': 70.0,
                               'rotor_diameter': 80.0,
                               'wind_direction': 270.0,
                               'points': 'unittest_ref_files/NOJ/points2.txt',
                               'u': 'unittest_ref_files/NOJ/points_u2.txt'}}}

    def testNOJ(self):
        plt.close(1)
        plt.figure(1)
        i = 0        
        for k, v in self.tests['NOJ'].iteritems():
            # print 'Test: ', k
            wt_desc = GenericWindTurbineVT()
            xy = [v['xpos'], v['ypos']]
            wt_desc.hub_height = v['hub_height']
            wt_desc.rotor_diameter = v['rotor_diameter']

            ws_positions = loadtxt(v['points'], delimiter=',')
            matlab_results = loadtxt(v['u'], delimiter=',')

            # Make the inflow using the log law
            inflow = NeutralLogLawInflowGenerator()
            inflow.z_0 = v['z_0']
            inflow.wind_speed = v['U0']
            inflow.z_ref = v['hub_height']
            inflow.ws_positions = ws_positions
            inflow.execute()

            wake = NOJWakeModel()
            wake.c_t = v['c_t']
            wake.wind_direction = v['wind_direction']
            wake.ws_array_inflow = inflow.ws_array
            wake.ws_positions = ws_positions
            wake.wt_desc = wt_desc
            wake.wt_xy = xy
            wake.execute()
            # print wake.ws_array_inflow, wake.ws_array, matlab_results, np.linalg.linalg.norm(wake.ws_array - matlab_results)
            eps = 1.0E-5

            plt.subplot(len(self.tests['NOJ']),1,i); i+=1
            plt.plot(wake.ws_array, label='python')
            plt.plot(matlab_results, label='matlab')
            plt.title('NOJ: ' + k)
            plt.legend()


            # ipdb.set_trace()
            self.assertTrue(norm(wake.ws_array - matlab_results) < eps)
            # ipdb.set_trace()

        plt.savefig('noj_single_wake.pdf')


class testHornsRev_NOJ(testHornsRev):
    file_NOJ_power = 'unittest_ref_files/NOJ/HR_Power_270.txt'
    file_NOJ_CT = 'unittest_ref_files/NOJ/HR_CT_270.txt'
    file_NOJ_U = 'unittest_ref_files/NOJ/HR_U_270.txt'

    def testNOJ(self):
        noj = NOJWindFarmWake()
        self.HR_test(noj, self.file_NOJ_power)

    def testMozaicTile(self):
        self.HR_test(MozaicTileWindFarmWake(), self.file_NOJ_power)



class test_AEP_NOJ(test_AEP):
    file_Positions = 'unittest_ref_files/HR_coordinates.dat'

    def testNOJ(self):
        noj = NOJWindFarmWake()
        self.HR_test(noj, self.file_NOJ_power)

    def testMozaicTile(self):
        self.HR_test(MozaicTileWindFarmWake())


if __name__ == "__main__":
    unittest.main()        