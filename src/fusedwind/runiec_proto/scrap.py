
def some_func():

        print "collecting ALL the output"
        for c in self.ws_driver.recorders[0].get_iterator():
            res =  c['runner.output']
            aero = res.aerocode
            fast = aero.rawfast  ### this may not exist, only for fast wrapper
            case = c['runner.input']
            print "!@#$!@#$!@#$"
            print "output for case ", case
            print "dlcresult = ", res
            print "aerocode wrapper= ", aero
            print "aerocode wrapper's underlying code = ", fast
            print case.ws, case.randomseed, max(fast.getOutputValue("RotPwr"))
#        print "again: windspeed, randomseed, max power"
        fout = file(output_params['main_output_file'], "w")
        fout.write( "#Results summary: \n")
        fout.write( "#Vs Hs Tp WaveDir, TwrBsMxt \n")
        for c in self.ws_driver.recorders[0].get_iterator():
            res =  c['runner.output']
            aero = res.aerocode
            fast = aero.rawfast  ### this may not exist, only for fast wrapper
            case = c['runner.input']
#            print case.ws, case.randomseed, fast.getMaxPower()  ### this may not exist, just an example
#            print "%.2f  %.2f   %.2f" % (case.ws, case.fst_params['WaveHs'], fast.getMaxPower())  ### this may not exist, just an example

#            print "%s   %.2f" % (case.name, fast.getMaxOutputValue('TwrBsMxt', directory=aero.results_dir))  ### this may not exist, just an example
            fout.write( "%.2f %.2f %.2f %.2f   %.2f\n" % (case.ws, case.fst_params['WaveHs'], case.fst_params['WaveTp'],case.fst_params['WaveDir'], fast.getMaxOutputValue('TwrBsMxt', directory=aero.results_dir)))  ### this may not exist, just an example
