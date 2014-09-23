import os
import openmdao.main.resource



class ClusterAllocator(openmdao.main.resource.ClusterAllocator):
  '''
    This class is a wrapper for creating a ClusterAllocator on Peregrine.
    It will first check for a PBS_NODEFILE, and allocate ClusterHosts
    based on those nodes listed.
    Failing that, it will allocate all four login nodes as ClusterHosts

    When allocating ClusterHosts, it uses the current environment to set up
    the individual hosts environment.
  '''

  def __init__(self):
    '''
      Environment probing, machine setup
    '''
    nodeset=set()
    if 'PBS_NODEFILE' in os.environ:
      with open(os.environ['PBS_NODEFILE']) as nodefile:
        for h in nodefile:
          nodeset.add(h.strip())
    else:
      nodeset.update(['hpc-login4'])
#      nodeset.update(['hpc-login1','hpc-login2','hpc-login3','hpc-login4'])
    #print(nodeset)
    print('Running on %s'%(','.join(nodeset)))
    # Set up environment command on login
    # First pass just import modules
    newmods = os.environ['LOADEDMODULES'].split(':')
    newenv = 'export TMPDIR=/scratch/$USER/tmp; export MODULEPATH=%s;module purge; module load %s;'%(os.environ['MODULEPATH'],' '.join(newmods))
#    newenv = 'export TMPDIR=/home/pgraf/projects/wese/fused_wind-11_16_13/fusedwind/src/fusedwind/runiec_proto/save_runs; export MODULEPATH=%s;module purge; module load %s;'%(os.environ['MODULEPATH'],' '.join(newmods))
    #print(newenv)
    machines = []
    for m in nodeset:
      machines.append(ClusterHost(m,None,True,True,beforestart=newenv))
    #super(openmdao.main.resource.ClusterAllocator, self).__init__('peregrinecluster',machines=machines,allow_shell=True)
    openmdao.main.resource.ClusterAllocator.__init__(self,'peregrinecluster',machines=machines,allow_shell=True)

import openmdao.main.resource 
import base64
import cPickle

import logging
import os
import subprocess
import time

from openmdao.main.rbac import get_credentials
from openmdao.main.mp_util import setup_tunnel, setup_reverse_tunnel

# Logging.
_LOGGER = logging.getLogger('peregrine_clusterhost')


class ClusterHost(openmdao.main.resource.ClusterHost):
    def __init__(self, hostname, python=None, tunnel_incoming=False,
                 tunnel_outgoing=False, identity_filename=None,beforestart=""):
        """
        Same as the Host init options but adds the ability to run commands in ssh
        prior to starting the manager.

        beforestart: string
            Commands needed to set up the node environment to run in a cluster
            properly.
        """
        self.beforestart=beforestart
        super(openmdao.main.resource.ClusterHost, self).__init__(hostname, python, tunnel_incoming, tunnel_outgoing, identity_filename)

    def start_manager(self, index, authkey, address, files, allow_shell=False):
        """
        Launch remote manager process via `ssh`.
        The environment variable ``OPENMDAO_KEEPDIRS`` can be used to avoid
        removal of the temporary directory used on the host.

        index: int
            Index in parent cluster.

        authkey: string
            Authorization key used to connect to host server.

        address: (ip_addr, port) or string referring to pipe.
            Address to use to connect back to parent.

        files: list(string)
            Files to be sent to support server startup.

        allow_shell: bool
            If True, :meth:`execute_command` and :meth:`load_model` are allowed
            in created servers. Use with caution!

        """
        try:
            self._check_ssh()
        except RuntimeError:
            self.state = 'failed'
            return

        self.tempdir = self._copy_to_remote(files)
        if not self.tempdir:
            self.state = 'failed'
            return
        _LOGGER.debug('startup files copied to %s:%s',
                      self.hostname, self.tempdir)

        if self.tunnel_incoming:
            _LOGGER.debug('setup reverse tunnel from %s to %s:%s',
                          self.hostname, address[0], address[1])
            address, cleanup = \
                setup_reverse_tunnel(self.hostname, address[0], address[1], 
                                     identity=self.identity_filename)
            self.reverse_cleanup = cleanup

        cmd = self._ssh_cmd()
        cmd.extend([self.hostname, self.beforestart, self.python, '-c',
                   '"import sys;'
                   ' sys.path.append(\'.\');'
                   ' import os;'
                   ' os.chdir(\'%s\');'
                   ' from mp_distributing import main;'
                   ' main()"' % self.tempdir])
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

        credentials = get_credentials()
        allowed_users = {credentials.user: credentials.public_key}

        # Tell the server what name to bind to
        # (in case it has multiple interfaces).
        user, remote_name = self.hostname.split('@')
        
        data = dict(
            name='BoostrappingHost', index=index, hostname=remote_name,
            # Avoid lots of SUBDEBUG messages.
            dist_log_level=max(_LOGGER.getEffectiveLevel(), logging.DEBUG),
            dir=self.tempdir, authkey=str(authkey), allowed_users=allowed_users,
            allow_shell=allow_shell, allow_tunneling=self.tunnel_outgoing,
            parent_address=address, registry=self.registry,
            keep_dirs=os.environ.get('OPENMDAO_KEEPDIRS', '0'))

        # Windows can't handle binary on stdin.
        dump = cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)
        dump = base64.b64encode(dump)
        _LOGGER.debug('sending %s config info (%s)', self.hostname, len(dump))
        self.proc.stdin.write(dump)
        self.proc.stdin.close()
        time.sleep(1)  # Give the proc time to register startup problems.
        self.poll()
        if self.state != 'failed':
            self.state = 'started'
