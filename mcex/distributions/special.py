'''
Created on Mar 17, 2011

@author: jsalvatier
'''
from theano import scalar,tensor
import numpy 
from scipy import special

class XlogX(scalar.UnaryScalarOp):
    """
    Compute X * log(X), with special case 0 log(0) = 0.
    """
    @staticmethod
    def st_impl(x):
        if x == 0.0:
            return 0.0
        return x * numpy.log(x)
    def impl(self, x):
        return XlogX.st_impl(x)
    def grad(self, inp, grads):
        x, = inp
        gz, = grads
        return [gz * (1 + scalar.log(x))]
    def c_code(self, node, name, inp, out, sub):
        x, = inp
        z, = out
        if node.inputs[0].type in [scalar.float32, scalar.float64]:
            return """%(z)s =
                %(x)s == 0.0
                ? 0.0
                : %(x)s * log(%(x)s);""" % locals()
        raise NotImplementedError('only floatingpoint is implemented')
scalar_xlogx  = XlogX(scalar.upgrade_to_float, name='scalar_xlogx')
xlogx = tensor.Elemwise(scalar_xlogx, name='xlogx')

class GammaLn(scalar.UnaryScalarOp):
    """
    Compute gammaln(x)
    """
    @staticmethod
    def st_impl(x):
        return special.gammaln(x)
    def impl(self, x):
        return GammaLn.st_impl(x)
    def grad(self, inp, grads):
        x, = inp
        gz, = grads
        return [gz * scalar_psi(x)]
    def c_code(self, node, name, inp, out, sub):
        x, = inp
        z, = out
        if node.inputs[0].type in [scalar.float32, scalar.float64]:
            return """%(z)s =
                lgamma(%(x)s);""" % locals()
        raise NotImplementedError('only floatingpoint is implemented')
    
scalar_gammaln  = GammaLn(scalar.upgrade_to_float, name='scalar_gammaln')
gammaln = tensor.Elemwise(scalar_gammaln, name='gammaln')


class Psi(scalar.UnaryScalarOp):
    """
    Compute gammaln(x)
    """
    @staticmethod
    def st_impl(x):
        return special.psi(x)
    def impl(self, x):
        return Psi.st_impl(x)
    
    #def grad()  no gradient now 
    
    def c_support_code(self):
        return ( 
        """
double psi(double x){

    /*taken from 
    Bernardo, J. M. (1976). Algorithm AS 103: Psi (Digamma) Function. Applied Statistics. 25 (3), 315-317. 
    http://www.uv.es/~bernardo/1976AppStatist.pdf */
    
    double y, R, psi_ = 0;
    double S  = 1.0e-5;
    double C = 8.5;
    double S3 = 8.333333333e-2;
    double S4 = 8.333333333e-3;
    double S5 = 3.968253968e-3;
    double D1 = -0.5772156649  ;   

    y = x;
    
    if (y <= 0.0)
        return psi_;
        
    if (y <= S )
        return D1 - 1.0/y;
    
    while (y < C){
        psi_ = psi_ - 1.0 / y;
        y = y + 1;}
    
    R = 1.0 / y;
    psi_ = psi_ + log(y) - .5 * R ;
    R= R*R;
    psi_ = psi_ - R * (S3 - R * (S4 - R * S5));
    
    return psi_;}
        """ )
    def c_code(self, node, name, inp, out, sub):
        x, = inp
        z, = out
        if node.inputs[0].type in [scalar.float32, scalar.float64]:
            return """%(z)s =
                psi(%(x)s);""" % locals()
        raise NotImplementedError('only floatingpoint is implemented')
    
scalar_psi = Psi(scalar.upgrade_to_float, name='scalar_psi')
psi = tensor.Elemwise(scalar_psi, name='psi')