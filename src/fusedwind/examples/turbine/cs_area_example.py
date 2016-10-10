
# --- 1 -----

from fusedwind.turbine.structure_vt import CrossSectionAreasVT

#top = Assembly()



cs_areas = CrossSectionAreasVT()

uniax = cs_areas.add_material('uniax')
uniax.E1 = 41.63e9
uniax.E2 = 14.93e9
uniax.E3 = 14.93e9
uniax.nu12 = 0.241
uniax.nu13 = 0.241
uniax.nu23 = 0.241
uniax.G12 = 5.047e9
uniax.G13 = 5.047e9
uniax.G23 = 5.047e9
uniax.rho = 1915.5

biax = cs_areas.add_material('biax')
biax.E1 = 13.92e9
biax.E2 = 13.92e9
biax.E3 = 13.92e9
biax.nu12 = 0.533
biax.nu13 = 0.533
biax.nu23 = 0.533
biax.G12 = 11.5e9
biax.G13 = 4.539e9
biax.G23 = 4.539e9
biax.rho = 1845


# add keypoints
KP000 = cs_areas.add_kp('KP000')
KP000.x = -0.1
KP000.y = 0.1
KP001 = cs_areas.add_kp('KP001')
KP001.x = 0.1
KP001.y = 0.1
KP002 = cs_areas.add_kp('KP002')
KP002.x = -0.1
KP002.y = 0.05
KP003 = cs_areas.add_kp('KP003')
KP003.x = -0.1
KP003.y = 0.05
KP004 = cs_areas.add_kp('KP004')
KP004.x = -0.05
KP004.y = 0.05
KP005 = cs_areas.add_kp('KP005')
KP005.x = +0.05
KP005.y = 0.05
KP006 = cs_areas.add_kp('KP006')
KP006.x = -0.1
KP006.y = -0.05
KP007 = cs_areas.add_kp('KP007')
KP007.x = +0.1
KP007.y = -0.05
KP008 = cs_areas.add_kp('KP008')
KP008.x = +0.1
KP008.y = -0.1
KP009 = cs_areas.add_kp('KP009')
KP009.x = -0.1
KP009.y = -0.1
KP010 = cs_areas.add_kp('KP010')
KP010.x = -0.05
KP010.y = -0.05
KP011 = cs_areas.add_kp('KP011')
KP011.x = +0.05
KP011.y = -0.05

# add areas
cap_up = cs_areas.add_area('cap_up')
cap_up.KPs = ['KP003',
              'KP002',
              'KP001',
              'KP000'
              ]
cap_up.mat = 'uniax'
cap_up.fiber_plane_angle = .0
cap_up.fiber_dir_angle = .0

cap_low = cs_areas.add_area('cap_low')
cap_low.KPs = ['KP009',
              'KP009',
              'KP007',
              'KP006'
              ]
cap_low.mat = 'uniax'
cap_low.fiber_plane_angle = .0
cap_low.fiber_dir_angle = .0

web = cs_areas.add_area('web')
web.KPs = ['KP010',
              'KP011',
              'KP005',
              'KP004'
              ]
web.mat = 'biax'
web.fiber_plane_angle = -90.0
web.fiber_dir_angle = -90.0

# HOWTO access single list object
kp = getattr(cs_areas, 'KP005')
print kp.x
print kp.y

# HOWTO access list obejct in for loop
for kpname in cs_areas.KPs:
    print kpname
    kp = getattr(cs_areas, kpname)
    print kp.x
    print kp.y