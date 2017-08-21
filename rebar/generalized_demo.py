from __future__ import absolute_import
from __future__ import print_function
import matplotlib.pyplot as plt

import autograd.numpy as np
import autograd.numpy.random as npr
from autograd.scipy.special import expit, logit

from autograd import grad, value_and_grad
from autograd.optimizers import adam

from rebar import simple_mc_generalized_rebar, init_nn_params

if __name__ == '__main__':

    D = 100
    num_hidden_units = 100
    rs = npr.RandomState(0)
    num_samples = 50
    init_est_params = init_nn_params(0.1, [D, num_hidden_units, 1])
    init_combined_params = (np.zeros(D), init_est_params)

    def objective(params, b):
        return (b - np.linspace(0, 1, D))**2

    def mc_objective_and_var(combined_params, t):
        params, est_params = combined_params
        params_rep = np.tile(params, (num_samples, 1))
        rs = npr.RandomState(t)
        noise_u = rs.rand(num_samples, D)
        noise_v = rs.rand(num_samples, D)
        objective_vals, grads = \
            value_and_grad(simple_mc_generalized_rebar)(params_rep, est_params, noise_u, noise_v, objective)
        return np.mean(objective_vals), np.var(grads, axis=0)

    def combined_obj(combined_params, t):
        # Combines objective value and variance of gradients.
        # However, model_params shouldn't affect variance (in expectation),
        # and est_params shouldn't affect objective (in expectation).
        obj_value, grad_variances = mc_objective_and_var(combined_params, t)
        return obj_value + grad_variances

    # Set up figure.
    fig = plt.figure(figsize=(8, 8), facecolor='white')
    ax1 = fig.add_subplot(311, frameon=False)
    ax2 = fig.add_subplot(312, frameon=False)
    ax3 = fig.add_subplot(313, frameon=False)

    plt.ion()
    plt.show(block=False)

    def callback(combined_params, t, gradient):
        params, est_params = combined_params
        grad_params = gradient[:D]
        if t % 10 == 0:
            objective_val, grad_vars = mc_objective_and_var(combined_params, t)
            print("Iteration {} objective {}".format(t, objective_val))
            ax1.cla()
            ax1.plot(expit(params), 'r')
            ax1.set_ylabel('parameter values')
            ax1.set_ylim([0, 1])
            ax2.cla()
            ax2.plot(grad_params, 'g')
            ax2.set_ylabel('average gradient')
            ax3.cla()
            ax3.plot(grad_vars, 'b')
            ax3.set_ylabel('gradient variance')
            ax3.set_xlabel('parameter index')

            plt.draw()
            plt.pause(1.0/30.0)

    print("Optimizing...")
    adam(grad(combined_obj), init_combined_params, step_size=0.1, num_iters=2000, callback=callback)
    plt.pause(10.0)