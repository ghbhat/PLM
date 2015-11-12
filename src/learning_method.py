"""
Implemented by Guillaume Lample

https://github.com/glample/UltraDeep/blob/master/learning_method.py
"""
import numpy as np
import theano
import theano.tensor as T

floatX = theano.config.floatX
device = theano.config.device


def sgd(cost, params, lr=0.01):
    """
    Stochatic gradient descent.
    """
    lr = theano.shared(np.float32(lr).astype(floatX))

    gradients = T.grad(cost, params)

    updates = []
    for p, g in zip(params, gradients):
        updates.append((p, p - lr * g))

    return updates


def sgdmomentum(cost, params, lr=0.01, momentum=0.9):
    """
    Stochatic gradient descent with momentum. Momentum has to be in [0, 1)
    """
    # Check that the momentum is a correct value
    assert 0 <= momentum < 1

    lr = theano.shared(np.float32(lr).astype(floatX))
    momentum = theano.shared(np.float32(momentum).astype(floatX))

    gradients = T.grad(cost, params)
    velocities = [theano.shared(np.zeros_like(param.get_value(borrow=True)).astype(floatX)) for param in params]

    updates = []
    for param, gradient, velocity in zip(params, gradients, velocities):
        new_velocity = momentum * velocity - lr * gradient
        updates.append((velocity, new_velocity))
        updates.append((param, param + new_velocity))
    return updates


def adagrad(cost, params, lr=1.0, epsilon=1e-6):
    """
    Adagrad. Based on http://www.ark.cs.cmu.edu/cdyer/adagrad.pdf
    """
    lr = theano.shared(np.float32(lr).astype(floatX))
    epsilon = theano.shared(np.float32(epsilon).astype(floatX))

    gradients = T.grad(cost, params)
    gsums = [theano.shared(np.zeros_like(param.get_value(borrow=True)).astype(floatX)) for param in params]

    updates = []
    for param, gradient, gsum in zip(params, gradients, gsums):
        new_gsum = gsum + gradient ** 2.
        updates.append((gsum, new_gsum))
        updates.append((param, param - lr * gradient / (T.sqrt(new_gsum + epsilon))))
    return updates


def adadelta(cost, params, rho=0.95, epsilon=1e-6):
    """
    Adadelta. Based on http://www.matthewzeiler.com/pubs/googleTR2012/googleTR2012.pdf
    """
    rho = theano.shared(np.float32(rho).astype(floatX))
    epsilon = theano.shared(np.float32(epsilon).astype(floatX))

    gradients = T.grad(cost, params)
    accu_gradients = [
        theano.shared(
            np.zeros_like(param.get_value(borrow=True)).astype(floatX)
        )
        for param in params
    ]
    accu_deltas = [
        theano.shared(
            np.zeros_like(param.get_value(borrow=True)).astype(floatX)
        )
        for param in params
    ]

    updates = []
    for param, gradient, accu_gradient, accu_delta in zip(params, gradients, accu_gradients, accu_deltas):
        new_accu_gradient = rho * accu_gradient + (1. - rho) * gradient ** 2.
        delta_x = - T.sqrt((accu_delta + epsilon) / (new_accu_gradient + epsilon)) * gradient
        new_accu_delta = rho * accu_delta + (1. - rho) * delta_x ** 2.
        updates.append((accu_gradient, new_accu_gradient))
        updates.append((accu_delta, new_accu_delta))
        updates.append((param, param + delta_x))
    return updates


def adam(cost, params, lr=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
    """
    Adam. Based on http://arxiv.org/pdf/1412.6980v4.pdf
    """
    updates = []
    gradients = T.grad(cost, params)

    t = theano.shared(np.float32(1.).astype(floatX))

    for param, gradient in zip(params, gradients):
        value = param.get_value(borrow=True)
        m_prev = theano.shared(np.zeros(value.shape, dtype=value.dtype),
                               broadcastable=param.broadcastable)
        v_prev = theano.shared(np.zeros(value.shape, dtype=value.dtype),
                               broadcastable=param.broadcastable)

        m = beta1 * m_prev + (1. - beta1) * gradient
        v = beta2 * v_prev + (1. - beta2) * gradient ** 2.
        m_hat = m / (1. - beta1 ** t)
        v_hat = v / (1. - beta2 ** t)
        theta = param - (lr * m_hat) / (T.sqrt(v_hat) + epsilon)

        updates.append((m_prev, m))
        updates.append((v_prev, v))
        updates.append((param, theta))

    updates.append((t, t + 1.))
    return updates
