'''
Copyright 2014, Austin Owens, All rights reserved.

Created on Dec 28, 2014

@author: Austin

An example in how to use the advanced math library I created in utilities
'''

import main.utility_package.utilities as utilities
import numpy
import random

advM = utilities.AdvancedMath()
e1 = advM.e1
e2 = advM.e2
e3 = advM.e3


T = advM.matrixMultiply(advM.Trans(e1, 10), advM.Rot(e3, 45), advM.inv(advM.Trans(e1, 10)))
print T, "\n"

R, P = advM.extractData(T)
print R, "\n"
print P, "\n"

k, angle = advM.aRot(T)
print k, "\n"
print angle, "\n"




a = numpy.random.rand(3,1)
b = numpy.random.rand(3,1)
c = numpy.random.rand(3,1)
k = a/numpy.linalg.norm(a)
k1 = b/numpy.linalg.norm(b)
k2 = c/numpy.linalg.norm(c)
phi = random.random()*180
phi1 = random.random()*180
phi2 = random.random()*180
d = random.random()
I = numpy.eye(3, dtype=int)

R, P = advM.extractData(advM.Rot(k, 0))
if numpy.all(numpy.equal(R, I, dtype=bool)):
    print('advM.Rot(k, 0) and I IS equal');
else:
    print('advM.Rot(k, 0) and I IS NOT equal');

R1, P = advM.extractData(advM.Rot(k, phi))
R2, P = advM.extractData(advM.Rot(k, phi + 360))
if numpy.all(numpy.equal(numpy.round(R1, 5), numpy.round(R2, 5))):
    print('advM.Rot(k, phi) and advM.Rot(k, phi + 360) IS equal');
else:
    print('advM.Rot(k, phi) and advM.Rot(k, phi + 360) IS NOT equal');


R1, P = advM.extractData(advM.Rot(numpy.negative(k), phi))
R2, P = advM.extractData(advM.Rot(k, phi))

if numpy.all(numpy.equal(numpy.round(R1, 5), numpy.round(numpy.transpose(R2), 5))):
    print('advM.Rot(-k, phi) and advM.Rot(k, phi)'' IS equal');
else:
    print('advM.Rot(-k, phi) and advM.Rot(k, phi)'' IS NOT equal');

R1, P = advM.extractData(advM.Rot(k, phi1))
R2, P = advM.extractData(advM.Rot(k, phi2))
R3, P = advM.extractData(advM.Rot(k, phi1 + phi2))
if numpy.all(numpy.equal(numpy.round(advM.matrixMultiply(R1, R2), 5), numpy.round(R3, 5))):
    print('advM.Rot(k, phi1)*advM.Rot(k, phi2) and advM.Rot(k, phi1 + phi2) IS equal');
else:
    print('advM.Rot(k, phi1)*advM.Rot(k, phi2) and advM.Rot(k, phi1 + phi2) IS NOT equal');

R, P = advM.extractData(advM.Rot(k, phi))
if numpy.all(numpy.equal(numpy.round(advM.matrixMultiply(R, k), 5), numpy.round(k, 5))):
    print('advM.Rot(k, phi)*k and k IS equal');
else:
    print('advM.Rot(k, phi)*k and k IS NOT equal');


R, P = advM.extractData(advM.Rot(k, phi))
c1, c2 = advM.aRot(R);
if numpy.all(numpy.equal(numpy.round(c1, 5), numpy.round(k, 5))) and numpy.all(numpy.equal(numpy.round(c2, 5), numpy.round(phi, 5))):
    print('aadvM.aRot(advM.Rot(k, phi)) and [k, phi] IS equal');
else:
    print('aadvM.aRot(advM.Rot(k, phi)) and [k, phi] IS NOT equal');


if numpy.all(numpy.equal(numpy.round(advM.inv(advM.matrixMultiply(advM.Trans(k1, d), advM.Rot(k2, phi))), 5), numpy.round(advM.matrixMultiply(advM.Rot(k2, -phi), advM.Trans(k1, -d)), 5))):
    print('inv(Trans(k1, d)*advM.Rot(k2, phi) and advM.Rot(k2, -phi)*Trans(k1, -d) IS equal');
else:
    print('inv(Trans(k1, d)*advM.Rot(k2, phi) and advM.Rot(k2, -phi)*Trans(k1, -d) IS NOT equal');


R, P = advM.extractData(advM.Rot(k, phi))
if numpy.all(numpy.equal(numpy.round(advM.matrixMultiply(R, advM.skew(a)), 5), numpy.round(advM.matrixMultiply(advM.skew(advM.matrixMultiply(R,a)), R), 5))):
    print('advM.Rot(k, 0) and I IS equal');
else:
    print('advM.Rot(k, 0) and I IS NOT equal');

